import os
import logging
from typing import List, Dict, Any
import numpy as np
from sentence_transformers import SentenceTransformer
import umap
import hdbscan
from groq import Groq

from models import PlayStoreReview
from pii_scrubber import PIIScrubber

logger = logging.getLogger(__name__)

class AnalysisEngine:
    def __init__(self, embedding_model: str = 'all-MiniLM-L6-v2', groq_model: str = 'llama-3.3-70b-versatile'):
        self.encoder = SentenceTransformer(embedding_model)
        self.groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY", ""))
        self.groq_model = groq_model

    def process(self, reviews: List[PlayStoreReview]) -> Dict[str, Any]:
        if not reviews:
            return {}

        logger.info("Scrubbing PII from reviews...")
        for r in reviews:
            r.scrubbed_content = PIIScrubber.scrub(r.content)

        texts = [r.scrubbed_content for r in reviews if r.scrubbed_content]
        
        texts = self._translate_reviews(texts)
        
        logger.info(f"Generating embeddings for {len(texts)} reviews...")
        embeddings = self.encoder.encode(texts, show_progress_bar=False)

        logger.info("Clustering embeddings with UMAP + HDBSCAN...")
        # Reduce dimensionality
        reducer = umap.UMAP(n_neighbors=15, n_components=5, metric='cosine', random_state=42)
        reduced_embeddings = reducer.fit_transform(embeddings)

        # Cluster
        clusterer = hdbscan.HDBSCAN(min_cluster_size=5, metric='euclidean', cluster_selection_method='eom')
        cluster_labels = clusterer.fit_predict(reduced_embeddings)

        # Group reviews by cluster
        clusters = {}
        for idx, label in enumerate(cluster_labels):
            if label == -1:
                continue # Noise
            if label not in clusters:
                clusters[label] = []
            clusters[label].append(reviews[idx])

        logger.info(f"Found {len(clusters)} valid clusters.")

        # Analyze top clusters (e.g. largest 5)
        sorted_clusters = sorted(clusters.items(), key=lambda x: len(x[1]), reverse=True)
        top_clusters = sorted_clusters[:5]

        report_data = {
            "themes": [],
            "quotes": [],
            "actions": []
        }

        logger.info("Analyzing clusters with Groq LLM...")
        for label, cluster_reviews in top_clusters:
            sample_texts = [r.scrubbed_content for r in cluster_reviews[:30]] # Send up to 30 to LLM
            analysis = self._analyze_cluster_with_llm(sample_texts)
            
            report_data["themes"].append(analysis.get("theme", "Unknown Theme"))
            report_data["quotes"].extend(analysis.get("quotes", []))
            report_data["actions"].extend(analysis.get("actions", []))

        return report_data

    def _analyze_cluster_with_llm(self, texts: List[str]) -> Dict[str, Any]:
        prompt = (
            "You are a product analyst. Analyze the following app reviews. "
            "Identify the main theme, extract 1-2 verbatim quotes that best represent the theme, "
            "and suggest 1 actionable idea for the product team.\n\n"
            "Reviews:\n" + "\n".join(f"- {t}" for t in texts) + "\n\n"
            "Return exactly in this JSON format:\n"
            "{\n"
            '  "theme": "Brief theme name (e.g., App performance & bugs - Lag during trading)",\n'
            '  "quotes": ["Exact quote 1", "Exact quote 2"],\n'
            '  "actions": ["Actionable idea 1"]\n'
            "}"
        )

        max_retries = 3
        for attempt in range(max_retries):
            try:
                chat_completion = self.groq_client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model=self.groq_model,
                    response_format={"type": "json_object"},
                    temperature=0.2,
                )
                import json
                result = json.loads(chat_completion.choices[0].message.content)
                return result
            except Exception as e:
                if 'rate_limit_exceeded' in str(e).lower() or '429' in str(e) or 'rate limit' in str(e).lower():
                    if attempt < max_retries - 1:
                        logger.warning(f"Groq Rate limit hit during cluster analysis. Sleeping for 60 seconds... (Attempt {attempt+1}/{max_retries})")
                        import time
                        time.sleep(60)
                        continue
                logger.error(f"Error calling Groq API: {e}")
                return {"theme": "Error analyzing cluster", "quotes": [], "actions": []}
        return {"theme": "Error analyzing cluster", "quotes": [], "actions": []}

    def _translate_reviews(self, texts: List[str]) -> List[str]:
        if not os.environ.get("GROQ_API_KEY"):
            logger.warning("GROQ_API_KEY not set. Skipping translation step.")
            return texts
            
        translated_texts = []
        batch_size = 50
        logger.info(f"Translating {len(texts)} reviews in batches of {batch_size} using Groq...")
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i+batch_size]
            prompt = (
                "You are an expert translator. Translate the following user reviews into English. "
                "If a review is already in English, return it exactly as is. If it is in Hinglish (Romanized Hindi) or any other language, translate it to English. "
                "Output ONLY a JSON array of strings, where each string is the translated review, preserving the original order exactly.\n\n"
                "Reviews to translate:\n" + "\n".join(f"{idx+1}. {text}" for idx, text in enumerate(batch))
            )
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    chat_completion = self.groq_client.chat.completions.create(
                        messages=[{"role": "user", "content": prompt}],
                        model=self.groq_model,
                        temperature=0.0,
                    )
                    import json
                    response_content = chat_completion.choices[0].message.content.strip()
                    if response_content.startswith("```json"):
                        response_content = response_content[7:-3]
                    elif response_content.startswith("```"):
                        response_content = response_content[3:-3]
                    
                    batch_translations = json.loads(response_content.strip())
                    if len(batch_translations) == len(batch):
                        translated_texts.extend(batch_translations)
                    else:
                        logger.warning("Translation batch size mismatch. Falling back to original texts for this batch.")
                        translated_texts.extend(batch)
                    break
                except Exception as e:
                    if 'rate_limit_exceeded' in str(e).lower() or '429' in str(e) or 'rate limit' in str(e).lower():
                        if attempt < max_retries - 1:
                            logger.warning(f"Groq Rate limit hit during translation. Sleeping for 60 seconds... (Attempt {attempt+1}/{max_retries})")
                            import time
                            time.sleep(60)
                            continue
                    logger.error(f"Translation batch failed: {e}. Falling back to original texts.")
                    translated_texts.extend(batch)
                    break
                
        return translated_texts

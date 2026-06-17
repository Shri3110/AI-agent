import unittest
import numpy as np
from unittest.mock import patch, MagicMock
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from analyzer import AnalysisEngine
from models import PlayStoreReview
import datetime

class TestAnalyzerClustering(unittest.TestCase):
    @patch("analyzer.SentenceTransformer")
    @patch("analyzer.Groq")
    @patch("analyzer.PIIScrubber.scrub")
    def test_clustering_logic(self, mock_scrub, mock_groq, mock_transformer):
        # We want to test the clustering logic (UMAP + HDBSCAN) inside process()
        # Create a mock AnalysisEngine
        
        # Make the scrubber just return the original text
        mock_scrub.side_effect = lambda x: x
        
        # Mock the Groq client so translation just returns original text
        engine = AnalysisEngine()
        engine._translate_reviews = lambda texts: texts
        engine._analyze_cluster_with_llm = lambda texts: {
            "theme": "Test Theme",
            "quotes": ["Test quote"],
            "actions": ["Test action"]
        }

        # Create 10 dummy reviews (we need at least 5 for HDBSCAN min_cluster_size=5)
        # We will create two distinct clusters
        reviews = []
        for i in range(15):
            r = PlayStoreReview(
                review_id=str(i),
                user_name=f"User {i}",
                content=f"Bug report {i}" if i < 8 else f"Feature request {i}",
                score=1 if i < 8 else 5,
                thumbs_up_count=0,
                review_created_version="1.0",
                at=datetime.datetime.now(),
                reply_content=None,
                replied_at=None,
                app_version="1.0"
            )
            reviews.append(r)
            
        # Mock the embeddings to return distinct, highly separable vectors for the two clusters
        # 8 items of cluster A, 7 items of cluster B
        embeddings = np.array(
            [[1.0, 0.0, 0.0, 0.0, 0.0]] * 8 + 
            [[-1.0, 0.0, 0.0, 0.0, 0.0]] * 7
        )
        engine.encoder.encode.return_value = embeddings
        
        # Since HDBSCAN min_cluster_size=5, and we have sizes 8 and 7, we should get exactly 2 clusters
        # Wait, UMAP with n_neighbors=15 might fail if dataset size is 15. We should make it 20 items.
        reviews = []
        for i in range(20):
            r = PlayStoreReview(
                review_id=str(i),
                user_name=f"User {i}",
                content=f"Bug report {i}" if i < 10 else f"Feature request {i}",
                score=1 if i < 10 else 5,
                thumbs_up_count=0,
                review_created_version="1.0",
                at=datetime.datetime.now(),
                reply_content=None,
                replied_at=None,
                app_version="1.0"
            )
            reviews.append(r)
            
        embeddings = np.array(
            [[1.0, 0.0, 0.0, 0.0, 0.0]] * 10 + 
            [[-1.0, 0.0, 0.0, 0.0, 0.0]] * 10
        )
        engine.encoder.encode.return_value = embeddings
        
        report_data = engine.process(reviews)
        
        # We should have exactly 2 themes returned (one for each cluster)
        self.assertEqual(len(report_data["themes"]), 2)
        self.assertEqual(report_data["themes"][0], "Test Theme")

if __name__ == "__main__":
    unittest.main()

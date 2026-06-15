import logging
from typing import List
import emoji
from models import PlayStoreReview

logger = logging.getLogger(__name__)

class ReviewNormalizer:
    @staticmethod
    def normalize(reviews: List[PlayStoreReview]) -> List[PlayStoreReview]:
        """
        Normalizes the reviews by filtering out:
        1. Reviews with less than 8 words.
        2. Reviews that contain emojis.
        3. Reviews that are not in English.
        """
        valid_reviews = []
        
        for r in reviews:
            content = r.content.strip()
            
            # Rule 1: At least 8 words
            if len(content.split()) < 8:
                continue
                
            # Rule 2: No emojis
            if emoji.emoji_count(content) > 0:
                continue
                
            valid_reviews.append(r)
            
        logger.info(f"Normalization complete. Filtered down from {len(reviews)} to {len(valid_reviews)} valid reviews.")
        return valid_reviews

import logging
from datetime import datetime, timedelta
from typing import List

from google_play_scraper import Sort, reviews
from models import PlayStoreReview

logger = logging.getLogger(__name__)

class PlayStoreScraper:
    def __init__(self, app_id: str = "com.nextbillion.groww"):
        self.app_id = app_id

    def fetch_reviews(self, weeks_back: int = 8, max_results: int = 50000) -> List[PlayStoreReview]:
        """
        Fetches reviews from the Google Play Store for the given app,
        filtering for reviews created within the last `weeks_back` weeks.
        """
        cutoff_date = datetime.now() - timedelta(weeks=weeks_back)
        logger.info(f"Fetching reviews for {self.app_id} since {cutoff_date.date()}...")

        fetched_reviews: List[PlayStoreReview] = []
        continuation_token = None
        
        while len(fetched_reviews) < max_results:
            # Fetch a batch of reviews
            result, continuation_token = reviews(
                self.app_id,
                lang='en', 
                country='in', 
                sort=Sort.NEWEST,
                count=200, # Max per request
                continuation_token=continuation_token
            )
            
            if not result:
                break
                
            older_than_cutoff = False
            for raw_review in result:
                created_at = raw_review['at']
                
                # Check if we've passed our cutoff window
                if created_at < cutoff_date:
                    older_than_cutoff = True
                    break
                    
                parsed_review = PlayStoreReview(
                    content=raw_review['content'],
                    score=raw_review['score'],
                    thumbs_up_count=raw_review['thumbsUpCount'],
                    app_version=raw_review.get('reviewCreatedVersion'),
                    created_at=raw_review['at']
                )
                fetched_reviews.append(parsed_review)
                
            if older_than_cutoff or continuation_token is None:
                break

        logger.info(f"Successfully fetched {len(fetched_reviews)} reviews.")
        return fetched_reviews

if __name__ == "__main__":
    # Simple test
    logging.basicConfig(level=logging.INFO)
    scraper = PlayStoreScraper()
    # Test fetch a small window (e.g., 1 week)
    res = scraper.fetch_reviews(weeks_back=1, max_results=10)
    for r in res[:2]:
        print(f"[{r.score} star] {r.created_at.date()}: {r.content[:100]}...")

import unittest
from unittest.mock import patch, MagicMock
import datetime
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from scraper import PlayStoreScraper
from models import PlayStoreReview

class TestPlayStoreScraper(unittest.TestCase):
    @patch("scraper.reviews")
    def test_fetch_reviews(self, mock_reviews):
        # Mock the google-play-scraper response
        mock_response = [
            {
                "reviewId": "1",
                "userName": "Test User",
                "content": "Great app!",
                "score": 5,
                "thumbsUpCount": 10,
                "reviewCreatedVersion": "1.0",
                "at": datetime.datetime.now(),
                "replyContent": None,
                "repliedAt": None,
                "appVersion": "1.0"
            },
            {
                "reviewId": "2",
                "userName": "Another User",
                "content": "Too many bugs.",
                "score": 1,
                "thumbsUpCount": 0,
                "reviewCreatedVersion": "1.0",
                "at": datetime.datetime.now() - datetime.timedelta(days=10),
                "replyContent": None,
                "repliedAt": None,
                "appVersion": "1.0"
            }
        ]
        
        # The scraper makes multiple calls if token is returned. We'll return the mock list and a None token.
        mock_reviews.return_value = (mock_response, None)
        
        scraper = PlayStoreScraper()
        # Fetch for the last 1 week
        fetched = scraper.fetch_reviews(weeks_back=1)
        
        # Should only include the first review, as the second is 10 days old (outside of 1 week window)
        self.assertEqual(len(fetched), 1)
        self.assertEqual(fetched[0].review_id, "1")
        self.assertEqual(fetched[0].content, "Great app!")

if __name__ == "__main__":
    unittest.main()

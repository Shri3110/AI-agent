from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class PlayStoreReview(BaseModel):
    content: str = Field(..., description="The text content of the review")
    score: int = Field(..., ge=1, le=5, description="The star rating (1-5)")
    thumbs_up_count: int = Field(default=0, description="Number of upvotes on the review")
    app_version: Optional[str] = Field(None, description="App version at the time of review")
    created_at: datetime = Field(..., description="Timestamp when the review was created")

    # Field used internally after PII scrubbing
    scrubbed_content: Optional[str] = Field(None, description="Review content after PII removal")

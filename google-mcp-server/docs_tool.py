from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from auth import get_credentials
import logging

logger = logging.getLogger(__name__)

def append_to_doc(doc_id: str, content: str) -> dict:
    """
    Appends text to the end of a Google Document.
    """
    creds = get_credentials()
    try:
        service = build("docs", "v1", credentials=creds)

        # The request to insert text at the end of the document.
        # Index 1 is used if we want to append to the start.
        # But we want to append at the end, so we can fetch the doc first to get the end index,
        # or we can simply insert at the end of the document by not providing the index
        # Actually, Google Docs API requires an explicit index or endOfSegmentLocation.
        requests = [
            {
                "insertText": {
                    "endOfSegmentLocation": {
                        "segmentId": "" # empty string means body
                    },
                    "text": content + "\n"
                }
            }
        ]

        result = service.documents().batchUpdate(
            documentId=doc_id, body={"requests": requests}
        ).execute()

        logger.info(f"Successfully appended text to Doc ID: {doc_id}")
        return {
            "status": "success",
            "documentId": doc_id,
            "replies": result.get("replies")
        }

    except HttpError as error:
        logger.error(f"An error occurred: {error}")
        return {"status": "error", "message": str(error)}

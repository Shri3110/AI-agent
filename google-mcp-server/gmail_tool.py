import base64
from email.message import EmailMessage
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from auth import get_credentials
import logging

logger = logging.getLogger(__name__)

def create_email_draft(to_email: str, subject: str, body: str) -> dict:
    """
    Creates an email draft in Gmail.
    """
    creds = get_credentials()
    try:
        service = build("gmail", "v1", credentials=creds)

        message = EmailMessage()
        message.set_content(body, subtype="html") # Assuming HTML body
        message["To"] = to_email
        message["From"] = "me"
        message["Subject"] = subject

        # Encode the message in base64url format
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        create_message = {"message": {"raw": encoded_message}}
        
        # Call the Gmail API to create the draft
        draft = service.users().drafts().create(userId="me", body=create_message).execute()

        logger.info(f"Successfully created draft with ID: {draft['id']}")
        return {
            "status": "success",
            "draftId": draft["id"]
        }

    except Exception as error:
        import traceback
        error_msg = traceback.format_exc()
        logger.error(f"An error occurred: {error_msg}")
        return {"status": "error", "message": error_msg}

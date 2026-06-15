import logging
from mcp.server.fastmcp import FastMCP
from typing import List

logger = logging.getLogger(__name__)

# Create the FastMCP server for Gmail
mcp = FastMCP("Gmail Pulse Server")

@mcp.tool()
def send_pulse_teaser(to_emails: List[str], subject: str, body: str, draft_only: bool = True) -> str:
    """
    Creates a draft or sends an email teaser for the Weekly Pulse.
    
    Args:
        to_emails: List of email addresses to send the teaser to.
        subject: The subject line of the email.
        body: The HTML body of the email (including the deep link to the Doc).
        draft_only: If True, only creates a draft. If False, sends the email.
        
    Returns:
        The Message ID of the created draft or sent email.
    """
    action = "Drafting" if draft_only else "Sending"
    logger.info(f"{action} email to {to_emails} with subject '{subject}'...")
    
    # In a real implementation, we would:
    # 1. Authenticate with Gmail API
    # 2. Construct the MIME message
    # 3. Call users().messages().send() or users().drafts().create()
    
    # Mocking the success
    mock_message_id = "msg_mock_987654321"
    
    if draft_only:
        return f"Draft created successfully. ID: {mock_message_id}"
    else:
        return f"Email sent successfully. ID: {mock_message_id}"

if __name__ == "__main__":
    # Start the standard stdio server
    mcp.run()

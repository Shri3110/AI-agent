import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# If modifying these scopes, delete the file token.json.
SCOPES = [
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/gmail.compose"
]

TOKEN_PATH = os.environ.get("TOKEN_PATH", "token.json")
CREDENTIALS_PATH = os.environ.get("CREDENTIALS_PATH", "credentials.json")

def get_credentials():
    """Gets valid user credentials from storage or initiates OAuth2 flow."""
    import json
    
    # Auto-inject from Railway environment variables if files are missing
    if not os.path.exists(TOKEN_PATH) and "GOOGLE_TOKEN_JSON" in os.environ:
        with open(TOKEN_PATH, "w") as f:
            f.write(os.environ["GOOGLE_TOKEN_JSON"])
            
    if not os.path.exists(CREDENTIALS_PATH) and "GOOGLE_CREDENTIALS_JSON" in os.environ:
        with open(CREDENTIALS_PATH, "w") as f:
            f.write(os.environ["GOOGLE_CREDENTIALS_JSON"])

    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
        
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDENTIALS_PATH):
                raise FileNotFoundError(
                    f"{CREDENTIALS_PATH} not found. Please download OAuth 2.0 Client ID "
                    "credentials from Google Cloud Console and save it or configure the environment variable."
                )
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_PATH, SCOPES
            )
            # Run local server to authenticate
            creds = flow.run_local_server(port=0)
            
        # Save the credentials for the next run
        with open(TOKEN_PATH, "w") as token:
            token.write(creds.to_json())
            
    return creds

# Google MCP Server

A FastAPI-based local server that acts as an MCP-style tool provider for Google Docs and Gmail, requiring interactive terminal approval before executing any actions.

## Setup

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Google Cloud Setup**
   - Go to the [Google Cloud Console](https://console.cloud.google.com/).
   - Create a new project.
   - Enable the **Google Docs API** and **Gmail API**.
   - Configure the OAuth consent screen.
   - Create OAuth 2.0 Client ID credentials (Desktop Application).
   - Download the JSON file and save it as `credentials.json` in this directory.

3. **Run the Server**
   ```bash
   uvicorn server:app --reload
   ```
   *Note: On the first run or when an API call is made for the first time, it will open a browser window to authenticate with Google. A `token.json` file will be generated for subsequent runs.*

## Endpoints

### 1. Append to Google Doc
`POST /append_to_doc`

**Request Body:**
```json
{
  "doc_id": "YOUR_GOOGLE_DOC_ID",
  "content": "Text to append"
}
```

### 2. Create Email Draft
`POST /create_email_draft`

**Request Body:**
```json
{
  "to_email": "example@example.com",
  "subject": "Test Subject",
  "body": "<h1>Hello</h1><p>This is a test draft.</p>"
}
```

## Approval Mechanism
Before any endpoint executes the Google API call, the terminal running the `uvicorn` server will print the action and payload, and prompt:
`Approve? (y/n):`

The API request will hang until you type `y` or `n` in the terminal. If you type `n`, the API will return a 403 Forbidden error.

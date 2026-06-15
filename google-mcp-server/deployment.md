# Railway Deployment Guide

The `google-mcp-server` has been successfully updated with production-ready configurations for Railway deployment.

## What Was Changed

1. **Procfile Added**: The app will now boot dynamically and bind to `0.0.0.0:$PORT` using standard buildpack processes.
2. **API Key Security**: If you set the `API_KEY` environment variable in Railway, the server will bypass the interactive terminal prompt and automatically approve requests that provide a valid `x-api-key` header. If the variable is not set, it falls back to the local terminal prompt.
3. **Railway Volumes Support**: The authentication paths can now be overridden via environment variables `TOKEN_PATH` and `CREDENTIALS_PATH` to support persistent file systems.

## How to Deploy to Railway

### Step 1: Push to GitHub
Commit your `google-mcp-server` directory (minus the `.gitignore` files like `token.json` and `credentials.json`) and push it to a new GitHub repository.

### Step 2: Create Railway Service
1. Go to your [Railway Dashboard](https://railway.app/).
2. Click **New Project** > **Deploy from GitHub repo**.
3. Select the repository containing your server code.

### Step 3: Configure Storage (Railway Volumes)
Because `token.json` is constantly overwritten when the access token refreshes, you need a persistent file system.
1. In your Railway service settings, navigate to the **Volumes** tab.
2. Add a new Volume and mount it at the path: `/data`.

### Step 4: Environment Variables
Go to the **Variables** tab in Railway and add the following:
- `API_KEY`: A strong, secret password (e.g., `super-secret-key-123`).
- `TOKEN_PATH`: `/data/token.json`
- `CREDENTIALS_PATH`: `/data/credentials.json`

### Step 5: Upload Secrets via Railway CLI
Since your secrets are git-ignored, you need to manually upload them to the Railway volume.
1. Install the Railway CLI: `npm i -g @railway/cli`.
2. Login to your account: `railway login`.
3. Link to your project: `railway link`.
4. Upload the files into the volume you created:
   ```bash
   railway run cp credentials.json /data/credentials.json
   railway run cp token.json /data/token.json
   ```

### Step 6: Update the Main App
When calling the MCP server from your main `weekly_pulse` app, make sure to add the API key header to your HTTP requests:
```python
headers = {"x-api-key": "super-secret-key-123"}
```

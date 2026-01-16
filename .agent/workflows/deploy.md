---
description: Deploy LINE Bot to Railway.app with Firebase
---

# Deploy to Railway

This workflow guides you through deploying the LINE Bot garbage duty rotation system to Railway.app.

## Prerequisites

- GitHub repository with the project code
- Railway.app account
- LINE Developers account
- Firebase project with Firestore enabled

## Steps

### 1. Prepare Project Files

Ensure the following files exist in your repository:

**Procfile:**
```
web: python main.py
```

**requirements.txt:**
Verify all dependencies are listed:
```
Flask==3.0.0
line-bot-sdk==3.5.0
python-dotenv==1.0.0
APScheduler==3.10.4
pytz==2023.3
firebase-admin==6.2.0
requests==2.31.0
```

**main.py:**
Check that the entry point uses Railway's PORT:
```python
if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
```

### 2. Create Railway Project

// turbo
1. Go to [railway.app](https://railway.app)
2. Click "New Project"
3. Choose "Deploy from GitHub repo"
4. Select your repository
5. Wait for Railway to detect it as a Python app

### 3. Configure Environment Variables

In Railway dashboard → Variables tab, add:

**LINE_CHANNEL_ACCESS_TOKEN:**
- Go to LINE Developers Console
- Select your Messaging API channel
- Copy the Channel access token
- Paste in Railway

**LINE_CHANNEL_SECRET:**
- In LINE Developers Console
- Copy the Channel secret
- Paste in Railway

**FIREBASE_CONFIG_JSON:**
- Go to Firebase Console → Project Settings → Service Accounts
- Click "Generate new private key"
- Download JSON file
- Copy the ENTIRE JSON content (as one line)
- Paste in Railway

### 4. Deploy

// turbo
Railway will automatically deploy after adding environment variables.

Check deployment status:
1. Go to "Deployments" tab
2. Wait for "Success" status
3. Click deployment to view logs

### 5. Get Public URL

// turbo
1. Go to "Settings" tab
2. Under "Domains", click "Generate Domain"
3. Copy the generated URL (e.g., `https://your-app.up.railway.app`)

### 6. Configure LINE Webhook

1. Go to LINE Developers Console
2. Select your Messaging API channel
3. Go to "Messaging API" tab
4. Set Webhook URL: `https://your-app.up.railway.app/callback`
5. Enable "Use webhook"
6. Click "Verify" (should show success)

### 7. Verify Deployment

Test the health endpoint:
// turbo
```bash
curl https://your-app.up.railway.app/
```

Should return: `🗑️ LINE Bot is running!`

Check Railway logs:
1. Go to "Deployments" tab
2. Click latest deployment
3. Click "View Logs"
4. Verify you see:
   - `✅ Firebase 可用`
   - `ACCESS_TOKEN: ...`
   - `Running on http://0.0.0.0:5000`

### 8. Test in LINE

1. Add the bot to a LINE group
2. Send `@help` in the group
3. Bot should respond with help menu

## Verification

- [ ] Railway deployment shows "Success"
- [ ] Health endpoint returns 200 OK
- [ ] Logs show Firebase connected
- [ ] LINE webhook verification passes
- [ ] Bot responds to `@help` in group

## Troubleshooting

**Deployment Failed:**
- Check logs for Python errors
- Verify `Procfile` exists and is correct
- Ensure all dependencies in `requirements.txt`

**Webhook 400 Error:**
- Verify `LINE_CHANNEL_SECRET` is correct
- Check webhook URL has `/callback` endpoint

**Firebase Connection Failed:**
- Verify `FIREBASE_CONFIG_JSON` is complete
- Check Firebase project is active
- Ensure service account has permissions

**No Scheduled Reminders:**
- Railway free tier sleeps after inactivity
- Consider upgrading to Hobby plan ($5/month)

## Next Steps

- Run `/setup-line-bot` to configure LINE settings
- Run `/test-debug` to verify all features

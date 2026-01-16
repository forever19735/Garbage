---
name: Railway Deployment
description: Deploy Python Flask applications to Railway.app with environment configuration and webhook setup
---

## When to use this skill

Deploy Flask LINE bots to Railway.app, configure environment variables, set up webhooks, and monitor deployments.

## How to use it

### Required Files

**Procfile:**
```
web: python main.py
```

**requirements.txt:**
```
Flask==3.0.0
line-bot-sdk==3.5.0
APScheduler==3.10.4
firebase-admin==6.2.0
```

**main.py entry point:**
```python
if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
```

### Environment Variables

Set in Railway dashboard:
- `LINE_CHANNEL_ACCESS_TOKEN` - LINE Bot token
- `LINE_CHANNEL_SECRET` - Channel secret
- `FIREBASE_CONFIG_JSON` - Complete Firebase JSON

### Deployment Steps

1. Connect GitHub repo to Railway
2. Set environment variables
3. Get generated domain URL
4. Configure LINE webhook: `https://your-app.up.railway.app/callback`

### Monitoring

Add health check:
```python
@app.route("/", methods=['GET'])
def health_check():
    return "Bot is running!", 200
```

View logs in Railway dashboard → Deployments → View Logs

### Common Issues

- **Crashed**: Check `Procfile` and `PORT` usage
- **Webhook 400**: Verify `LINE_CHANNEL_SECRET`
- **Firebase failed**: Check JSON format in env var
- **No scheduled jobs**: Upgrade to Hobby plan ($5/mo)

### Links

- [Railway Docs](https://docs.railway.app/)
- [LINE Developers](https://developers.line.biz/)

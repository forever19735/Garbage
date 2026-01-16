---
description: Configure LINE Developers Console for Messaging API
---

# Setup LINE Bot

This workflow guides you through setting up a LINE Bot in the LINE Developers Console.

## Prerequisites

- LINE account (personal or business)
- Access to LINE Developers Console

## Steps

### 1. Create Provider (if needed)

1. Go to [LINE Developers Console](https://developers.line.biz/)
2. Click "Create Provider"
3. Enter provider name (e.g., "My Company")
4. Click "Create"

### 2. Create Messaging API Channel

1. In your provider, click "Create a new channel"
2. Select "Messaging API"
3. Fill in channel information:
   - **Channel name**: e.g., "垃圾輪值提醒 Bot"
   - **Channel description**: e.g., "自動輪值提醒系統"
   - **Category**: Choose "Productivity"
   - **Subcategory**: Choose appropriate option
4. Read and agree to terms
5. Click "Create"

### 3. Configure Basic Settings

In the channel settings:

1. **Channel icon** (optional):
   - Upload a 512x512 icon image
   - Consider using 🗑️ emoji theme

2. **Channel description**:
   - Add detailed description for users

3. **Privacy policy URL** (optional):
   - Add if you have one

4. **Terms of use URL** (optional):
   - Add if you have one

### 4. Configure Messaging API

Go to "Messaging API" tab:

1. **Bot basic ID**:
   - Note your bot's ID for reference

2. **QR code**:
   - Download for easy bot access

3. **Webhook settings**:
   - Enable "Use webhook"
   - Set webhook URL (from Railway): `https://your-app.up.railway.app/callback`
   - Click "Verify" to test (do this AFTER deploying to Railway)

4. **Auto-reply messages**:
   - **Disable** "Auto-reply messages" (we handle this in code)
   - **Disable** "Greeting messages" (optional)

5. **Response mode**:
   - Select "Bot" (not "Chat")

### 5. Get Credentials

**Channel Access Token:**
1. Scroll to "Channel access token" section
2. Click "Issue" button
3. Copy the long token
4. Save as `LINE_CHANNEL_ACCESS_TOKEN` in Railway

**Channel Secret:**
1. Go to "Basic settings" tab
2. Find "Channel secret"
3. Click "Show" and copy
4. Save as `LINE_CHANNEL_SECRET` in Railway

### 6. Configure Features (Optional)

**Scan QR Code Join:**
1. Go to "Messaging API" tab
2. Enable "Allow bot to join group chats"
3. Enable "Scan QR code" feature

**Rich Menu** (Optional):
1. Create rich menu for better UX
2. Add quick action buttons:
   - "查看排程" → sends `@schedule`
   - "查看成員" → sends `@members`
   - "幫助" → sends `@help`

### 7. Add Bot to Test Group

1. Create a LINE group for testing
2. Use QR code or bot ID to add bot
3. Bot should send join message (if implemented)

### 8. Verify Configuration

Test basic functionality:

1. Send `@help` in group
2. Verify bot responds with help menu
3. Try `@schedule` command
4. Check Railway logs for activity

## Verification Checklist

- [ ] Messaging API channel created
- [ ] Webhook URL configured and verified
- [ ] Auto-reply messages disabled
- [ ] Channel access token issued and saved
- [ ] Channel secret copied and saved
- [ ] Bot added to test group
- [ ] Bot responds to `@help`

## Important Notes

**Free Plan Limitations:**
- LINE Messaging API has message quotas on free plan
- Monitor usage in console

**Webhook URL:**
- Must be HTTPS (Railway provides this)
- Must be publicly accessible
- Should return 200 OK

**Security:**
- Keep Channel Secret private
- Never commit credentials to Git
- Use environment variables

## Next Steps

- Run `/deploy` if you haven't deployed to Railway
- Run `/setup-firebase` to configure database
- Run `/test-debug` to verify all features

## Troubleshooting

**Webhook Verification Failed:**
- Ensure Railway app is deployed and running
- Check webhook URL is correct with `/callback`
- Verify `LINE_CHANNEL_SECRET` in Railway matches

**Bot Not Responding:**
- Check Railway logs for errors
- Verify webhook is enabled
- Ensure auto-reply is disabled
- Check response mode is "Bot"

**Cannot Add Bot to Group:**
- Enable "Allow bot to join group chats"
- Check bot is not blocked

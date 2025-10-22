# Deploy TaxGuard WhatsApp Bot to Render (Cloud API)

This guide covers deploying the TaxGuard WhatsApp bot using **Meta's WhatsApp Cloud API** (free tier) instead of Twilio.

## Prerequisites
- GitHub account
- Render account (sign up at https://render.com)
- Meta (Facebook) Business account
- WhatsApp Cloud API access
- Gemini API key or OpenAI API key

## Step 1: Set Up WhatsApp Cloud API

### 1.1 Create Meta Business Account
1. Go to https://business.facebook.com
2. Create a business account
3. Go to Meta for Developers: https://developers.facebook.com

### 1.2 Create WhatsApp App
1. Go to **My Apps** → **Create App**
2. Select **Business** as app type
3. Fill in app details:
   - **App Name**: TaxGuard WhatsApp Bot
   - **Business Account**: Select your business
4. Click **Create App**

### 1.3 Add WhatsApp Product
1. In your app dashboard, find **WhatsApp** product
2. Click **Set up**
3. Select your business portfolio

### 1.4 Get Your Credentials
1. Navigate to **WhatsApp** → **API Setup**
2. Copy the following:
   - **Temporary Access Token** (valid 24h - you'll generate permanent one later)
   - **Phone Number ID** (under "From" section)
   - **WhatsApp Business Account ID**

### 1.5 Generate Permanent Access Token
1. Go to **System Users** in Business Settings
2. Create a system user (e.g., "TaxGuard Bot")
3. Assign **WhatsApp Business Management** permission
4. Generate permanent token
5. Save this token securely

### 1.6 Add Test Phone Number
1. In **API Setup**, add your phone number to test
2. You'll receive a verification code via WhatsApp
3. Verify your number

## Step 2: Prepare Your Repository

### 2.1 Initialize Git (if not already done)
```bash
cd /Users/app/Documents/projects/python/taxguard-demo
git init
git add .
git commit -m "Initial commit: TaxGuard WhatsApp Bot with Cloud API"
```

### 2.2 Push to GitHub
```bash
# Create a new repository on GitHub first, then:
git remote add origin https://github.com/YOUR_USERNAME/taxguard-demo.git
git branch -M main
git push -u origin main
```

## Step 3: Deploy to Render

### Option A: Using render.yaml (Blueprint - Recommended)

1. **Go to Render Dashboard**: https://dashboard.render.com
2. Click **"New +"** → **"Blueprint"**
3. Connect your GitHub repository
4. Render will detect `render.yaml` in `module2-whatsapp-bot/`
5. Click **"Apply"**

### Option B: Manual Setup

1. **Go to Render Dashboard**: https://dashboard.render.com
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Configure:
   - **Name**: `taxguard-whatsapp-bot`
   - **Root Directory**: `module2-whatsapp-bot`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements_cloud_api.txt`
   - **Start Command**: `gunicorn app_cloud_api:app --bind 0.0.0.0:$PORT`
   - **Plan**: `Free`

## Step 4: Configure Environment Variables

In Render Dashboard → Your Service → **Environment**:

Add these variables:

| Key | Value | Required | Where to Get |
|-----|-------|----------|--------------|
| `META_ACCESS_TOKEN` | Your permanent access token | ✅ Yes | Meta Business Settings → System Users |
| `META_PHONE_NUMBER_ID` | Your phone number ID | ✅ Yes | WhatsApp → API Setup → Phone Number ID |
| `META_WEBHOOK_VERIFY_TOKEN` | Your custom secret (e.g., `taxguard_secret_123`) | ✅ Yes | Create your own secure random string |
| `GEMINI_API_KEY` | Your Gemini API key | ⚠️ One required | Google AI Studio |
| `OPENAI_API_KEY` | Your OpenAI API key | ⚠️ One required | OpenAI Dashboard |

**Notes**:
- You need either `GEMINI_API_KEY` OR `OPENAI_API_KEY` (not both required)
- `META_WEBHOOK_VERIFY_TOKEN` is a secret you create yourself (save it for webhook setup)

## Step 5: Deploy and Get URL

1. Click **"Create Web Service"** or **"Apply"**
2. Wait for deployment (2-5 minutes)
3. Once deployed, copy your URL: `https://taxguard-whatsapp-bot.onrender.com`

## Step 6: Configure Meta Webhook

### 6.1 Set Up Webhook in Meta
1. Go to Meta for Developers → Your App → **WhatsApp** → **Configuration**
2. Under **Webhook**, click **Edit**
3. Enter:
   - **Callback URL**: `https://taxguard-whatsapp-bot.onrender.com/webhook`
   - **Verify Token**: The same value you used for `META_WEBHOOK_VERIFY_TOKEN`
4. Click **Verify and Save**

### 6.2 Subscribe to Webhook Events
1. In **Webhook Fields**, subscribe to:
   - ✅ `messages` (required - to receive messages)
2. Click **Save**

## Step 7: Test Your Bot

1. Send a test message to your WhatsApp Business number:
   ```
   start
   ```
2. You should receive the welcome message
3. Try asking:
   - "Mera tax calculate karo"
   - "How do I file tax return?"

## Step 8: Customize Business Profile (Optional but Recommended)

1. Go to **Meta Business Manager** → **WhatsApp Manager**
2. Select your phone number
3. Customize:
   - **Business Name**: TaxGuard AI
   - **Profile Picture**: Upload your logo
   - **About**: Pakistan's intelligent tax assistant
   - **Business Category**: Financial Services
   - **Website**: Your website URL

## Keeping Your Server Awake (24/7 Uptime)

Render's free tier sleeps after 15 minutes of inactivity. Keep it awake:

### Option 1: UptimeRobot (Recommended - Free)

1. Sign up at https://uptimerobot.com
2. Create new monitor:
   - **Monitor Type**: HTTP(s)
   - **URL**: `https://taxguard-whatsapp-bot.onrender.com/health`
   - **Monitoring Interval**: 5 minutes
3. Save - bot stays awake 24/7!

### Option 2: Cron-job.org

1. Sign up at https://cron-job.org
2. Create cron job:
   - **URL**: `https://taxguard-whatsapp-bot.onrender.com/health`
   - **Schedule**: Every 5 minutes

### Option 3: GitHub Actions

Create `.github/workflows/keep-alive.yml`:

```yaml
name: Keep Render Alive
on:
  schedule:
    - cron: '*/10 * * * *'  # Every 10 minutes
  workflow_dispatch:

jobs:
  keep-alive:
    runs-on: ubuntu-latest
    steps:
      - name: Ping Render
        run: curl https://taxguard-whatsapp-bot.onrender.com/health
```

## Monitoring & Debugging

### Check Health Status
Visit: `https://YOUR_APP.onrender.com/health`

Should return:
```json
{
  "status": "healthy",
  "service": "TaxGuard AI WhatsApp Bot (Cloud API)",
  "ai_provider": "gemini",
  "meta_configured": true
}
```

### View Logs
- **Render Dashboard** → Your Service → **Logs**
- Look for:
  - `🤖 Using Google Gemini API` or `🤖 Using OpenAI API`
  - `✅ WhatsApp Cloud API configured`
  - `📩 Received from ...` (incoming messages)
  - `📤 Sent response: ...` (outgoing messages)

### Common Errors

| Error | Solution |
|-------|----------|
| "Webhook verification failed" | Check `META_WEBHOOK_VERIFY_TOKEN` matches in Render env vars and Meta webhook config |
| "AI service not configured" | Verify `GEMINI_API_KEY` or `OPENAI_API_KEY` is set |
| "WhatsApp Cloud API credentials not configured" | Check `META_ACCESS_TOKEN` and `META_PHONE_NUMBER_ID` are set |
| 502 Bad Gateway | Check Render logs, app might be starting up (wait 30 seconds) |

## Troubleshooting

### Bot not responding to messages

1. **Check webhook subscription**:
   - Go to Meta → WhatsApp → Configuration → Webhook
   - Ensure `messages` field is subscribed

2. **Verify webhook is receiving data**:
   - Send a message
   - Check Render logs for `📥 Webhook data: ...`
   - If no logs, webhook isn't configured correctly

3. **Check Render logs** for errors:
   - `❌ Error processing message: ...`
   - `❌ Exception while sending message: ...`

### Webhook verification failing

- Ensure `META_WEBHOOK_VERIFY_TOKEN` in Render matches the token in Meta webhook config
- Check Render logs: `✅ Webhook verified successfully!` or `❌ Webhook verification failed!`

### Access token expired

- Temporary tokens expire in 24 hours
- Generate a **permanent token** from System Users in Business Settings

## Costs & Limits

| Service | Free Tier | Cost |
|---------|-----------|------|
| **Render** | 750 hours/month | Free (1 app 24/7) |
| **WhatsApp Cloud API** | 1,000 conversations/month | Free, then $0.005-0.03/conversation |
| **Gemini API** | 15 requests/minute | Free tier available |
| **OpenAI API** | Pay-as-you-go | ~$0.01-0.03 per 1000 tokens |

**Note**: WhatsApp defines a "conversation" as a 24-hour window with a user.

## Updating Your Deployment

Every push to GitHub `main` branch triggers auto-redeploy:

```bash
git add .
git commit -m "Update bot features"
git push origin main
```

## Going to Production

### 1. Verify Your Business Account
- Submit business verification to Meta
- Usually takes 1-3 business days

### 2. Get Phone Number Approved
- Request official WhatsApp number
- Or use your own business phone number

### 3. Increase Rate Limits
- Default: 1,000 conversations/month
- After verification: 10,000+/month
- Apply for higher limits in Meta Business Manager

### 4. Add Multiple Languages
- Enhance Urdu language support
- Add more regional languages

### 5. Add Advanced Features
- Image processing (receipts, documents)
- Document uploads
- Interactive buttons & templates
- Payment integration

## Security Best Practices

1. **Never commit `.env` file** - already in `.gitignore`
2. **Use permanent access tokens** - not temporary 24h tokens
3. **Secure webhook verify token** - use strong random string
4. **Enable HTTPS only** - Render provides this automatically
5. **Monitor API usage** - Check Meta and AI API dashboards regularly

## Support & Resources

- **Render Docs**: https://render.com/docs
- **WhatsApp Cloud API Docs**: https://developers.facebook.com/docs/whatsapp/cloud-api
- **Gemini API**: https://ai.google.dev/docs
- **OpenAI API**: https://platform.openai.com/docs

## Next Steps

- ✅ Deploy to Render
- ✅ Configure WhatsApp Cloud API webhook
- ✅ Set up UptimeRobot for 24/7 uptime
- ✅ Customize business profile
- Test with real users
- Monitor conversations and costs
- Apply for business verification
- Add advanced features

---

**Developed for**: AI Wrapper Competition 2025 - Ignite Pakistan
**Free Tier**: Yes - 1000 conversations/month with WhatsApp Cloud API

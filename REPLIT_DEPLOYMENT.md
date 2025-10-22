# Deploy TaxGuard WhatsApp Bot on Replit

Complete guide for deploying your WhatsApp bot using **Meta's WhatsApp Cloud API** on **Replit** (100% free).

## Prerequisites
- Replit account (sign up at https://replit.com)
- GitHub account
- Meta (Facebook) Business account
- WhatsApp Cloud API access
- Gemini API key or OpenAI API key

---

## Part 1: Set Up WhatsApp Cloud API

### Step 1: Create Meta Business Account
1. Go to https://business.facebook.com
2. Create a business account (or use existing)
3. Go to Meta for Developers: https://developers.facebook.com

### Step 2: Create WhatsApp App
1. Go to **My Apps** → **Create App**
2. Select **Business** as app type
3. Fill in details:
   - **App Name**: TaxGuard WhatsApp Bot
   - **Business Account**: Select your business
4. Click **Create App**

### Step 3: Add WhatsApp Product
1. In app dashboard, find **WhatsApp** product
2. Click **Set up**
3. Select your business portfolio

### Step 4: Get Your Credentials

**Important - Save these values:**

1. Navigate to **WhatsApp** → **API Setup**
2. Copy:
   - **Temporary Access Token** (24h validity)
   - **Phone Number ID** (under "From" section)
   - **WhatsApp Business Account ID**

### Step 5: Generate Permanent Access Token

1. Go to **Business Settings** → **System Users**
2. Click **Add** → Create system user (e.g., "TaxGuard Bot")
3. Assign **WhatsApp Business Management** permission
4. Click **Generate New Token**
5. Select your app and permissions:
   - ✅ `whatsapp_business_management`
   - ✅ `whatsapp_business_messaging`
6. Copy and save this permanent token securely

### Step 6: Add Test Phone Number
1. In **API Setup**, click **"Add phone number"**
2. Enter your phone number with country code
3. You'll receive verification code via WhatsApp
4. Enter code to verify

---

## Part 2: Deploy on Replit

### Step 1: Import from GitHub

1. Go to https://replit.com
2. Sign in or create account
3. Click **"+ Create Repl"**
4. Select **"Import from GitHub"**
5. Enter your repository URL:
   ```
   https://github.com/sajidali12/taxguard-whatsapp
   ```
6. Click **"Import from GitHub"**

### Step 2: Configure Secrets (Environment Variables)

1. In your Repl, click **"Tools"** (on left sidebar)
2. Click **"Secrets"** (lock icon)
3. Add these secrets:

| Key | Value | Where to Get |
|-----|-------|--------------|
| `META_ACCESS_TOKEN` | Your permanent access token | Meta Business Settings → System Users |
| `META_PHONE_NUMBER_ID` | Your phone number ID | WhatsApp → API Setup |
| `META_WEBHOOK_VERIFY_TOKEN` | Create your own (e.g., `taxguard_secret_2025`) | Any secure random string |
| `GEMINI_API_KEY` | Your Gemini API key | https://aistudio.google.com/apikey |

**Note**: You need either `GEMINI_API_KEY` OR `OPENAI_API_KEY` (add one, not both required)

### Step 3: Install Dependencies

1. In Replit Shell (bottom panel), run:
```bash
pip install -r requirements_cloud_api.txt
```

Or Replit will automatically install when you run the app.

### Step 4: Run Your Bot

1. Click the **"Run"** button at the top
2. Wait for app to start
3. You'll see output like:
```
🚀 TaxGuard AI WhatsApp Bot (Cloud API) starting on port 5000...
📱 Webhook endpoint: http://localhost:5000/webhook
🤖 AI Provider: GEMINI
✅ WhatsApp Cloud API configured
```

### Step 5: Get Your Replit URL

1. After running, you'll get a URL in the **Webview** panel
2. It looks like: `https://taxguard-whatsapp.YOUR_USERNAME.repl.co`
3. Copy this URL - you'll need it for webhook setup

**Important**: Keep the Repl running (don't stop it)

---

## Part 3: Configure Meta Webhook

### Step 1: Set Webhook URL in Meta

1. Go to Meta for Developers → Your App
2. Navigate to **WhatsApp** → **Configuration**
3. Under **Webhook**, click **Edit**
4. Enter:
   - **Callback URL**: `https://taxguard-whatsapp.YOUR_USERNAME.repl.co/webhook`
   - **Verify Token**: Same value as `META_WEBHOOK_VERIFY_TOKEN` secret
5. Click **"Verify and Save"**

You should see: ✅ "Webhook verified successfully!"

### Step 2: Subscribe to Webhook Events

1. In **Webhook Fields**, click **Manage**
2. Subscribe to:
   - ✅ `messages` (required)
3. Click **Save**

---

## Part 4: Test Your Bot

### Send Test Message

1. Open WhatsApp on your phone
2. Send message to your WhatsApp Business number
3. Type: `start`
4. You should receive the welcome message!

### Try These Commands:
- "Mera tax calculate karo"
- "How do I file tax return?"
- "What deductions can I claim?"

### Check Logs in Replit

In the Console (bottom panel), you'll see:
```
📩 Received from +923XXXXXXXXX: start
📤 Sent response: 🇵🇰 *TaxGuard AI - خوش آمدید*...
```

---

## Part 5: Keep Your Repl Always Running

Replit free tier sleeps after inactivity. Here are solutions:

### Option 1: UptimeRobot (Recommended - Free)

1. Sign up at https://uptimerobot.com
2. Create new monitor:
   - **Monitor Type**: HTTP(s)
   - **URL**: `https://taxguard-whatsapp.YOUR_USERNAME.repl.co/health`
   - **Monitoring Interval**: 5 minutes
3. Save

Your bot will now stay awake 24/7!

### Option 2: Replit Always On (Paid)

- Replit offers "Always On" feature for ~$7/month
- Guaranteed uptime without external services

### Option 3: Cron-job.org

1. Sign up at https://cron-job.org
2. Create cron job:
   - **URL**: `https://taxguard-whatsapp.YOUR_USERNAME.repl.co/health`
   - **Execution**: Every 5 minutes

---

## Monitoring & Debugging

### Check Health Status

Visit: `https://taxguard-whatsapp.YOUR_USERNAME.repl.co/health`

Expected response:
```json
{
  "status": "healthy",
  "service": "TaxGuard AI WhatsApp Bot (Cloud API)",
  "ai_provider": "gemini",
  "meta_configured": true
}
```

### View Logs in Replit

- Check the **Console** panel at bottom
- Look for:
  - `📩 Received from ...` (incoming messages)
  - `📤 Sent response: ...` (outgoing messages)
  - Error messages if any

### Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| **"Webhook verification failed"** | Verify `META_WEBHOOK_VERIFY_TOKEN` in Secrets matches Meta webhook config |
| **"AI service not configured"** | Add `GEMINI_API_KEY` in Replit Secrets |
| **"WhatsApp Cloud API credentials not configured"** | Add `META_ACCESS_TOKEN` and `META_PHONE_NUMBER_ID` in Secrets |
| **Bot not responding** | Check webhook is subscribed to `messages` field in Meta |
| **Repl keeps sleeping** | Set up UptimeRobot to ping `/health` every 5 minutes |

---

## Customizing Your Bot

### Update Business Profile

1. Go to **Meta Business Manager** → **WhatsApp Manager**
2. Select your phone number
3. Customize:
   - **Display Name**: TaxGuard AI
   - **Profile Picture**: Upload logo
   - **About**: Pakistan's intelligent tax assistant
   - **Category**: Financial Services

### Update Bot Responses

Edit `app_cloud_api.py` in Replit:
- Modify `SYSTEM_PROMPT` for AI behavior
- Update welcome message
- Add new command handlers

After editing, click **"Run"** again to restart.

---

## Updating Your Bot

### Method 1: Edit Directly in Replit
1. Make changes to code in Replit editor
2. Click **"Run"** to restart
3. Changes are live immediately

### Method 2: Push from GitHub
1. Make changes locally
2. Push to GitHub:
```bash
git add .
git commit -m "Update bot"
git push origin main
```
3. In Replit, click **"Version control"** → **"Pull"**
4. Click **"Run"** to restart

---

## Costs & Limits

| Service | Free Tier | Notes |
|---------|-----------|-------|
| **Replit** | Free (with sleep) | Keeps awake with UptimeRobot |
| **WhatsApp Cloud API** | 1,000 conversations/month | Free tier forever |
| **Gemini API** | 15 requests/minute | Generous free tier |
| **UptimeRobot** | 50 monitors | 100% free |

**Total Monthly Cost**: $0 for up to 1,000 conversations 🎉

---

## Going to Production

### 1. Verify Business Account
- Submit business verification in Meta Business Manager
- Takes 1-3 business days
- Required for official phone number

### 2. Get Official Phone Number
- Request WhatsApp Business phone number
- Or migrate existing business number

### 3. Increase Rate Limits
- Default: 1,000 conversations/month
- After verification: 10,000+ conversations/month
- Apply in Meta Business Settings

### 4. Consider Replit Hacker Plan
- $7/month for "Always On" feature
- Better than UptimeRobot pinging
- Guaranteed uptime

---

## Security Best Practices

1. ✅ Never commit `.env` file (already in `.gitignore`)
2. ✅ Use **Secrets** in Replit for all API keys
3. ✅ Use **permanent access token** (not 24h temporary)
4. ✅ Create strong `META_WEBHOOK_VERIFY_TOKEN`
5. ✅ Monitor API usage regularly
6. ✅ Enable 2FA on Meta and Replit accounts

---

## Troubleshooting Checklist

Before asking for help, verify:

- [ ] All Secrets are added in Replit
- [ ] Repl is running (green play button)
- [ ] Webhook URL is correct in Meta
- [ ] Webhook verify token matches
- [ ] `messages` field is subscribed in webhook
- [ ] Phone number is verified in Meta
- [ ] Access token is permanent (not temporary)
- [ ] UptimeRobot is pinging `/health`

---

## Support & Resources

- **Replit Docs**: https://docs.replit.com
- **WhatsApp Cloud API**: https://developers.facebook.com/docs/whatsapp/cloud-api
- **Gemini API**: https://ai.google.dev/docs
- **Meta Business Help**: https://business.facebook.com/help

---

## Quick Start Summary

1. ✅ Create Meta Business account & WhatsApp app
2. ✅ Get permanent access token & phone number ID
3. ✅ Import GitHub repo to Replit
4. ✅ Add Secrets in Replit
5. ✅ Run the bot
6. ✅ Configure webhook in Meta
7. ✅ Test with WhatsApp
8. ✅ Set up UptimeRobot for 24/7 uptime

**Your bot is now live! 🚀**

---

**Developed for**: AI Wrapper Competition 2025 - Ignite Pakistan
**Cost**: $0/month for up to 1,000 conversations
**Deployment Platform**: Replit (Free Tier)

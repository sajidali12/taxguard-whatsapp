# WhatsApp Cloud API Setup Guide

Complete guide to migrate from Twilio to WhatsApp Cloud API (FREE with custom name & picture)

## Why WhatsApp Cloud API?

- **FREE**: 1,000 conversations per month at no cost
- **Custom Business Profile**: Your own business name and profile picture
- **No Sandbox Limitations**: Use your own phone number
- **Official Meta Solution**: Direct integration with WhatsApp

---

## Step 1: Create Meta Business Account

1. Go to [Meta Business Suite](https://business.facebook.com/)
2. Click **"Create Account"**
3. Enter your business name (e.g., "TaxGuard AI")
4. Fill in business details
5. Verify your business email

---

## Step 2: Set Up WhatsApp Cloud API

### 2.1 Create Meta Developer App

1. Go to [Meta for Developers](https://developers.facebook.com/)
2. Click **"My Apps"** → **"Create App"**
3. Select **"Business"** as app type
4. Fill in app details:
   - **App Name**: TaxGuard AI Bot
   - **App Contact Email**: your@email.com
   - **Business Account**: Select your business account

### 2.2 Add WhatsApp Product

1. In your app dashboard, click **"Add Product"**
2. Find **"WhatsApp"** and click **"Set Up"**
3. Select your Meta Business Account
4. You'll see the WhatsApp **Getting Started** page

### 2.3 Get Test Number (Temporary)

Meta provides a test number to start immediately:

1. On the **Getting Started** page, you'll see:
   - **Phone Number ID** (copy this - you'll need it)
   - **Temporary Access Token** (copy this too)
2. Add your personal WhatsApp number as a recipient:
   - Click **"Add phone number"**
   - Enter your WhatsApp number with country code
   - Verify the OTP received on WhatsApp

### 2.4 Send Test Message

Test the API in the dashboard:
```bash
curl -X POST \
  'https://graph.facebook.com/v21.0/YOUR_PHONE_NUMBER_ID/messages' \
  -H 'Authorization: Bearer YOUR_ACCESS_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
    "messaging_product": "whatsapp",
    "to": "YOUR_WHATSAPP_NUMBER",
    "type": "text",
    "text": {
      "body": "Hello from TaxGuard AI!"
    }
  }'
```

If you receive the message, the API is working!

---

## Step 3: Get Permanent Access Token

The temporary token expires in 24 hours. Get a permanent one:

### 3.1 Create System User

1. Go to [Meta Business Settings](https://business.facebook.com/settings/)
2. Click **"Users"** → **"System Users"**
3. Click **"Add"** → Create system user:
   - **Name**: TaxGuard Bot
   - **Role**: Admin
4. Click **"Generate New Token"**
5. Select your app
6. Enable these permissions:
   - `whatsapp_business_messaging`
   - `whatsapp_business_management`
7. Click **"Generate Token"**
8. **COPY AND SAVE THIS TOKEN** - it won't be shown again!

---

## Step 4: Register Your Own Phone Number

To use your own business number (instead of Meta's test number):

### 4.1 Requirements

- A phone number NOT currently on WhatsApp
- Access to receive SMS/calls on that number
- Facebook Business verification (may be required)

### 4.2 Add Phone Number

1. In WhatsApp API Settings, go to **"Phone Numbers"**
2. Click **"Add Phone Number"**
3. Enter your business phone number
4. Verify via SMS/call
5. Set up two-factor authentication PIN
6. Your number is now registered!

### 4.3 Get New Phone Number ID

After registration, copy the new **Phone Number ID** (different from test number)

---

## Step 5: Customize Business Profile

This is where you set your custom name and picture!

### 5.1 Set Business Profile

1. Go to **WhatsApp Manager** → **Phone Numbers**
2. Click on your phone number
3. Click **"WhatsApp Business Profile"**
4. Fill in:
   - **Display Name**: TaxGuard AI (this appears to users!)
   - **Category**: Financial Services
   - **Description**: Pakistan's intelligent tax compliance assistant
   - **Business Email**: support@taxguard.ai
   - **Website**: https://taxguard.ai
   - **Address**: Your business address

### 5.2 Upload Profile Picture

1. Click **"Profile Photo"**
2. Upload an image:
   - **Format**: PNG or JPG
   - **Size**: Minimum 512x512 pixels
   - **Recommended**: Square image, 1024x1024
3. Click **"Save"**

**Your custom name and picture are now live!** 🎉

---

## Step 6: Set Up Webhook

Webhooks receive incoming messages from users.

### 6.1 Deploy Your App

First, deploy your Flask app to a public server:

**Option A: Using ngrok (for testing)**
```bash
# Install ngrok
brew install ngrok  # macOS
# or download from https://ngrok.com/

# Run your Flask app
python app_cloud_api.py

# In another terminal, expose it
ngrok http 5000

# Copy the HTTPS URL (e.g., https://abc123.ngrok.io)
```

**Option B: Deploy to Render/Railway/Heroku**
- Push your code to GitHub
- Connect to Render.com or Railway.app
- Deploy and get your public URL

### 6.2 Configure Webhook in Meta

1. In your app dashboard, go to **WhatsApp** → **Configuration**
2. In the **Webhook** section, click **"Edit"**
3. Enter:
   - **Callback URL**: `https://YOUR_DOMAIN/webhook`
   - **Verify Token**: Your custom token from `.env` (e.g., `taxguard_secret_token_123`)
4. Click **"Verify and Save"**

### 6.3 Subscribe to Webhook Events

1. Click **"Manage"** under Webhook Fields
2. Subscribe to:
   - ✅ **messages** (required)
3. Click **"Save"**

---

## Step 7: Configure Your Bot

### 7.1 Create .env File

Copy the example and fill in your values:
```bash
cp .env.cloud_api.example .env
```

Edit `.env`:
```bash
# Meta Configuration
META_ACCESS_TOKEN=your_permanent_access_token_from_step_3
META_PHONE_NUMBER_ID=your_phone_number_id_from_step_2_or_4
META_WEBHOOK_VERIFY_TOKEN=taxguard_secret_token_123

# AI Configuration (choose one)
OPENAI_API_KEY=sk-...
# OR
GEMINI_API_KEY=AIza...
```

### 7.2 Install Dependencies

```bash
pip install -r requirements_cloud_api.txt
```

### 7.3 Run Your Bot

```bash
python app_cloud_api.py
```

You should see:
```
🚀 TaxGuard AI WhatsApp Bot (Cloud API) starting on port 5000...
📱 Webhook endpoint: http://localhost:5000/webhook
🤖 AI Provider: GEMINI
✅ WhatsApp Cloud API configured
```

---

## Step 8: Test Your Bot

1. Open WhatsApp on your phone
2. Send a message to your business number
3. Try: **"start"** or **"hello"**
4. You should receive a welcome message from **TaxGuard AI** (with your custom name and picture!)

### Test Commands

- `start` - Welcome message
- `calculate tax` - Tax calculation prompt
- `How do I file tax return?` - AI-powered response
- `میرا ٹیکس کتنا ہے؟` - Urdu support test

---

## Pricing & Limits

### Free Tier
- **1,000 conversations/month** - FREE
- **24-hour conversation window**
- **Unlimited messages** within conversation window

### What's a Conversation?
- User-initiated: Starts when user messages you (free for 1st 1000)
- Business-initiated: Starts when you message user first (charged after free tier)

### After Free Tier
- User-initiated: $0.005 - $0.009 per conversation
- Business-initiated: $0.007 - $0.025 per conversation
- Pricing varies by country

---

## Troubleshooting

### Webhook Verification Failed
- ✅ Ensure verify token matches exactly
- ✅ Check URL is publicly accessible (HTTPS required)
- ✅ Remove trailing slashes from URL

### Messages Not Received
- ✅ Check webhook is subscribed to "messages" field
- ✅ Verify phone number is approved
- ✅ Check server logs for errors
- ✅ Test with Meta's test number first

### Access Token Expired
- ✅ Use permanent token (not temporary)
- ✅ Regenerate from System User settings

### Business Verification Required
- Some features require verified business
- Go to Meta Business Settings → Security Center
- Complete business verification process

---

## Migration from Twilio

### Files Created
- `app_cloud_api.py` - New WhatsApp Cloud API implementation
- `requirements_cloud_api.txt` - Updated dependencies
- `.env.cloud_api.example` - Environment variable template

### Key Differences

| Feature | Twilio | Cloud API |
|---------|--------|-----------|
| Cost | Paid | Free (1000/month) |
| Custom Profile | ❌ No (sandbox) | ✅ Yes |
| Phone Number | Twilio's | Your own |
| Setup | Easy | Moderate |
| API | Twilio SDK | REST API |

### Keep Both?
You can keep both implementations:
- `app.py` - Twilio version (for testing)
- `app_cloud_api.py` - Cloud API version (for production)

---

## Next Steps

1. ✅ Test thoroughly with your phone number
2. ✅ Add more features (buttons, templates, media)
3. ✅ Set up database for conversation history
4. ✅ Monitor usage in Meta Business Manager
5. ✅ Apply for business verification (if needed)
6. ✅ Scale to handle more users

---

## Useful Links

- [Meta for Developers](https://developers.facebook.com/)
- [WhatsApp Cloud API Docs](https://developers.facebook.com/docs/whatsapp/cloud-api)
- [WhatsApp Business Manager](https://business.facebook.com/wa/manage/)
- [API Reference](https://developers.facebook.com/docs/whatsapp/cloud-api/reference)
- [Message Templates](https://developers.facebook.com/docs/whatsapp/cloud-api/guides/send-message-templates)

---

## Support

If you encounter issues:
1. Check Meta Developer docs
2. Review server logs
3. Test with Meta's API explorer
4. Check webhook delivery logs in Meta dashboard

---

**Congratulations!** 🎉

You now have a FREE WhatsApp bot with your custom business name and profile picture using WhatsApp Cloud API!

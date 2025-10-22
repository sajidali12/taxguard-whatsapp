"""
TaxGuard AI - WhatsApp Chatbot using Meta Cloud API
Free implementation with custom business profile support

Requirements:
pip install flask requests openai python-dotenv google-generativeai

Environment Variables (.env file):
META_ACCESS_TOKEN=your_meta_access_token
META_PHONE_NUMBER_ID=your_phone_number_id
META_WEBHOOK_VERIFY_TOKEN=your_webhook_verify_token (create your own secret)
OPENAI_API_KEY=your_openai_key (optional - use either this or Gemini)
GEMINI_API_KEY=your_gemini_key (optional - use either this or OpenAI)
"""

from flask import Flask, request, jsonify
import requests
import os
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
META_ACCESS_TOKEN = os.getenv('META_ACCESS_TOKEN')
META_PHONE_NUMBER_ID = os.getenv('META_PHONE_NUMBER_ID')
META_WEBHOOK_VERIFY_TOKEN = os.getenv('META_WEBHOOK_VERIFY_TOKEN', 'taxguard_secret_token_123')
META_API_VERSION = os.getenv('META_API_VERSION', 'v21.0')

# WhatsApp Cloud API endpoint
WHATSAPP_API_URL = f"https://graph.facebook.com/{META_API_VERSION}/{META_PHONE_NUMBER_ID}/messages"

# Determine which AI provider to use
AI_PROVIDER = None
genai = None

if OPENAI_API_KEY:
    try:
        import openai
        openai.api_key = OPENAI_API_KEY
        AI_PROVIDER = "openai"
        print("🤖 Using OpenAI API")
    except ImportError:
        print("⚠️ Warning: openai package not installed. Run: pip3 install openai")

if not AI_PROVIDER and GEMINI_API_KEY:
    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        AI_PROVIDER = "gemini"
        print("🤖 Using Google Gemini API")
    except ImportError:
        print("⚠️ Warning: google-generativeai package not installed. Run: pip3 install google-generativeai")

if not AI_PROVIDER:
    print("⚠️ Warning: No AI API key configured or packages missing. Please set OPENAI_API_KEY or GEMINI_API_KEY and install required packages.")

# User conversation history (in production, use database)
user_sessions = {}

# System prompt for TaxGuard AI
SYSTEM_PROMPT = """You are TaxGuard AI, Pakistan's intelligent tax compliance assistant. You help Pakistani citizens with:
1. Tax filing guidance in Urdu and English
2. Tax calculations based on Pakistani tax laws
3. Deduction recommendations
4. Answering FBR-related questions
5. Explaining tax concepts simply

Guidelines:
- Be helpful, friendly, and professional
- Support both Urdu and English (detect language automatically)
- Provide specific guidance for Pakistani tax system
- Keep responses concise for WhatsApp (under 1500 characters)
- Use simple language, avoid jargon
- When asked about tax calculation, ask for: monthly income, profession, city
- Suggest legitimate deductions based on profession
- If asked about receipts/documents, explain you can process them via photo upload

Pakistani Tax Brackets 2024-25:
- Up to Rs. 600,000: 0%
- Rs. 600,001 to 1,200,000: 5%
- Rs. 1,200,001 to 2,400,000: 15%
- Rs. 2,400,001 to 3,600,000: 25%
- Rs. 3,600,001 to 6,000,000: 30%
- Above Rs. 6,000,000: 35%

Common deductions:
- Zakat/charitable donations (up to 30% of taxable income)
- Education expenses for children
- Medical expenses
- Pension contributions
- Life insurance premiums
"""

def send_whatsapp_message(recipient_phone, message_text):
    """Send message using WhatsApp Cloud API"""

    if not META_ACCESS_TOKEN or not META_PHONE_NUMBER_ID:
        print("⚠️ Error: WhatsApp Cloud API credentials not configured")
        return False

    headers = {
        "Authorization": f"Bearer {META_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": recipient_phone,
        "type": "text",
        "text": {
            "preview_url": False,
            "body": message_text
        }
    }

    try:
        response = requests.post(WHATSAPP_API_URL, headers=headers, json=payload)

        if response.status_code == 200:
            print(f"✅ Message sent successfully to {recipient_phone}")
            return True
        else:
            print(f"❌ Error sending message: {response.status_code}")
            print(f"Response: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Exception while sending message: {str(e)}")
        return False

def get_ai_response(user_message, user_id):
    """Get response from AI provider (OpenAI or Gemini)"""

    if AI_PROVIDER is None:
        return "معذرت / Sorry, AI service is not configured. Please contact administrator."

    # Initialize or retrieve conversation history
    if user_id not in user_sessions:
        user_sessions[user_id] = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]

    # Add user message to history
    user_sessions[user_id].append({"role": "user", "content": user_message})

    # Keep only last 10 messages to manage token limits
    if len(user_sessions[user_id]) > 11:  # 1 system + 10 messages
        user_sessions[user_id] = [user_sessions[user_id][0]] + user_sessions[user_id][-10:]

    try:
        if AI_PROVIDER == "openai":
            # Call OpenAI API
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=user_sessions[user_id],
                temperature=0.7,
                max_tokens=500
            )
            ai_message = response.choices[0].message.content

        elif AI_PROVIDER == "gemini":
            # Call Gemini API
            model = genai.GenerativeModel('gemini-2.0-flash-exp')

            # Convert message history to Gemini format
            conversation_text = SYSTEM_PROMPT + "\n\n"
            for msg in user_sessions[user_id][1:]:  # Skip system message
                if msg["role"] == "user":
                    conversation_text += f"User: {msg['content']}\n"
                elif msg["role"] == "assistant":
                    conversation_text += f"Assistant: {msg['content']}\n"

            # Generate response
            response = model.generate_content(conversation_text)
            ai_message = response.text

        # Add AI response to history
        user_sessions[user_id].append({"role": "assistant", "content": ai_message})

        return ai_message

    except Exception as e:
        return f"معذرت / Sorry, I'm experiencing technical difficulties. Please try again. Error: {str(e)}"

def process_whatsapp_message(message_data):
    """Process incoming WhatsApp message"""

    try:
        # Extract message details
        message = message_data['entry'][0]['changes'][0]['value']['messages'][0]
        sender_phone = message['from']
        message_type = message['type']

        # Only handle text messages for now
        if message_type != 'text':
            send_whatsapp_message(sender_phone, "Sorry, I can only process text messages at the moment.")
            return

        incoming_msg = message['text']['body'].strip()

        # Log incoming message
        print(f"📩 Received from {sender_phone}: {incoming_msg}")

        # Generate response based on message content
        response_text = None

        # Handle welcome message
        if incoming_msg.lower() in ['start', 'شروع', 'hello', 'hi', 'السلام علیکم']:
            response_text = """🇵🇰 *TaxGuard AI - خوش آمدید*

Welcome to Pakistan's intelligent tax assistant!

I can help you with:
✅ Tax calculations / ٹیکس کا حساب
✅ Filing guidance / فائلنگ کی رہنمائی
✅ Deduction tips / کٹوتیوں کی تجاویز
✅ FBR questions / ایف بی آر کے سوالات

Try asking:
• "Mera tax calculate karo" (میرا ٹیکس)
• "How do I file tax return?"
• "What deductions can I claim?"

*Type your question in Urdu or English!* 🤖"""

        # Handle tax calculation requests
        elif any(keyword in incoming_msg.lower() for keyword in ['calculate', 'حساب', 'tax kitna', 'کتنا ٹیکس']):
            response_text = """💰 *Tax Calculation*

Please provide:
1️⃣ Your monthly salary (e.g., "50000")
2️⃣ Your profession (e.g., "software engineer")
3️⃣ Your city (e.g., "Karachi")

Example: "Monthly income 80000, software engineer, Islamabad"

براہ کرم بتائیں:
ماہانہ تنخواہ، پیشہ، شہر"""

        # Handle empty or very short messages
        elif len(incoming_msg) < 3:
            response_text = "Please send a complete message. / براہ کرم مکمل پیغام بھیجیں۔"

        # Handle all other queries with AI
        else:
            # Get AI response
            ai_response = get_ai_response(incoming_msg, sender_phone)
            response_text = f"{ai_response}\n\n_- TaxGuard AI 🤖_"

        # Send response
        if response_text:
            send_whatsapp_message(sender_phone, response_text)
            print(f"📤 Sent response: {response_text[:100]}...")

    except Exception as e:
        print(f"❌ Error processing message: {str(e)}")

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    """Handle WhatsApp Cloud API webhook"""

    if request.method == 'GET':
        # Webhook verification (required by Meta)
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')

        if mode == 'subscribe' and token == META_WEBHOOK_VERIFY_TOKEN:
            print("✅ Webhook verified successfully!")
            return challenge, 200
        else:
            print("❌ Webhook verification failed!")
            return 'Forbidden', 403

    elif request.method == 'POST':
        # Handle incoming messages
        data = request.get_json()

        # Log webhook data
        print(f"📥 Webhook data: {json.dumps(data, indent=2)}")

        # Check if this is a message event
        if data.get('object') == 'whatsapp_business_account':
            if 'entry' in data and len(data['entry']) > 0:
                if 'changes' in data['entry'][0] and len(data['entry'][0]['changes']) > 0:
                    change = data['entry'][0]['changes'][0]

                    if change.get('field') == 'messages':
                        if 'messages' in change['value']:
                            # Process the message
                            process_whatsapp_message(data)

        return jsonify({"status": "ok"}), 200

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "TaxGuard AI WhatsApp Bot (Cloud API)",
        "ai_provider": AI_PROVIDER or "not_configured",
        "meta_configured": bool(META_ACCESS_TOKEN and META_PHONE_NUMBER_ID)
    }

@app.route('/', methods=['GET'])
def home():
    """Home page with setup instructions"""
    ai_status = f"🤖 {AI_PROVIDER.upper()}" if AI_PROVIDER else "⚠️ Not Configured"
    meta_status = "✅ Configured" if (META_ACCESS_TOKEN and META_PHONE_NUMBER_ID) else "⚠️ Not Configured"

    return f"""
    <html>
    <head><title>TaxGuard AI - WhatsApp Bot (Cloud API)</title></head>
    <body style="font-family: Arial; max-width: 800px; margin: 50px auto; padding: 20px;">
        <h1>🇵🇰 TaxGuard AI - WhatsApp Cloud API</h1>
        <h2>Status: ✅ Running</h2>
        <h3>AI Provider: {ai_status}</h3>
        <h3>Meta Cloud API: {meta_status}</h3>

        <h3>Setup Instructions:</h3>
        <ol>
            <li>Create a Meta (Facebook) Business account</li>
            <li>Set up WhatsApp Cloud API in Meta for Developers</li>
            <li>Get your Access Token and Phone Number ID</li>
            <li>Configure webhook URL: <code>https://YOUR_DOMAIN/webhook</code></li>
            <li>Set environment variables in .env file</li>
            <li>Customize your business profile (name, picture) in Meta Business Manager</li>
        </ol>

        <h3>Features:</h3>
        <ul>
            <li>✅ Bilingual support (Urdu & English)</li>
            <li>✅ Tax calculations</li>
            <li>✅ Filing guidance</li>
            <li>✅ Deduction recommendations</li>
            <li>✅ FBR query assistance</li>
            <li>🆕 Free WhatsApp Cloud API (1000 conversations/month)</li>
            <li>🆕 Custom business name & profile picture</li>
            <li>🆕 Multi-AI support (OpenAI GPT-4 or Google Gemini)</li>
        </ul>

        <h3>Webhook Verification:</h3>
        <p>Verify Token: <code>{META_WEBHOOK_VERIFY_TOKEN}</code></p>

        <p><strong>Developed for:</strong> AI Wrapper Competition 2025 - Ignite Pakistan</p>
    </body>
    </html>
    """

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 TaxGuard AI WhatsApp Bot (Cloud API) starting on port {port}...")
    print(f"📱 Webhook endpoint: http://localhost:{port}/webhook")

    if AI_PROVIDER:
        print(f"🤖 AI Provider: {AI_PROVIDER.upper()}")
    else:
        print("⚠️ Warning: No AI provider configured!")

    if META_ACCESS_TOKEN and META_PHONE_NUMBER_ID:
        print(f"✅ WhatsApp Cloud API configured")
    else:
        print("⚠️ Warning: WhatsApp Cloud API not configured!")
        print("   Set META_ACCESS_TOKEN and META_PHONE_NUMBER_ID in .env file")

    app.run(host='0.0.0.0', port=port, debug=True)

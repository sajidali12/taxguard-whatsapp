"""
TaxGuard AI - WhatsApp Chatbot Demo
Complete implementation for AI Wrapper Competition 2025

Requirements:
pip install flask twilio openai python-dotenv google-generativeai

Environment Variables (.env file):
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
OPENAI_API_KEY=your_openai_key (optional - use either this or Gemini)
GEMINI_API_KEY=your_gemini_key (optional - use either this or OpenAI)
"""

from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
import os
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')

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

# Initialize Twilio client
twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

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
            # Call Gemini API (using the latest model name)
            model = genai.GenerativeModel('gemini-2.0-flash-exp')

            # Convert message history to Gemini format
            # Combine system prompt with conversation history
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

def calculate_tax(annual_income):
    """Calculate Pakistani income tax"""
    tax = 0

    if annual_income <= 600000:
        tax = 0
    elif annual_income <= 1200000:
        tax = (annual_income - 600000) * 0.05
    elif annual_income <= 2400000:
        tax = 30000 + (annual_income - 1200000) * 0.15
    elif annual_income <= 3600000:
        tax = 210000 + (annual_income - 2400000) * 0.25
    elif annual_income <= 6000000:
        tax = 510000 + (annual_income - 3600000) * 0.30
    else:
        tax = 1230000 + (annual_income - 6000000) * 0.35

    return round(tax, 2)

@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle incoming WhatsApp messages"""

    # Get incoming message details
    incoming_msg = request.values.get('Body', '').strip()
    sender_number = request.values.get('From', '')

    # Create response object
    resp = MessagingResponse()
    msg = resp.message()

    # Log incoming message
    print(f"📩 Received from {sender_number}: {incoming_msg}")

    # Handle welcome message
    if incoming_msg.lower() in ['start', 'شروع', 'hello', 'hi', 'السلام علیکم']:
        welcome_text = """🇵🇰 *TaxGuard AI - خوش آمدید*

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

        msg.body(welcome_text)

    # Handle tax calculation requests
    elif any(keyword in incoming_msg.lower() for keyword in ['calculate', 'حساب', 'tax kitna', 'کتنا ٹیکس']):
        calculation_prompt = """💰 *Tax Calculation*

Please provide:
1️⃣ Your monthly salary (e.g., "50000")
2️⃣ Your profession (e.g., "software engineer")
3️⃣ Your city (e.g., "Karachi")

Example: "Monthly income 80000, software engineer, Islamabad"

براہ کرم بتائیں:
ماہانہ تنخواہ، پیشہ، شہر"""

        msg.body(calculation_prompt)

    # Handle empty or very short messages
    elif len(incoming_msg) < 3:
        msg.body("Please send a complete message. / براہ کرم مکمل پیغام بھیجیں۔")

    # Handle all other queries with AI
    else:
        # Get AI response
        ai_response = get_ai_response(incoming_msg, sender_number)

        # Add TaxGuard AI signature
        response_text = f"{ai_response}\n\n_- TaxGuard AI 🤖_"

        msg.body(response_text)
        print(f"📤 Sent response: {response_text[:100]}...")

    return str(resp)

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "TaxGuard AI WhatsApp Bot",
        "ai_provider": AI_PROVIDER or "not_configured"
    }

@app.route('/', methods=['GET'])
def home():
    """Home page with setup instructions"""
    ai_status = f"🤖 {AI_PROVIDER.upper()}" if AI_PROVIDER else "⚠️ Not Configured"
    return f"""
    <html>
    <head><title>TaxGuard AI - WhatsApp Bot</title></head>
    <body style="font-family: Arial; max-width: 800px; margin: 50px auto; padding: 20px;">
        <h1>🇵🇰 TaxGuard AI - WhatsApp Chatbot</h1>
        <h2>Status: ✅ Running</h2>
        <h3>AI Provider: {ai_status}</h3>

        <h3>Setup Instructions:</h3>
        <ol>
            <li>Your webhook URL: <code>https://YOUR_DOMAIN/webhook</code></li>
            <li>Configure this URL in Twilio WhatsApp Sandbox</li>
            <li>Set either OPENAI_API_KEY or GEMINI_API_KEY in your .env file</li>
            <li>Send "start" to your WhatsApp number to begin</li>
        </ol>

        <h3>Features:</h3>
        <ul>
            <li>✅ Bilingual support (Urdu & English)</li>
            <li>✅ Tax calculations</li>
            <li>✅ Filing guidance</li>
            <li>✅ Deduction recommendations</li>
            <li>✅ FBR query assistance</li>
            <li>🆕 Multi-AI support (OpenAI GPT-4 or Google Gemini)</li>
        </ul>

        <p><strong>Developed for:</strong> AI Wrapper Competition 2025 - Ignite Pakistan</p>
    </body>
    </html>
    """

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 TaxGuard AI WhatsApp Bot starting on port {port}...")
    print(f"📱 Webhook endpoint: http://localhost:{port}/webhook")
    if AI_PROVIDER:
        print(f"🤖 AI Provider: {AI_PROVIDER.upper()}")
    else:
        print("⚠️ Warning: No AI provider configured!")
    app.run(host='0.0.0.0', port=port, debug=True)

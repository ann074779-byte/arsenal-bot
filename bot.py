import os
import threading
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# ===== 1. FAKE WEBSITE TO KEEP RENDER HAPPY =====
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running")
    def log_message(self, format, *args):
        return

def keep_alive():
    port = int(os.environ.get("PORT", 10000))
    HTTPServer(("0.0.0.0", port), Handler).serve_forever()

threading.Thread(target=keep_alive, daemon=True).start()

# ===== 2. YOUR ARSENAL BOT =====
TOKEN = os.environ.get("BOT_TOKEN", "9147060497:AAEikPECab21wjANeffP5Ek1e4cgJY1Ft8E")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔴 Welcome to Arsenal Bot! ⚪\n\n"
        "Commands:\n"
        "/start - Show this message\n"
        "/news - Latest Arsenal news\n"
        "/fixtures - Next fixtures"
    )

async def news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Fetching latest Arsenal news...")
    try:
        # Use Google News RSS for Arsenal
        url = "https://news.google.com/rss/search?q=Arsenal+FC&hl=en&gl=KE&ceid=KE:en"
        r = requests.get(url, timeout=10)
        text = r.text
        # Simple parse - get first 5 titles
        import re
        titles = re.findall(r"<title>(.*?)</title>", text)
        # First title is feed title, skip it
        msg = "📰 Latest Arsenal News:\n\n"
        for t in titles[1:6]:
            t = t.replace("<![CDATA[", "").replace("]]>", "").replace("&amp;", "&")
            msg += f"• {t}\n\n"
        await update.message.reply_text(msg)
    except Exception as e:
        await update.message.reply_text("Could not fetch news right now. Try again later.")

async def fixtures(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "⚽ Next Arsenal Fixtures:\n\n"
        "Check the official Arsenal site for the latest fixtures:\n"
        "https://www.arsenal.com/fixtures"
    )

def main():
    print("Bot is running...")
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("news", news))
    app.add_handler(CommandHandler("fixtures", fixtures))
    app.run_polling()

if __name__ == "__main__":
    main()

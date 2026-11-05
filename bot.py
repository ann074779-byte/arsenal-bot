import os
import requests
import xml.etree.ElementTree as ET
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = "9147060497:AAEikPECab21wjANeffP5Ek1e4cgJY1Ft8E"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome to Arsenal News KE! 🔴⚪\n\n"
        "Send /news for latest Arsenal news\n"
        "Send /start to see this again"
    )

async def news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Fetching latest Arsenal news... ⏳")
    try:
        url = "https://feeds.bbci.co.uk/sport/football/teams/arsenal/rss.xml"
        r = requests.get(url, timeout=10)
        root = ET.fromstring(r.content)
        items = root.findall(".//item")[:5]
        msg = "🔴 *LATEST ARSENAL NEWS* ⚪\n\n"
        for item in items:
            title = item.findtext("title")
            link = item.findtext("link")
            msg += f"• {title}\n{link}\n\n"
        await update.message.reply_text(msg)
    except Exception as e:
        await update.message.reply_text("Sorry, couldn't fetch news now. Try again in 1 min.")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("news", news))
    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
import os, re, threading, requests
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from datetime import time as dtime
from zoneinfo import ZoneInfo

# ===== 1. KEEP RENDER HAPPY =====
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

# ===== 2. BOT =====
TOKEN = os.environ.get("BOT_TOKEN", "PASTE_YOUR_TOKEN_HERE")

# Store users who pressed /start so 8am news can find them
CHAT_IDS = set()

def get_news():
    try:
        url = "https://news.google.com/rss/search?q=Arsenal+FC&hl=en&gl=KE&ceid=KE:en"
        r = requests.get(url, timeout=15)
        items = re.findall(r"<item>(.*?)</item>", r.text, re.DOTALL)
        news = []
        for item in items[:5]:
            title = re.search(r"<title>(.*?)</title>", item, re.DOTALL)
            link = re.search(r"<link>(.*?)</link>", item, re.DOTALL)
            if title and link:
                t = title.group(1).replace("<![CDATA[", "").replace("]]>", "").replace("&amp;", "&").replace("&#39;", "'")
                l = link.group(1).strip()
                news.append((t, l))
        return news
    except Exception:
        return []

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    CHAT_IDS.add(update.effective_chat.id)
    await update.message.reply_text(
        "🔴 Welcome to Arsenal Bot! ⚪\n\n"
        "Commands:\n"
        "/start - Show this\n"
        "/news - Latest news with links 📰\n"
        "/fixtures - Next fixtures ⚽\n"
        "/table - Premier League table 🏆\n\n"
        "✅ You will also get auto news every day at 8:00 AM!"
    )

async def news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Fetching latest Arsenal news...")
    items = get_news()
    if not items:
        await update.message.reply_text("Could not fetch news. Try again.")
        return
    msg = "📰 Latest Arsenal News:\n\n"
    for i, (t, l) in enumerate(items, 1):
        msg += f"{i}. {t}\n🔗 {l}\n\n"
    await update.message.reply_text(msg, disable_web_page_preview=False)

async def fixtures(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "⚽ Next Arsenal Fixtures:\n\n"
        "Check official fixtures:\nhttps://www.arsenal.com/fixtures"
    )

async def table(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Fetching Premier League table...")
    try:
        # TheSportsDB - free, no key needed
        url = "https://www.thesportsdb.com/api/v1/json/3/lookuptable.php?l=4328&s=2026-2027"
        r = requests.get(url, timeout=15).json()
        rows = r.get("table", [])[:10]
        if not rows:
            raise Exception("no data")
        msg = "🏆 Premier League - Top 10:\n\n"
        msg += "Pos  Team              Pts\n"
        msg += "------------------------\n"
        for row in rows:
            pos = row.get("intRank", "?")
            team = row.get("strTeam", "?")[:16]
            pts = row.get("intPoints", "?")
            msg += f"{pos}.   {team:<16} {pts}\n"
        msg += "\nFull table: https://www.premierleague.com/tables"
        await update.message.reply_text(f"<pre>{msg}</pre>", parse_mode="HTML")
    except Exception as e:
        await update.message.reply_text("Could not fetch table. Try again later.\nhttps://www.premierleague.com/tables")

async def send_morning_news(context: ContextTypes.DEFAULT_TYPE):
    items = get_news()
    if not items:
        return
    msg = "☀️ Good Morning Gooner! 8AM Arsenal News:\n\n"
    for i, (t, l) in enumerate(items, 1):
        msg += f"{i}. {t}\n🔗 {l}\n\n"
    for chat_id in list(CHAT_IDS):
        try:
            await context.bot.send_message(chat_id=chat_id, text=msg)
        except Exception:
            pass

def main():
    print("Bot is running...")
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("news", news))
    app.add_handler(CommandHandler("fixtures", fixtures))
    app.add_handler(CommandHandler("table", table))
    # Auto news at 8:00 AM Kenya time
    if app.job_queue:
        app.job_queue.run_daily(send_morning_news, time=dtime(hour=8, minute=0, tzinfo=ZoneInfo("Africa/Nairobi")))
    app.run_polling()

if __name__ == "__main__":
    main()


import logging
import random
import time
from datetime import datetime, timedelta
from telegram import Update, InputMediaAnimation
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# Foydalanuvchilar ma'lumotlari
users = {}
last_active = {}

# Animatsion GIF fayl nomi
GIF_PATH = "plane.gif"

# Tasodifiy koeffitsient generatori
def generate_multiplier():
    return round(random.uniform(1.00, 5.00), 2)

# /start komandasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in users:
        users[user_id] = {"balance": 10000, "games": 0, "wins": 0}
    last_active[user_id] = datetime.now()
    await update.message.reply_text("🎮 Welcome to Aviator Bot!
Your balance: 10,000 UZS.
Enter your cashout (1.1 to 5.0):")

# O'yin funksiyasi
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text
    last_active[user_id] = datetime.now()

    try:
        cashout = float(text)
        if cashout < 1.1 or cashout > 5.0:
            raise ValueError

        multiplier = generate_multiplier()
        user = users[user_id]
        bet = 1000

        result = f"🎯 Multiplier: {multiplier}x\n"

        if multiplier >= cashout:
            win = int(bet * cashout)
            user["balance"] += win
            user["wins"] += 1
            result += f"✅ You won! +{win} UZS"
        else:
            user["balance"] -= bet
            result += f"❌ You lost. -{bet} UZS"

        user["games"] += 1
        result += f"\n📊 Balance: {user['balance']} UZS\n🎮 Rounds: {user['games']}, Wins: {user['wins']}"

        await context.bot.send_animation(chat_id=update.effective_chat.id, animation=open(GIF_PATH, 'rb'))
        await update.message.reply_text(result)

        # Onlayn foydalanuvchilar
        online_users = [f"@{context.bot.get_chat(uid).username or uid}" for uid, t in last_active.items()
                        if datetime.now() - t < timedelta(minutes=7)]
        if online_users:
            await update.message.reply_text("🟢 Online users: " + ", ".join(online_users))

    except:
        await update.message.reply_text("❗️ Invalid input. Please enter a cashout from 1.1 to 5.0.")

# Botni ishga tushirish
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    TOKEN = "YOUR_BOT_TOKEN_HERE"

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

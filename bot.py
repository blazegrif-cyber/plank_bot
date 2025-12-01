from datetime import time as dt_time
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
    JobQueue
)
import random
import json
import os

TOKEN = "8245220100:AAGz31sjwsTbFTZByAG6UnSoQj08MojcI0Q"
USERS_FILE = "users.json"

# -------------------------
# Стикеры
# -------------------------

# Стартовый стикер (ТОЛЬКО при /start)
START_STICKER = "CAACAgIAAxkBAAEB1rhpLaUheHaFYtPm_l6w0t-o60vd4QACQoUAAqzsYEnEt9oKoeiNDTYE"

# Все остальные стикеры
OTHER_STICKERS = [
    "CAACAgIAAxkBAAEB1rRpLaIuVytK8jeEkXhsrna8cjLqdwAC8q8AAqYvaUkCRK5gk9hBmTYE",
    "CAACAgIAAxkBAAEB1rJpLaIrsKEm513pp7LyEXSXpypCOAACspEAAlozaUmWa8V-QVU0QzYE",
    "CAACAgIAAxkBAAEB1rBpLaIk3NrqN3WzYeBLO7RiZMxWaAACOZEAAsBrYElSaCQefY_GXDYE",
    "CAACAgIAAxkBAAEB1q5pLaIfhUg1WuJjUJTMMLIivLsfygACWZ0AAjysaUln5o-qDCBi6jYE",
    "CAACAgIAAxkBAAEB1qxpLaIb29uWcn338qeK2gyTMVYQRQACX5YAAiUIaElbcrez6mvjBzYE",
    "CAACAgIAAxkBAAEB1qppLaIVWpiqBmm4NYcsSGafkhfr7gACzYgAAhdXaUmHRpjrHkd_XzYE",
    "CAACAgIAAxkBAAEB1qhpLaIQ6y2ZWebND1MLF-dSDPFq7QACVIYAAmXJYUmmDjZnR2qjwTYE",
    "CAACAgIAAxkBAAEB1rZpLaLS-qG1gb-9SKo7qtHQ-vdaQAACWYUAAnecaEmkhLAXDHS-iTYE",
    "CAACAgIAAxkBAAEUVV5pLZ4R0vcOQK5Bmjq1f-DvYvLG8wACGocAAqL2YEmCTk18tmClTDYE"
]

# -------------------------
# Работа с пользователями
# -------------------------

def load_users():
    if not os.path.exists(USERS_FILE):
        return []
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            if isinstance(data, dict):
                return [int(k) for k in data.keys() if k.isdigit()]
            return []
    except:
        return []

def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2)

# -------------------------
# /start
# -------------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    users = load_users()
    if user_id not in users:
        users.append(user_id)
        save_users(users)

    text = (
        "Привет!\n"
        "Я буду отслеживать твои дни планки!\n"
        "Используй кнопку 'Планка', чтобы открыть приложение."
    )
    await update.message.reply_text(text)

    # определённый старт-стикер
    try:
        await update.message.reply_sticker(START_STICKER)
    except Exception as e:
        print("Ошибка отправки стартового стикера:", e)

# -------------------------
# Напоминание в 23:00
# -------------------------

async def send_reminder(context: ContextTypes.DEFAULT_TYPE):
    users = load_users()
    for user_id in users:
        try:
            text = "Помнишь про планку?\n*Просто напоминаю =)*"
            await context.bot.send_message(chat_id=user_id, text=text, parse_mode="Markdown")

            sticker = random.choice(OTHER_STICKERS)
            await context.bot.send_sticker(chat_id=user_id, sticker=sticker)

        except Exception as e:
            print(f"Ошибка отправки напоминания пользователю {user_id}: {e}")

# -------------------------
# Ответ на любые сообщения
# -------------------------

async def unknown_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "Я не понимаю... Ты хочешь сделать планку?\n"
        "Используй кнопку \"Планка\", чтобы зафиксировать сегодняшний день!"
    )
    await update.message.reply_text(text)

    # случайный стикер из остальных
    try:
        sticker = random.choice(OTHER_STICKERS)
        await update.message.reply_sticker(sticker)
    except Exception as e:
        print("Ошибка отправки случайного стикера:", e)

# -------------------------
# Настройка бота
# -------------------------

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, unknown_message))

# напоминание ежедневно в 23:00
job_queue: JobQueue = app.job_queue
job_queue.run_daily(send_reminder, dt_time(hour=23, minute=0))

print("Бот запущен!")
app.run_polling()

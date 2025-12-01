import os
import json
import random
from datetime import datetime, time
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, JobQueue

# Получаем токен из переменных окружения
TOKEN = os.getenv("TELEGRAM_TOKEN")
USERS_FILE = "users.json"

# Стикеры
START_STICKER = "CAACAgIAAxkBAAEB1rhpLaUheHaFYtPm_l6w0t-o60vd4QACQoUAAqzsYEnEt9oKoeiNDTYE"
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

def load_users():
    """Загружает список пользователей из файла"""
    if not os.path.exists(USERS_FILE):
        return []
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except:
        return []

def save_users(users):
    """Сохраняет список пользователей в файл"""
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2)

def start(update, context):
    """Обработчик команды /start"""
    user_id = update.message.from_user.id
    users = load_users()
    
    if user_id not in users:
        users.append(user_id)
        save_users(users)
    
    text = (
        "Привет!\n"
        "Я буду отслеживать твои дни планки!\n"
        "Используй кнопку 'Планка', чтобы открыть приложение."
    )
    update.message.reply_text(text)
    
    try:
        update.message.reply_sticker(START_STICKER)
    except Exception as e:
        print(f"Ошибка отправки стикера: {e}")

def unknown_message(update, context):
    """Обработчик любых сообщений"""
    text = (
        "Я не понимаю... Ты хочешь сделать планку?\n"
        "Используй кнопку \"Планка\", чтобы зафиксировать сегодняшний день!"
    )
    update.message.reply_text(text)
    
    try:
        sticker = random.choice(OTHER_STICKERS)
        update.message.reply_sticker(sticker)
    except Exception as e:
        print(f"Ошибка отправки стикера: {e}")

def send_daily_reminder(context):
    """Ежедневное напоминание в 23:00"""
    job = context.job
    users = load_users()
    
    for user_id in users:
        try:
            text = "Помнишь про планку?\n*Просто напоминаю =)*"
            context.bot.send_message(
                chat_id=user_id, 
                text=text, 
                parse_mode="Markdown"
            )
            
            sticker = random.choice(OTHER_STICKERS)
            context.bot.send_sticker(chat_id=user_id, sticker=sticker)
            
        except Exception as e:
            print(f"Не удалось отправить напоминание {user_id}: {e}")

def error(update, context):
    """Обработчик ошибок"""
    print(f"Update {update} caused error {context.error}")

def main():
    """Основная функция запуска бота"""
    if not TOKEN:
        print("❌ ОШИБКА: TELEGRAM_TOKEN не найден!")
        print("Добавь переменную TELEGRAM_TOKEN в настройках Render")
        return
    
    print("🚀 Запуск бота на Render...")
    
    # Создаем Updater для версии 13.15
    updater = Updater(TOKEN, use_context=True)
    
    # Получаем диспетчер
    dp = updater.dispatcher
    
    # Добавляем обработчики
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text, unknown_message))
    dp.add_error_handler(error)
    
    # Настраиваем ежедневное напоминание в 23:00
    job_queue = updater.job_queue
    if job_queue:
        job_queue.run_daily(send_daily_reminder, time=time(hour=23, minute=0))
        print("⏰ Напоминание настроено на 23:00 ежедневно")
    
    # Запускаем бота
    print("✅ Бот запущен и работает!")
    print("📝 Отправь /start в Telegram для проверки")
    
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()

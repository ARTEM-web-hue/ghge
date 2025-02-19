import logging
from datetime import datetime, timedelta
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackContext,
)
from telegram import Update

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Глобальные переменные для статистики сообщений
message_count_all = {}  # Счетчик всех сообщений
message_count_hour = {}  # Счетчик сообщений за последний час
message_count_day = {}  # Счетчик сообщений за день
kalkylator_mode = False  # Флаг режима калькулятора


# Функция для проверки и вычисления математического выражения
def evaluate_expression(expression: str) -> str:
    try:
        result = eval(expression)
        if isinstance(result, int):
            if result % 2 == 0:
                return f"{result}=͟͟͞͞🏀"
            else:
                return f"{result}🏀"
        return ""
    except Exception:
        return ""


# Команда /start
async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("Бот запущен! Используйте команды для взаимодействия.")


# Команда /kalkylator
async def kalkylator(update: Update, context: CallbackContext) -> None:
    global kalkylator_mode
    kalkylator_mode = not kalkylator_mode
    status = "включен" if kalkylator_mode else "выключен"
    await update.message.reply_text(f"Режим калькулятора {status}!")


# Обработка текстовых сообщений
async def handle_message(update: Update, context: CallbackContext) -> None:
    global kalkylator_mode

    user_id = update.message.from_user.id
    now = datetime.now()

    # Обновление статистики сообщений
    message_count_all[user_id] = message_count_all.get(user_id, 0) + 1
    message_count_hour[user_id] = message_count_hour.get(user_id, {"count": 0, "time": now})
    message_count_day[user_id] = message_count_day.get(user_id, {"count": 0, "time": now})

    if (now - message_count_hour[user_id]["time"]).total_seconds() > 3600:
        message_count_hour[user_id] = {"count": 0, "time": now}
    if (now - message_count_day[user_id]["time"]).total_seconds() > 86400:
        message_count_day[user_id] = {"count": 0, "time": now}

    message_count_hour[user_id]["count"] += 1
    message_count_day[user_id]["count"] += 1

    # Режим калькулятора
    if kalkylator_mode:
        response = evaluate_expression(update.message.text)
        if response:
            await update.message.reply_text(response)
        return

    # Обработка действий
    reply_to_message = update.message.reply_to_message
    if reply_to_message and reply_to_message.from_user:
        action = update.message.text.strip()
        if len(action) > 2:
            action = action[:-2] + "л(а)"
            sender_username = update.message.from_user.username or "Игрок"
            recipient_username = reply_to_message.from_user.username or "Пользователь"
            await update.message.reply_text(f"@{sender_username} {action} @{recipient_username}")


# Команда !Статачас
async def stat_hour(update: Update, context: CallbackContext) -> None:
    now = datetime.now()
    filtered_stats = {
        user_id: data["count"]
        for user_id, data in message_count_hour.items()
        if (now - data["time"]).total_seconds() <= 3600
    }
    sorted_stats = sorted(filtered_stats.items(), key=lambda x: x[1], reverse=True)[:10]

    response = "Топ по сообщениям за последний час:\n"
    for idx, (user_id, count) in enumerate(sorted_stats, start=1):
        username = update.effective_chat.get_member(user_id).user.username or "Пользователь"
        response += f"{idx}. 🏆(@{username}) {count} сообщений\n"

    await update.message.reply_text(response or "За последний час никто не писал.")


# Команда !Статаалл
async def stat_all(update: Update, context: CallbackContext) -> None:
    sorted_stats = sorted(message_count_all.items(), key=lambda x: x[1], reverse=True)[:10]

    response = "Топ по всем сообщениям:\n"
    for idx, (user_id, count) in enumerate(sorted_stats, start=1):
        username = update.effective_chat.get_member(user_id).user.username or "Пользователь"
        response += f"{idx}. 🏆(@{username}) {count} сообщений\n"

    await update.message.reply_text(response or "Никто еще не писал.")


# Команда !Статадень
async def stat_day(update: Update, context: CallbackContext) -> None:
    now = datetime.now()
    filtered_stats = {
        user_id: data["count"]
        for user_id, data in message_count_day.items()
        if (now - data["time"]).total_seconds() <= 86400
    }
    sorted_stats = sorted(filtered_stats.items(), key=lambda x: x[1], reverse=True)[:10]

    response = "Топ по сообщениям за день:\n"
    for idx, (user_id, count) in enumerate(sorted_stats, start=1):
        username = update.effective_chat.get_member(user_id).user.username or "Пользователь"
        response += f"{idx}. 🏆(@{username}) {count} сообщений\n"

    await update.message.reply_text(response or "За день никто не писал.")


# Основная функция
def main():
    token = "7613638103:AAFi9pdL77iWZuZ4-vwh35sycLQh-Jx5RiQ"  # Замените YOUR_BOT_TOKEN на токен вашего бота
    application = Application.builder().token(token).build()

    # Регистрация обработчиков
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("kalkylator", kalkylator))
    application.add_handler(CommandHandler("Статачас", stat_hour))
    application.add_handler(CommandHandler("Статаалл", stat_all))
    application.add_handler(CommandHandler("Статадень", stat_day))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Бот запущен...")
    application.run_polling()


if __name__ == "__main__":
    main()
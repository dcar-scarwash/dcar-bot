import logging, os
from telegram import (
    Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
)
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters, ConversationHandler, CallbackQueryHandler, ContextTypes
)

CATEGORY, SERVICE, DATE, TIME, CONFIRM = range(5)

CATEGORIES = {
    "Кат.1 🚗": "Легковой",
    "Кат.2 🏎️": "Купе",
    "Кат.3 🚙": "Кроссовер/Джип",
    "Кат.4 🚐": "Фургон",
    "Кат.5 🚐": "Минивэн"
}

SERVICES = {
    "Пробивка": "probivka",
    "Мойка кузова": "body",
    "Полная мойка": "full",
    "Премиум": "premium"
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я бот бронирования автомойки DCAR‑S. Выбери категорию авто:",
        reply_markup=ReplyKeyboardMarkup([[k] for k in CATEGORIES.keys()], one_time_keyboard=True, resize_keyboard=True),
    )
    return CATEGORY

async def choose_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["category"] = update.message.text
    await update.message.reply_text(
        "Отлично! Теперь выбери услугу:",
        reply_markup=ReplyKeyboardMarkup([[k] for k in SERVICES.keys()], one_time_keyboard=True, resize_keyboard=True),
    )
    return SERVICE

async def choose_service(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["service"] = update.message.text
    today_btns = [
        InlineKeyboardButton("Сегодня", callback_data="today"),
        InlineKeyboardButton("Завтра", callback_data="tomorrow"),
    ]
    await update.message.reply_text(
        "На какой день хотите записаться?",
        reply_markup=InlineKeyboardMarkup.from_row(today_btns),
    )
    return DATE

async def pick_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    choice = query.data
    context.user_data["date"] = choice
    times = ["09:00", "10:00", "11:00", "13:00", "14:00", "15:00", "17:00"]
    buttons = [[InlineKeyboardButton(t, callback_data=t)] for t in times]
    await query.edit_message_text("Выберите время:", reply_markup=InlineKeyboardMarkup(buttons))
    return TIME

async def pick_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["time"] = query.data
    data = context.user_data
    summary = f"Категория: {data['category']}\nУслуга: {data['service']}\nДата: {data['date']}\nВремя: {data['time']}\n\nПодтверждаете?"
    btns = [
        InlineKeyboardButton("✅ Да", callback_data="yes"),
        InlineKeyboardButton("❌ Отмена", callback_data="no"),
    ]
    await query.edit_message_text(summary, reply_markup=InlineKeyboardMarkup.from_row(btns))
    return CONFIRM

async def confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "yes":
        await query.edit_message_text("Бронирование подтверждено! Ждём вас 🚗")
    else:
        await query.edit_message_text("Бронирование отменено.")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Отменено.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

def main():
    token = os.getenv("BOT_TOKEN")
    if not token:
        print("Укажите BOT_TOKEN в переменной окружения")
        return
    logging.basicConfig(level=logging.INFO)
    application = Application.builder().token(token).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CATEGORY: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_category)],
            SERVICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_service)],
            DATE: [CallbackQueryHandler(pick_date)],
            TIME: [CallbackQueryHandler(pick_time)],
            CONFIRM: [CallbackQueryHandler(confirm)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv)
    application.run_polling()

if __name__ == "__main__":
    main()

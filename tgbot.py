Python 3.12.1 (tags/v3.12.1:2305ca5, Dec  7 2023, 22:03:25) [MSC v.1937 64 bit (AMD64)] on win32
Type "help", "copyright", "credits" or "license()" for more information.
>>> from telegram import Update
... from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler
... import datetime
... import logging
... 
... # Enable logging
... logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
... logger = logging.getLogger(__name__)
... 
... # States
... CHOOSING, SET_DAILY_REMINDER, SET_CUSTOM_REMINDER = range(3)
... 
... # Dictionary to store user reminders
... user_reminders = {}
... 
... def start(update: Update, context: CallbackContext) -> int:
...     update.message.reply_text(
...         "Привіт! Я бот для нагадувань. Виберіть опцію для налаштування нагадувань:\n"
...         "1. /daily - Нагадування кожен день\n"
...         "2. /custom - Нагадування за конкретною датою та часом"
...     )
...     return CHOOSING
... 
... def set_daily(update: Update, context: CallbackContext) -> int:
...     user_id = update.message.from_user.id
...     user_reminders[user_id] = {'type': 'daily'}
...     update.message.reply_text("Нагадування встановлено. Я буду нагадувати вам кожен день.")
...     return ConversationHandler.END
... 
... def set_custom(update: Update, context: CallbackContext) -> int:
...     update.message.reply_text("Введіть дату та час для нагадування (у форматі YYYY-MM-DD HH:MM):")
...     return SET_CUSTOM_REMINDER

def save_custom(update: Update, context: CallbackContext) -> int:
    user_id = update.message.from_user.id
    custom_datetime_str = update.message.text

    try:
        custom_datetime = datetime.datetime.strptime(custom_datetime_str, "%Y-%m-%d %H:%M")
        user_reminders[user_id] = {'type': 'custom', 'datetime': custom_datetime}
        update.message.reply_text(f"Нагадування встановлено на {custom_datetime}.")
    except ValueError:
        update.message.reply_text("Неправильний формат дати та часу. Спробуйте ще раз.")
        return SET_CUSTOM_REMINDER

    return ConversationHandler.END

def remind_job(context: CallbackContext):
    for user_id, reminder_info in user_reminders.items():
        if reminder_info['type'] == 'daily':
            context.bot.send_message(chat_id=user_id, text="Нагадування: Кожен день!")
        elif reminder_info['type'] == 'custom':
            current_datetime = datetime.datetime.now()
            if current_datetime >= reminder_info['datetime']:
                context.bot.send_message(chat_id=user_id, text="Нагадування: Час настав!")

def main() -> None:
    updater = Updater("YOUR_TELEGRAM_BOT_TOKEN")
    dp = updater.dispatcher

    # Create the conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CHOOSING: [CommandHandler('daily', set_daily), CommandHandler('custom', set_custom)],
            SET_CUSTOM_REMINDER: [MessageHandler(Filters.text & ~Filters.command, save_custom)],
        },
        fallbacks=[],
    )

    dp.add_handler(conv_handler)

    # Job to send reminders
    job_queue = updater.job_queue
    job_queue.run_daily(remind_job, time=datetime.time(0, 0, 0))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()

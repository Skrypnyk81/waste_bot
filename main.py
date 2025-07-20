import logging
import os
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler
from dotenv import load_dotenv

from commands.handlers import (
    start, set_notification_time, handle_custom_time, set_address, handle_address_input, 
    check_today, check_tomorrow, show_info, stop_notifications, restart_notifications, 
    set_notification, set_address_command, SETTING_TIME, SETTING_ADDRESS
)
from logic.schedule import schedule_tomorrow_notification
from db_manager import DatabaseManager

load_dotenv()

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Replace with your actual Telegram Bot token
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Inizializza il database manager
db = DatabaseManager(os.environ.get('DATABASE_URL'))

def main() -> None:
    """Start the bot."""
    # Create the Application
    application = ApplicationBuilder().token(TOKEN).build()
    
    # Add conversation handler for setup
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
            CommandHandler("setNotifica", set_notification),
            CommandHandler("setIndirizzo", set_address_command)
        ],
        states={
            SETTING_TIME: [
                CallbackQueryHandler(set_notification_time, pattern="^(now|default|custom)$"),
                MessageHandler(telegram.ext.filters.TEXT & ~telegram.ext.filters.COMMAND, handle_custom_time)
            ],
            SETTING_ADDRESS: [
                CallbackQueryHandler(set_address, pattern="^(yes_address|no_address)$"),
                MessageHandler(telegram.ext.filters.TEXT & ~telegram.ext.filters.COMMAND, handle_address_input)
            ]
        },
        fallbacks=[CommandHandler("start", start)]
    )
    
    application.add_handler(conv_handler)
    
    # Add command handlers
    application.add_handler(CommandHandler("oggi", check_today))
    application.add_handler(CommandHandler("domani", check_tomorrow))
    application.add_handler(CommandHandler("info", show_info))
    application.add_handler(CommandHandler("stop", stop_notifications))
    application.add_handler(CommandHandler("restart", restart_notifications))

    # Start the Bot
    try:
        # Schedule notifications for all users when the bot starts
        application.job_queue.run_once(
            lambda context: schedule_tomorrow_notification(context),
            0
        )
        
        application.run_polling(timeout=60)
    finally:
        # Make sure to close the database connection when the bot stops
        db.close()

if __name__ == '__main__':
    main()
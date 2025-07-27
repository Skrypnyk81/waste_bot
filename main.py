import logging
import os
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ConversationHandler,
    MessageHandler,
    filters  # Assicurati che filters sia importato
)
from dotenv import load_dotenv

# Importa gli handler esistenti
from commands.handlers import (
    start, set_notification_time, handle_custom_time, set_address, handle_address_input,
    check_today, check_tomorrow, show_info, stop_notifications, restart_notifications,
    set_notification, set_address_command, SETTING_TIME, SETTING_ADDRESS
)
# Importa i nuovi handler per i bidoni
from commands.bins_handler import (
    show_bins_menu,
    button_handler,
    handle_limit_input,
    cancel,
    SETTING_LIMIT
)
from service.schedule import schedule_tomorrow_notification
from db_manager import DatabaseManager

load_dotenv()

# Configurazione del logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
db = DatabaseManager(os.environ.get('DATABASE_URL'))

def main() -> None:
    """Avvia il bot."""
    application = ApplicationBuilder().token(TOKEN).build()

    # Conversation handler per la configurazione iniziale (/start)
    setup_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            SETTING_TIME: [
                CallbackQueryHandler(set_notification_time, pattern="^(now|default|custom)$"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_custom_time)
            ],
            SETTING_ADDRESS: [
                CallbackQueryHandler(set_address, pattern="^(yes_address|no_address)$"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_address_input)
            ]
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )

    # Conversation handler per la gestione dei bidoni (/bidone)
    bins_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("bidone", show_bins_menu)],
        states={
            # Stato in attesa dell'input numerico per il limite
            SETTING_LIMIT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_limit_input)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        # Permetti di gestire i pulsanti come entry point dopo il primo avvio
        map_to_parent={
            ConversationHandler.END: ConversationHandler.END
        }
    )

    # Aggiungi un handler per i pulsanti che non fanno parte di una conversazione attiva
    # Questo gestirà i pulsanti del menu dei bidoni
    application.add_handler(CallbackQueryHandler(button_handler))
    
    # Aggiungi i conversation handler
    application.add_handler(setup_conv_handler)
    application.add_handler(bins_conv_handler)

    # Aggiungi gli altri command handler
    application.add_handler(CommandHandler("oggi", check_today))
    application.add_handler(CommandHandler("domani", check_tomorrow))
    application.add_handler(CommandHandler("info", show_info))
    application.add_handler(CommandHandler("stop", stop_notifications))
    application.add_handler(CommandHandler("restart", restart_notifications))
    application.add_handler(CommandHandler("setNotifica", set_notification))
    application.add_handler(CommandHandler("setIndirizzo", set_address_command))

    try:
        # Programma le notifiche all'avvio del bot
        application.job_queue.run_once(
            lambda context: schedule_tomorrow_notification(context), 0
        )
        application.run_polling(timeout=60)
    finally:
        db.close()

if __name__ == '__main__':
    main()
import datetime
import logging
import os
import pytz
import telegram
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes, ConversationHandler, MessageHandler
from config.waste_schedules import WASTE_SCHEDULE, WASTE_INSTRUCTIONS, WASTE_EMOJI, DAY_NAMES, MONTH_NAMES

from dotenv import load_dotenv
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

# Define conversation states
SETTING_TIME, SETTING_ADDRESS = range(2)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Send a welcome message when the command /start is issued."""
    user = update.effective_user
    user_id = user.id
    
    # Crea o recupera l'utente dal database
    user_data = db.get_user(user_id)
    if not user_data:
        db.create_user(user_id, user.username, user.first_name, user.last_name)
        user_data = db.get_user(user_id)
    
    await update.message.reply_text(
        f"Ciao {user.first_name}! 👋\n\n"
        f"Benvenuto al bot per la raccolta differenziata di Calvenzano.\n\n"
        f"Questo bot ti invierà notifiche sui giorni di raccolta dei rifiuti in base al calendario 2025 del Comune di Calvenzano.\n\n"
        f"Usa i seguenti comandi:\n"
        f"/oggi - Verifica quali rifiuti raccolgono oggi\n"
        f"/domani - Verifica quali rifiuti raccolgono domani\n"
        f"/setNotifica - Imposta l'orario della notifica giornaliera\n"
        f"/setIndirizzo - Imposta il tuo indirizzo per i tessili\n"
        f"/info - Istruzioni per la raccolta differenziata\n"
        f"/stop - Disattiva le notifiche\n"
        f"/start - Riattiva le notifiche"
    )
    
    # Ask for notification time setting
    keyboard = [
        [InlineKeyboardButton("Adesso", callback_data="now")],
        [InlineKeyboardButton("20:00 (Default)", callback_data="default")],
        [InlineKeyboardButton("Personalizza", callback_data="custom")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "A che ora vuoi ricevere le notifiche per la raccolta rifiuti?",
        reply_markup=reply_markup
    )
    
    return SETTING_TIME

async def set_notification_time(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle notification time selection."""
    query = update.callback_query
    user_id = query.from_user.id
    
    await query.answer()
    
    if query.data == "now":
        # Get current time
        now = datetime.datetime.now(pytz.timezone('Europe/Rome'))
        notification_time = now.strftime("%H:%M")
        db.set_notification_time(user_id, notification_time)
        await query.edit_message_text(
            f"Notifiche impostate per le {notification_time}.\n\n"
            f"Vuoi impostare il tuo indirizzo per la raccolta dei tessili?"
        )
    elif query.data == "default":
        db.set_notification_time(user_id, "20:00")
        await query.edit_message_text(
            "Notifiche impostate per le 20:00.\n\n"
            "Vuoi impostare il tuo indirizzo per la raccolta dei tessili?"
        )
    elif query.data == "custom":
        await query.edit_message_text(
            "Per favore, invia l'orario in cui desideri ricevere le notifiche nel formato HH:MM (es. 19:30)"
        )
        return SETTING_TIME
    
    # Ask for address
    keyboard = [
        [InlineKeyboardButton("Sì", callback_data="yes_address")],
        [InlineKeyboardButton("No", callback_data="no_address")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await context.bot.send_message(
        chat_id=user_id,
        text="Vuoi impostare il tuo indirizzo per la raccolta dei tessili?",
        reply_markup=reply_markup
    )
    
    return SETTING_ADDRESS

async def handle_custom_time(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle custom time input."""
    text = update.message.text
    user_id = update.effective_user.id
    
    # Check if the format is correct (HH:MM)
    try:
        hours, minutes = map(int, text.split(':'))
        if 0 <= hours <= 23 and 0 <= minutes <= 59:
            notification_time = f"{hours:02d}:{minutes:02d}"
            db.set_notification_time(user_id, notification_time)
            await update.message.reply_text(
                f"Notifiche impostate per le {notification_time}."
            )
        else:
            await update.message.reply_text(
                "Formato orario non valido. Per favore, usa il formato HH:MM (es. 19:30)"
            )
            return SETTING_TIME
    except ValueError:
        await update.message.reply_text(
            "Formato orario non valido. Per favore, usa il formato HH:MM (es. 19:30)"
        )
        return SETTING_TIME
    
    # Ask for address
    keyboard = [
        [InlineKeyboardButton("Sì", callback_data="yes_address")],
        [InlineKeyboardButton("No", callback_data="no_address")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "Vuoi impostare il tuo indirizzo per la raccolta dei tessili?",
        reply_markup=reply_markup
    )
    
    return SETTING_ADDRESS

async def set_address(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle address setting."""
    query = update.callback_query
    user_id = query.from_user.id
    
    await query.answer()
    
    if query.data == "yes_address":
        await query.edit_message_text(
            "Per favore, invia il tuo indirizzo (via e numero civico)"
        )
        return SETTING_ADDRESS
    elif query.data == "no_address":
        await query.edit_message_text(
            "Configurazione completata! Riceverai notifiche per la raccolta dei rifiuti.\n\n"
            "Usa /oggi per verificare la raccolta di oggi o /domani per quella di domani."
        )
        # Ensure notifications are enabled
        db.set_notifications_enabled(user_id, True)
        # Schedule the first check for tomorrow's waste collection
        await schedule_tomorrow_notification(context)
        return ConversationHandler.END

async def handle_address_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle address input."""
    text = update.message.text
    user_id = update.effective_user.id
    
    # Save the address
    db.set_address(user_id, text)
    
    await update.message.reply_text(
        f"Indirizzo impostato: {text}\n\n"
        f"Configurazione completata! Riceverai notifiche per la raccolta dei rifiuti.\n\n"
        f"Usa /oggi per verificare la raccolta di oggi o /domani per quella di domani."
    )
    
    # Ensure notifications are enabled
    db.set_notifications_enabled(user_id, True)
    # Schedule the first check for tomorrow's waste collection
    await schedule_tomorrow_notification(context)
    
    return ConversationHandler.END

async def check_today(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Check what waste types are collected today."""
    today = datetime.datetime.now(pytz.timezone('Europe/Rome'))
    waste_types = get_waste_collection(today.day, today.month)
    
    if waste_types:
        await update.message.reply_text(
            f"📅 Oggi, {DAY_NAMES[today.weekday()]} {today.day} {MONTH_NAMES[today.month]}, verranno raccolti:\n\n" +
            "\n".join([f"{WASTE_EMOJI[waste_type]} {waste_type}" for waste_type in waste_types]) +
            "\n\nRicorda: posiziona i rifiuti in strada non prima delle ore 20:00 del giorno precedente."
        )
    else:
        await update.message.reply_text(
            f"📅 Oggi, {DAY_NAMES[today.weekday()]} {today.day} {MONTH_NAMES[today.month]}, non è prevista alcuna raccolta di rifiuti."
        )

async def check_tomorrow(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Check what waste types are collected tomorrow."""
    today = datetime.datetime.now(pytz.timezone('Europe/Rome'))
    tomorrow = today + datetime.timedelta(days=1)
    waste_types = get_waste_collection(tomorrow.day, tomorrow.month)
    
    if waste_types:
        await update.message.reply_text(
            f"📅 Domani, {DAY_NAMES[tomorrow.weekday()]} {tomorrow.day} {MONTH_NAMES[tomorrow.month]}, verranno raccolti:\n\n" +
            "\n".join([f"{WASTE_EMOJI[waste_type]} {waste_type}" for waste_type in waste_types]) +
            "\n\nRicorda: posiziona i rifiuti in strada non prima delle ore 20:00 di oggi."
        )
    else:
        await update.message.reply_text(
            f"📅 Domani, {DAY_NAMES[tomorrow.weekday()]} {tomorrow.day} {MONTH_NAMES[tomorrow.month]}, non è prevista alcuna raccolta di rifiuti."
        )

async def set_notification(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle the /setNotifica command."""
    user_id = update.effective_user.id
    logger.info(f"Update setting notification for user {user_id}")
    
    # Ask for notification time setting
    keyboard = [
        [InlineKeyboardButton("Adesso", callback_data="now")],
        [InlineKeyboardButton("20:00 (Default)", callback_data="default")],
        [InlineKeyboardButton("Personalizza", callback_data="custom")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "A che ora vuoi ricevere le notifiche per la raccolta rifiuti?",
        reply_markup=reply_markup
    )
    
    return SETTING_TIME

async def set_address_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle the /setIndirizzo command."""
    await update.message.reply_text(
        "Per favore, invia il tuo indirizzo (via e numero civico) per la raccolta dei tessili."
    )
    
    return SETTING_ADDRESS

async def show_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show waste disposal instructions."""
    info_text = "ℹ️ **ISTRUZIONI PER LA RACCOLTA DIFFERENZIATA**\n\n"
    
    for waste_type, instruction in WASTE_INSTRUCTIONS.items():
        info_text += f"{WASTE_EMOJI[waste_type]} **{waste_type}**\n{instruction}\n\n"
    
    info_text += (
        "⏰ **ORARI CENTRO DI RACCOLTA**\n\n"
        "**Dal 1° Aprile al 30 Settembre:**\n"
        "- Martedì: 9.00 - 13.00\n"
        "- Giovedì: 14.00 - 18.00\n"
        "- Sabato: 9.00 - 12.00, 15.00 - 18.00\n\n"
        "**Dal 1° Ottobre al 31 Marzo:**\n"
        "- Martedì: 10.00 - 13.00\n"
        "- Giovedì: 14.00 - 17.00\n"
        "- Sabato: 10.00 - 13.00, 14.00 - 17.00\n\n"
        "⚠️ **NOTA**: La raccolta dei rifiuti viene effettuata a partire dalle ore 5.00. "
        "Posizionare i rifiuti in strada non prima delle ore 20.00 del giorno precedente.\n\n"
        "Per segnalare disservizi: tel. 0363/860737"
    )
    
    await update.message.reply_text(info_text, parse_mode=telegram.constants.ParseMode.MARKDOWN)

async def stop_notifications(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Disable notifications."""
    user_id = update.effective_user.id
    db.set_notifications_enabled(user_id, False)
    
    await update.message.reply_text(
        "Notifiche disattivate. Usa /start per riattivarle."
    )

async def restart_notifications(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Re-enable notifications."""
    user_id = update.effective_user.id
    db.set_notifications_enabled(user_id, True)
    
    await update.message.reply_text(
        "Notifiche riattivate. Riceverai informazioni sulla raccolta differenziata."
    )
    
    # Schedule the next notification
    await schedule_tomorrow_notification(context)

def get_waste_collection(day, month):
    """Get waste types collected on a specific date."""
    waste_types = []
    
    for waste_type, schedule in WASTE_SCHEDULE.items():
        if month in schedule and day in schedule[month]:
            waste_types.append(waste_type)
    
    return waste_types

async def send_notification(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send notification about tomorrow's waste collection."""
    job = context.job
    user_id = job.data
    
    # Get user data from database
    user_data = db.get_user(user_id)
    
    # Check if notifications are enabled for this user
    if not user_data or not user_data.get('notifications_enabled', False):
        return
    
    # Get tomorrow's date
    today = datetime.datetime.now(pytz.timezone('Europe/Rome'))
    tomorrow = today + datetime.timedelta(days=1)
    
    # Get waste collection for tomorrow
    waste_types = get_waste_collection(tomorrow.day, tomorrow.month)
    
    if waste_types:
        message = (
            f"📢 **PROMEMORIA RACCOLTA RIFIUTI**\n\n"
            f"Domani, {DAY_NAMES[tomorrow.weekday()]} {tomorrow.day} {MONTH_NAMES[tomorrow.month]}, verranno raccolti:\n\n" +
            "\n".join([f"{WASTE_EMOJI[waste_type]} **{waste_type}**" for waste_type in waste_types]) +
            "\n\nRicorda: posiziona i rifiuti in strada non prima delle ore 20:00 di oggi."
        )
        
        # Add special note for textile collection (last Thursday of month)
        address = user_data.get('address')
        if "TESSILI E INDUMENTI" in waste_types and address:
            message += (
                f"\n\n👕 **IMPORTANTE**: Domani è prevista la raccolta di tessili e indumenti usati. "
                f"Il tuo indirizzo registrato è: {address}. "
                f"Ricorda di segnalare via WhatsApp al 324 150 8217."
            )
        
        await context.bot.send_message(
            user_id,
            message,
            parse_mode=telegram.constants.ParseMode.MARKDOWN
        )
    
    # Schedule the next notification for tomorrow
    await schedule_tomorrow_notification(context)

async def schedule_tomorrow_notification(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Schedule notification for tomorrow's waste collection."""
    # Remove all existing jobs
    current_jobs = context.job_queue.get_jobs_by_name("notification")
    for job in current_jobs:
        job.schedule_removal()
    
    # Get all users who have notifications enabled
    users = db.get_all_users_for_notification()
    
    # Schedule notifications for all users
    for user in users:
        user_id = user['user_id']
        notification_time = user['notification_time']
        
        # Parse notification time
        hours, minutes = map(int, notification_time.split(':'))
        
        # Calculate when to send the notification
        now = datetime.datetime.now(pytz.timezone('Europe/Rome'))
        notification_time = now.replace(hour=hours, minute=minutes, second=0, microsecond=0)
        
        # If the time has already passed today, schedule for tomorrow
        if now > notification_time:
            notification_time = notification_time + datetime.timedelta(days=1)
        
        # Calculate seconds until notification
        seconds_until_notification = (notification_time - now).total_seconds()
        
        # Schedule the job
        context.job_queue.run_once(
            send_notification,
            seconds_until_notification,
            data=user_id,
            name="notification"
        )

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

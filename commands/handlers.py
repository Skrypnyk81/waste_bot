import datetime
import logging
import os
import pytz
import telegram
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from config.waste_schedules import WASTE_SCHEDULE, WASTE_INSTRUCTIONS, WASTE_EMOJI, DAY_NAMES, MONTH_NAMES

from db_manager import DatabaseManager
from service.schedule import schedule_tomorrow_notification, get_waste_collection

# Inizializza il database manager
db = DatabaseManager(os.environ.get('DATABASE_URL'))

logger = logging.getLogger(__name__)

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

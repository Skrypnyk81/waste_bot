import datetime
import pytz
import telegram
from telegram.ext import ContextTypes
from config.waste_schedules import WASTE_SCHEDULE, WASTE_EMOJI, DAY_NAMES, MONTH_NAMES
from db_manager import DatabaseManager
import os

# Inizializza il database manager
db = DatabaseManager(os.environ.get('DATABASE_URL'))

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

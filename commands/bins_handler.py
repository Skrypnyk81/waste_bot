from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from db_manager import DatabaseManager
import os

# Inizializza il database manager
db = DatabaseManager(os.environ.get('DATABASE_URL'))

# Stati per la conversazione
MANAGE_BINS, SETTING_LIMIT = range(2)

async def show_bins_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Shows the bins management menu."""
    keyboard = [
        [InlineKeyboardButton("📝 Porti fuori un bidone", callback_data="out_bins")],
        [InlineKeyboardButton("📊 Statistiche", callback_data="bins_show_info")],
        [InlineKeyboardButton("⚙️ Imposta limite", callback_data="bins_set_limit")],
        [InlineKeyboardButton("🔄 Azzera bidoni", callback_data="bins_reset_count")],
        [InlineKeyboardButton("⬅️ Indietro", callback_data="cancel")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message_text = (
        "🗑️ GESTIONE BIDONE DEL SECCO 🗑️\n\n"
        "In questo menu puoi gestire il bidone del secco.\n\n"
        "📝 Puoi segnalare quando porti fuori un bidone\n"
        "📊 Guarda il tuo conteggio attuale e il limite annuale\n"
        "⚙️ Impostare il limite annuale per il numero di bidoni che puoi esporre\n"
        "🔄 Azzerare il conteggio dei bidoni esposti\n"
    )

    if update.callback_query:
        query = update.callback_query
        await query.edit_message_text(
            text=message_text,
            reply_markup=reply_markup
        )
    else:
        await update.message.reply_text(
            text=message_text,
            reply_markup=reply_markup
        )
    
    return MANAGE_BINS

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Gestisce la pressione dei pulsanti della tastiera inline."""
    query = update.callback_query
    await query.answer()  # Notifica Telegram che la query è stata ricevuta

    action = query.data
    user_id = query.from_user.id

    if action == "out_bins":
        user_data = db.get_user(user_id)
        count_bins = user_data.get('count_bins', 0)
        limit_bins = user_data.get('limit_bins', 0) # Prende il limite o 0 se non esiste
        
        new_count = count_bins + 1
        db.update_user(user_id, count_bins=new_count)
        
        # Prepara il testo e i pulsanti in base al valore di limit_bins
        if limit_bins > 0:
            remaining_bins = limit_bins - new_count
            if remaining_bins >= 0:
                message_text = (
                    f"✅ Ottimo! Hai portato fuori {new_count} bidoni. "
                    f"Rimangono {remaining_bins} bidoni per raggiungere il limite di {limit_bins}.\n\n"
                    "Vuoi fare altro?"
                )
            else:
                message_text = (
                    f"⚠️ Attenzione! Hai portato fuori {new_count} bidoni, "
                    f"hai superato il limite di {limit_bins} bidoni.\n\n"
                    "Vuoi fare altro?"
                )
            
            # Mantieni il menu attivo invece di terminare
            keyboard = [
                [InlineKeyboardButton("📝 Porti fuori un bidone", callback_data="out_bins")],
                [InlineKeyboardButton("📊 Statistiche", callback_data="bins_show_info")],
                [InlineKeyboardButton("⚙️ Imposta limite", callback_data="bins_set_limit")],
                [InlineKeyboardButton("🔄 Azzera bidoni", callback_data="bins_reset_count")],
                [InlineKeyboardButton("⬅️ Indietro", callback_data="cancel")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                text=message_text,
                reply_markup=reply_markup
            )
        else:
            # Se il limite non è impostato, mostra il conteggio e suggerisci di impostarlo
            message_text = (
                f"✅ Ottimo! Hai portato fuori {new_count} bidoni. "
                "Il limite annuale non è ancora impostato. Vuoi impostarlo ora?"
            )
            keyboard = [
                [InlineKeyboardButton("⚙️ Imposta limite", callback_data="bins_set_limit")],
                [InlineKeyboardButton("⬅️ Torna al menu", callback_data="bins_back_to_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            # Modifica il messaggio per includere il nuovo testo e il pulsante
            await query.edit_message_text(
                text=message_text,
                reply_markup=reply_markup
            )
        
        return MANAGE_BINS  # Rimane nello stato MANAGE_BINS invece di terminare

    elif action == "bins_set_limit":
        await query.edit_message_text(text="Ok, inviami il nuovo limite numerico per i bidoni.")
        return SETTING_LIMIT # Entra nello stato per ricevere l'input

    elif action == "bins_reset_count":
        db.update_user(user_id, count_bins=0)
        
        # Mostra il messaggio di conferma e mantieni il menu
        message_text = (
            "🔄 Conteggio bidoni azzerato!\n\n"
            "Vuoi fare altro?"
        )
        keyboard = [
            [InlineKeyboardButton("📝 Porti fuori un bidone", callback_data="out_bins")],
            [InlineKeyboardButton("📊 Statistiche", callback_data="bins_show_info")],
            [InlineKeyboardButton("⚙️ Imposta limite", callback_data="bins_set_limit")],
            [InlineKeyboardButton("🔄 Azzera bidoni", callback_data="bins_reset_count")],
            [InlineKeyboardButton("⬅️ Indietro", callback_data="cancel")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=message_text,
            reply_markup=reply_markup
        )
        return MANAGE_BINS
    
    elif action == "bins_show_info":
        user_data = db.get_user(user_id)
        count_bins = user_data.get('count_bins', 0)
        limit_bins = user_data.get('limit_bins', 0)
        
        if limit_bins > 0:
            remaining_bins = limit_bins - count_bins
            info_text = (
                f"📊 **STATISTICHE BIDONI DEL SECCO**\n\n"
                f"🗑️ Bidoni esposti: {count_bins}\n"
                f"📏 Limite annuale: {limit_bins}\n"
                f"📈 Rimanenti: {remaining_bins}\n\n"
                "Questa sezione ti aiuta a tenere traccia di quanti bidoni del secco hai esposto "
                "per rimanere entro il limite annuale previsto dal tuo comune."
            )
        else:
            info_text = (
                f"📊 **STATISTICHE BIDONI DEL SECCO**\n\n"
                f"🗑️ Bidoni esposti: {count_bins}\n"
                f"📏 Limite annuale: Non impostato\n\n"
                "Questa sezione ti aiuta a tenere traccia di quanti bidoni del secco hai esposto "
                "per rimanere entro il limite annuale previsto dal tuo comune."
            )
        
        keyboard = [[InlineKeyboardButton("⬅️ Torna al menu", callback_data="bins_back_to_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text=info_text, reply_markup=reply_markup)
        return MANAGE_BINS

    elif action == "bins_back_to_menu":
        await show_bins_menu(update, context) # Torna al menu principale
        return MANAGE_BINS

    elif action == "cancel":
        # Inline "Indietro" / cancel button pressed – delegate to cancel handler
        return await cancel(update, context)

async def handle_limit_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Gestisce l'input dell'utente per il limite dei bidoni."""
    user_id = update.effective_user.id
    try:
        limit = int(update.message.text)
        if limit > 0:
            db.update_user(user_id, limit_bins=limit)
            await update.message.reply_text(f"✅ Limite impostato a {limit} bidoni.")
        else:
            await update.message.reply_text("Per favore, inserisci un numero intero positivo.")
    except ValueError:
        await update.message.reply_text("Input non valido. Per favore, inserisci un numero.")

    await show_bins_menu(update, context)
    return MANAGE_BINS

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Annulla e termina la conversazione."""
    # Support both message-based calls and callback_query calls
    if getattr(update, 'callback_query', None):
        query = update.callback_query
        try:
            await query.answer()
        except Exception:
            pass
        # edit the original message to show cancellation (removes inline keyboard)
        if query.message:
            await query.edit_message_text('Operazione annullata.')
        else:
            # fallback: send a chat message
            chat = update.effective_chat
            if chat:
                await context.bot.send_message(chat.id, 'Operazione annullata.')
    else:
        # message-based invocation (/cancel)
        if update.message:
            await update.message.reply_text('Operazione annullata.')

    return ConversationHandler.END
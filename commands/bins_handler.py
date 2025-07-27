from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.ext import ContextTypes, ConversationHandler
from db_manager import DatabaseManager
import os

# Inizializza il database manager
db = DatabaseManager(os.environ.get('DATABASE_URL'))

# Stato per la conversazione per impostare il limite
SETTING_LIMIT = 0

async def show_bins_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Mostra o aggiorna il menu interattivo per il tracciamento dei bidoni.
    """
    user = update.effective_user
    
    try:
        user_data = db.get_user(user.id)
        if not user_data:
            await update.message.reply_text(
                "🤔 Utente non trovato.\n"
                "Per favore, usa il comando /start per iniziare."
            )
            return
            
    except Exception as e:
        print(f"Errore nel recuperare i dati per l'utente {user.id}: {e}")
        await update.message.reply_text(
            "⚠️ Si è verificato un errore nel recupero dei tuoi dati. Riprova più tardi."
        )
        return

    count_bins: int = user_data.get('count_bins', 0)
    limit_bins: int = user_data.get('limit_bins') or "non impostato"

    text = (
        f"Ciao *{user.first_name}*! 👋\n\n"
        f"📊 *Stato Tracciamento Bidoni Secco*\n"
        f"Hai portato fuori: `{count_bins}` bidoni\.\n"
        f"Il tuo limite è: `{limit_bins}` bidoni\.\n\n"
        "Scegli un'azione qui sotto:"
    )

    keyboard = [
        [InlineKeyboardButton("➕ Segna un bidone", callback_data="bins_add_one")],
        [
            InlineKeyboardButton("⚙️ Imposta Limite", callback_data="bins_set_limit"),
            InlineKeyboardButton("🔄 Azzera Conteggio", callback_data="bins_reset_count"),
        ],
        [InlineKeyboardButton("ℹ️ Info", callback_data="bins_show_info")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Se la funzione è chiamata da un pulsante (query), modifica il messaggio esistente.
    # Altrimenti, se chiamata da un comando, invia un nuovo messaggio.
    if update.callback_query:
        await update.callback_query.edit_message_text(
            text,
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN_V2
        )
    else:
        await update.message.reply_text(
            text,
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN_V2
        )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Gestisce la pressione dei pulsanti della tastiera inline."""
    query = update.callback_query
    await query.answer()  # Notifica Telegram che la query è stata ricevuta

    action = query.data
    user_id = query.from_user.id

    if action == "bins_add_one":
        user_data = db.get_user(user_id)
        count_bins = user_data.get('count_bins', 0)
        new_count = count_bins + 1
        db.update_user(user_id, count_bins=new_count)
        await query.answer(text=f"✅ Ottimo! Hai portato fuori {new_count} bidoni.", show_alert=True)
        await show_bins_menu(update, context)  # Aggiorna il menu
        return ConversationHandler.END

    elif action == "bins_set_limit":
        await query.edit_message_text(text="Ok, inviami il nuovo limite numerico per i bidoni.")
        return SETTING_LIMIT # Entra nello stato per ricevere l'input

    elif action == "bins_reset_count":
        db.update_user(user_id, count_bins=0)
        await query.answer(text="🔄 Conteggio bidoni azzerato!", show_alert=True)
        await show_bins_menu(update, context)  # Aggiorna il menu
        return ConversationHandler.END
    
    elif action == "bins_show_info":
        info_text = (
            "Questa sezione ti aiuta a tenere traccia di quanti bidoni del secco hai esposto "
            "per rimanere entro il limite annuale previsto dal tuo comune."
        )
        keyboard = [[InlineKeyboardButton("⬅️ Indietro", callback_data="bins_back_to_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text=info_text, reply_markup=reply_markup)
        return ConversationHandler.END

    elif action == "bins_back_to_menu":
        await show_bins_menu(update, context) # Torna al menu principale
        return ConversationHandler.END

async def handle_limit_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Gestisce l'input dell'utente per il limite dei bidoni."""
    user_id = update.effective_user.id
    try:
        limit = int(update.message.text)
        if limit > 0:
            db.update_user(user_id, limit_bins=limit)
            await update.message.reply_text(f"✅ Limite impostato a {limit} bidoni.")
            # Mostra di nuovo il menu aggiornato
            await show_bins_menu(update, context)
        else:
            await update.message.reply_text("Per favore, inserisci un numero intero positivo.")
    except ValueError:
        await update.message.reply_text("Input non valido. Per favore, inserisci un numero.")

    return ConversationHandler.END # Termina la conversazione

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Annulla e termina la conversazione."""
    await update.message.reply_text('Operazione annullata.')
    return ConversationHandler.END
from app.bot.methods import *
from app.bot.states import *
from dotenv import load_dotenv
import os
import logging
import sys
from typing import Final
from telegram import Update
from telegram.ext import ContextTypes, Application, CommandHandler, ConversationHandler, CallbackQueryHandler, MessageHandler, filters
from app.settings import TG_BOT_TOKEN

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

def main() -> None:
    """
    Start the bot
    """
    _app = Application.builder().token(TG_BOT_TOKEN).build()
    
    # handlers
    conv_handler: ConversationHandler = ConversationHandler(
        entry_points=[CommandHandler("daily_blanks", daily_blanks)],
        states={
            0: [MessageHandler(filters=filters.TEXT, callback=receive_days)]
        },
        fallbacks=[MessageHandler(filters=filters.Regex("^Отмена$"), callback=cancel)]
    )
    _app.add_handler(conv_handler)
    
    # _app.add_handler(CommandHandler("daily_blanks", daily_blanks))
    _app.add_handler(CallbackQueryHandler(callback=student_selected, pattern=r"^student_"))
    _app.add_handler(CallbackQueryHandler(callback=reason_selected, pattern=r"^reason_"))
    _app.add_handler(CallbackQueryHandler(callback=show_students, pattern=r"back1show_students"))
    _app.add_handler(CallbackQueryHandler(callback=skipped_count, pattern=r"^all_lessons|specify_count|count_"))
    
    _app.run_polling(allowed_updates=Update.ALL_TYPES)
   
from dotenv import load_dotenv
import os
import logging
from typing import Final
from telegram import Update
from telegram.ext import ContextTypes, Application, CommandHandler, ConversationHandler, CallbackQueryHandler, MessageHandler

from app.app import today, show_students, student_selected, reason_selected
from app.states import *


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


load_dotenv()
TG_BOT_TOKEN: Final[str] = os.getenv('TG_BOT_TOKEN', None)  


def main() -> None:
    """
    Start the bot
    """
    _app = Application.builder().token(TG_BOT_TOKEN).build()
    
    # handlers
    _app.add_handler(CommandHandler("today", today))
    _app.add_handler(CallbackQueryHandler(callback=student_selected, pattern=r"^student_"))
    _app.add_handler(CallbackQueryHandler(callback=reason_selected, pattern=r"^reason_"))
    _app.add_handler(CallbackQueryHandler(callback=show_students, pattern=r"back2show_students"))
    
    _app.run_polling(allowed_updates=Update.ALL_TYPES)
    
if __name__ == "__main__":
    main()
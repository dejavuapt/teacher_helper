from app.app import *
from app.states import *
from dotenv import load_dotenv
import os
import logging
import sys
from typing import Final
from telegram import Update
from telegram.ext import ContextTypes, Application, CommandHandler, ConversationHandler, CallbackQueryHandler, MessageHandler, filters
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent


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
    conv_handler: ConversationHandler = ConversationHandler(
        entry_points=[CommandHandler("daily_blanks", daily_blanks)],
        states={
            1: [MessageHandler(filters=filters.TEXT, callback=receive_days)]
        },
        fallbacks=[MessageHandler(filters=filters.Regex("^Отмена$"), callback=cancel)]
    )
    _app.add_handler(conv_handler)
    
    # _app.add_handler(CommandHandler("daily_blanks", daily_blanks))
    _app.add_handler(CallbackQueryHandler(callback=student_selected, pattern=r"^student_"))
    _app.add_handler(CallbackQueryHandler(callback=reason_selected, pattern=r"^reason_"))
    _app.add_handler(CallbackQueryHandler(callback=show_students, pattern=r"back2show_students"))
    _app.add_handler(CallbackQueryHandler(callback=skipped_count, pattern=r"^all_lessons|specify_count|count_"))
    
    _app.run_polling(allowed_updates=Update.ALL_TYPES)
    
# class FileChangeHandler(FileSystemEventHandler):
#     def __init__(self, callback):
#         self._callback = callback
#         self._restart = False
#     
#     def on_any_event(self, event: FileSystemEvent):
#         if event.is_directory or event.src_path.endswith(".py"):
#             if not self._restart:
#                 logger.info(f"Changed in {event.src_path}. Restart")
#                 self._restart = True
#                 self._callback()
#     
# def watch_docs() -> None:
#     def restart_bot():
#         logger.info("[LOG] Bot restarting")
#         os.execv(sys.executable, ['python3'] + sys.argv)
#     
#     event_handler = FileChangeHandler(restart_bot)
#     observer = Observer()
#     observer.schedule(event_handler, path='.', recursive=True) 
#     observer.start()
#
#     try:
#         main()
#     except KeyboardInterrupt:
#         observer.stop()
#     observer.join()
    
if __name__ == "__main__":
    # watch_docs()
    main()
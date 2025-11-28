from . import callbacks, states
from telegram.ext import (
    CallbackQueryHandler,
    ConversationHandler,
    CommandHandler,
    MessageHandler
)
from telegram.ext import filters


handlers = [
    ConversationHandler(
        entry_points=[CommandHandler("daily_blanks", callbacks.daily_blanks)],
        states={
            states.RECEIVE_DAYS: [MessageHandler(filters.TEXT, callbacks.receive_days)]
        },
        fallbacks=[MessageHandler(filters.Regex("оОтмена"), callbacks.cancel)]
    ),
    CallbackQueryHandler(callbacks.student_selected, r'^student_'),
    CallbackQueryHandler(callbacks.reason_selected, r'reason_'),
    CallbackQueryHandler(callbacks.show_students, r'back1show_students'),
    CallbackQueryHandler(callbacks.skipped_count, r'all_lessons|specify_count|count_'),
]
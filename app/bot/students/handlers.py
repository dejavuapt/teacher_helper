from app.bot.students.callbacks import StudentCallback, EDIT_NAME
from telegram.ext import (
    CommandHandler,
    ConversationHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters
)

handlers = StudentCallback.as_handlers() + [ 
    ConversationHandler(
        entry_points=[CallbackQueryHandler(callback=StudentCallback.edit, pattern=r'student-edit_')],
        states={
            EDIT_NAME: [MessageHandler(filters=filters.TEXT, callback=StudentCallback.name)]
        },
        fallbacks=[]
    )
] 
from app.bot.students.callbacks import StudentCallback, EDIT_NAME
from telegram.ext import (
    CommandHandler,
    ConversationHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters
)

#TODO: Взять и чпокнуть эту херню (если уж есть генератор хендлеров то и на конверсейтион надо бы тоже это накинуть)
#TODO: прикольно было бы сделать в пайпланйне, чтобы проходился по всем файлам и выцеплял todoшки всякие :)
handlers = StudentCallback.as_handlers() + [ 
    ConversationHandler(
        entry_points=[CallbackQueryHandler(callback=StudentCallback.edit, pattern=r'student-edit_'),
                      CallbackQueryHandler(callback=StudentCallback.add, pattern=r'student-add')],
        states={
            EDIT_NAME: [MessageHandler(filters=filters.TEXT, callback=StudentCallback.name)]
        },
        fallbacks=[]
    )
] 
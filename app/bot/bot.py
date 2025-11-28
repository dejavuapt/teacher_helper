import logging
from telegram import Update
from telegram.ext import (
    Application, 
    CommandHandler, 
    ConversationHandler, 
    CallbackQueryHandler, 
    MessageHandler, 
    filters)
from app.bot.methods import (
    daily_blanks, 
    receive_days,
    cancel,
    student_selected,
    reason_selected,
    show_students,
    skipped_count
)
from app.bot._exceptions import NullTokenError


logger = logging.getLogger(__name__)

def init_handlers(app: Application) -> None:
    conv_handler: ConversationHandler = ConversationHandler(
        entry_points=[CommandHandler("daily_blanks", daily_blanks)],
        states={
            0: [MessageHandler(filters=filters.TEXT, callback=receive_days)]
        },
        fallbacks=[MessageHandler(filters=filters.Regex("^Отмена$"), callback=cancel)]
    )
    app.add_handler(conv_handler)
    
    app.add_handler(CallbackQueryHandler(callback=student_selected, pattern=r"^student_"))
    app.add_handler(CallbackQueryHandler(callback=reason_selected, pattern=r"^reason_"))
    app.add_handler(CallbackQueryHandler(callback=show_students, pattern=r"back1show_students"))
    app.add_handler(CallbackQueryHandler(callback=skipped_count, pattern=r"^all_lessons|specify_count|count_"))
 

# TODO: Проверить, будет ли работать через отправку через app. Т.к. вроде
# python не создает копию больших объектов, а передает их по ссылке. Могу ошибаться
def build_run(token: str) -> None:
    if not token:
        raise NullTokenError()
    app: Application = Application.builder().token(token).build()
    init_handlers(app)
    app.run_polling(allowed_updates=Update.ALL_TYPES)
   
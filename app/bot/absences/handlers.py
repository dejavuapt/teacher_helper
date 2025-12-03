from telegram.ext import (
    CallbackQueryHandler,
    ConversationHandler,
    CommandHandler,
    MessageHandler
)
from telegram.ext import filters
from app.bot.absences.callbacks import AbsencesCallbacks, FillAbsencesCallbacks


handlers = AbsencesCallbacks.as_handlers() + FillAbsencesCallbacks.as_handlers() + []
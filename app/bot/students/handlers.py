from . import callbacks
from telegram.ext import (
    CommandHandler,
)

handlers = [
    CommandHandler('students', callbacks.students, has_args=True),
]
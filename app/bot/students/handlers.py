from . import callbacks
from telegram.ext import (
    CommandHandler,
)

handlers = [ 
    
] + callbacks.StudentCallback.as_callbacks()
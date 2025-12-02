# CallbackQueryHandler(callbacks.student_selected, r'^student_'),
from typing import Callable, Final, Any
import functools
import logging
from telegram.ext._handlers.basehandler import BaseHandler
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    MessageHandler, 
    filters
)

l = logging.getLogger(__name__)

QUERY, COMMAND, MESSAGE = range(3)
class bindablemethod:
    def __init__(self, method: Callable, **options) -> None:
        self._method = method
        self._opts = options
        self._instance = None

    def __get__(self, instance: None, owner: type, /) -> Callable:
        if not instance:
            return self.__wrap(owner())
        
        if instance:
            return self.__wrap(instance)

        return self.__wrap(self._instance)        
    
    def __wrap(self, instance: None): 
        @functools.wraps(self._method)
        def call(*args, **kwargs):
            return self._method(instance, *args, **kwargs)
        
        for k, v in self._opts.items():
            setattr(call, k, v)

        return call

class callbacks:
    
    @staticmethod 
    def command(command: str = None):
        def decorator(f: Callable):
            pt = command or f.__name__
            tp = COMMAND
            opts = {
                'command': pt,
                'is_callback': True,
                'type_callback': tp,
            }
            return bindablemethod(f, **opts)
        return decorator

    @staticmethod 
    def query(pattern: str = None):
        def decorator(f: Callable):
            pt = pattern or f.__name__
            type_callback = QUERY
            opts = {
                'pattern': pt,
                'is_callback': True,
                'type_callback': type_callback,
            }
            return bindablemethod(f, **opts)
        return decorator

    @staticmethod 
    def message(filters: Any):
        def decorator(f: Callable):
            if not filters:
                raise ValueError("Please write a filters in qury callback")
            pt = filters
            type_callback = MESSAGE
            opts = {
                'filters': pt,
                'is_callback': True,
                'type_callback': type_callback,
            }
            return bindablemethod(f, **opts)
        return decorator


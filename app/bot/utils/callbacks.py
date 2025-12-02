from typing import Callable, List, Final, Any
from sqlalchemy.orm import Session
from telegram.ext._handlers.basehandler import BaseHandler
from telegram.ext import (
    Application,
    CallbackQueryHandler, CommandHandler, MessageHandler
)
from app.bot._exceptions import NoneDBScope
import abc
import inspect
from app.bot.utils.decorators import QUERY, COMMAND, MESSAGE
import logging

l = logging.getLogger(__name__)


class Base(abc.ABC):
    __CALLBACK_MAP: Final[dict[str, Any]] = {
        QUERY: lambda func: CallbackQueryHandler(callback=func, pattern=getattr(func, 'pattern')),
        COMMAND: lambda func: CommandHandler(callback=func, command=getattr(func, 'command')),
        MESSAGE: lambda func: MessageHandler(callback=func, filters=getattr(func, 'filters'))
    }

    def _get_scope(self, app: Application) -> Callable[..., Session]:
        scope = app.bot_data.get('db', None)
        if not scope:
            raise NoneDBScope()
        return scope

    # TODO: rename to DB_session
    def _get_session(self, app: Application) -> Session:
        return self._get_scope(app)()
    
    @classmethod
    def as_handlers(cls) -> list[BaseHandler]:
        """ Use as [{callbacks}] + {callback}.as_callbacks() """
        callbacks: List[BaseHandler] = []

        for name, value in inspect.getmembers(cls, predicate=inspect.isfunction):
            if hasattr(value, 'is_callback'):
                callbacks.append(cls._callback_mapping(value))
                l.debug(f'{name} is parsed and added to callbacks')

        return callbacks        

    @classmethod
    def _callback_mapping(cls, callback_f: Callable) -> BaseHandler:
        callback_type: int = getattr(callback_f, 'type_callback')
        if not callback_type:
            pass

        handler_lambda = cls.__CALLBACK_MAP.get(callback_type)
        if not handler_lambda:
            pass
        return handler_lambda(callback_f) 
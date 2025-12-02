# CallbackQueryHandler(callbacks.student_selected, r'^student_'),
from typing import Callable
import functools
import logging

l = logging.getLogger(__name__)

QUERY, COMMAND = range(2)
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
            opts = {
                'command': pt,
                'is_callback': True,
                'type_callback': COMMAND,
            }
            return bindablemethod(f, **opts)
        return decorator

    @staticmethod 
    def query(pattern: str = None):
        def decorator(f: Callable):
            pt = pattern or f.__name__
            opts = {
                'pattern': pt,
                'is_callback': True,
                'type_callback': QUERY,
            }
            return bindablemethod(f, **opts)
        return decorator

    
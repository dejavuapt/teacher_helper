import logging
from telegram import Update
from telegram.ext import Application 
from app.bot._exceptions import NullTokenError

logger = logging.getLogger(__name__)

def discover_handlers() -> list:
    from pathlib import Path
    import importlib

    handlers = []
    base_path = Path('app')
    for handler_file in base_path.rglob('handlers.py'):
        module_path = str(handler_file).replace('/', '.').replace('.py', '')
        try:
            module = importlib.import_module(module_path)
            if hasattr(module, 'handlers'):
                handlers.extend(module.handlers)
                logger.debug(f"Loaded handlers from {module_path}.")
        except Exception as e:
            logger.error(str(e))
    return handlers

def init_handlers(app: Application) -> None:
    for handler in discover_handlers():
        app.add_handler(handler)

def build_run(token: str) -> None:
    if not token:
        raise NullTokenError()
    app: Application = Application.builder().token(token).build()
    init_handlers(app)
    app.run_polling(allowed_updates=Update.ALL_TYPES)
   
import logging
from telegram import Update
from telegram.ext import Application 
from app.db import init_db

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
    try:
        db_scope = init_db()        
        app: Application = Application.builder().token(token).build()
        app.bot_data['db'] = db_scope
        
        init_handlers(app)

    except Exception as e:
        logger.error(str(e))
        return
    
    app.run_polling(allowed_updates=Update.ALL_TYPES)
   
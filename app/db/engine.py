from app.settings import DATABASE_CONFIG
import sqlalchemy
import sqlalchemy.orm
from typing import Callable, Generator, Any
import logging
from contextlib import contextmanager
from app.db.base import Base

logger = logging.getLogger(__name__)


def import_models() -> None:
    from pathlib import Path
    import importlib

    base_path = Path('app')
    for models_file in base_path.rglob('models.py'):
        module_path = str(models_file).replace('/', '.').replace('.py', '')
        try:
            importlib.import_module(module_path)
            logger.debug(f'Loaded models from {module_path}')
        except Exception as e:
            logger.error(str(e))

def init_db() -> Callable[... , Generator[sqlalchemy.orm.Session, Any, None]]:
    try:
        engine = sqlalchemy.engine_from_config(DATABASE_CONFIG, prefix='db.')
        import_models()
        Base.metadata.create_all(engine)
        Session = sqlalchemy.orm.sessionmaker(bind=engine)
        
        @contextmanager
        def session_scope():
            s = Session()
            try:
                yield s
                s.commit()
            except OSError as e:
                s.rollback()
                logger.error(str(e))
                raise
            finally:
                s.close()
        
        return session_scope
    except Exception as e:
        logger.error(str(e))
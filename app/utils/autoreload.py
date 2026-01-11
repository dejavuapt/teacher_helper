from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent
import sys, os, logging
from typing import Callable
from app.utils import net   
from app.settings import DEBUG, DEBUG_ARGV


# FIXME: Выглядит стремно, по мне стоит это либо вынести в cli либо в debugging вернуть эту же тему
if DEBUG:
    from app.settings import DEBUG_PORT, DEBUG_HOST

logger = logging.getLogger(__name__)

class FileChangeHandler(FileSystemEventHandler):
    def __init__(self, callback):
        self._callback = callback
        self._restart = False
    
    def on_modified(self, event: FileSystemEvent):
        if event.src_path.endswith(".py") and not event.src_path.__contains__('.venv'):
            if not self._restart:
                logger.debug(f"{event.src_path} has been updated. Restarting bot to apply changes...")
                self._restart = True 
                self._callback()

def observer_changes(entry_func: Callable, **kwargs) -> None:
    def on_change_file_callback():
        if DEBUG and net.is_port_connectable(DEBUG_HOST, int(DEBUG_PORT)):
            net.kill_process_linux(int(DEBUG_PORT))
        os.execv(DEBUG_ARGV[0], DEBUG_ARGV[:])

    event_handler = FileChangeHandler(on_change_file_callback)
    observer = Observer()
    observer.schedule(event_handler, path='.', recursive=True) 
    observer.start()

    try:
        entry_func(**kwargs)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
    

autoreload = observer_changes
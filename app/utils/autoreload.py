from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent
import sys, os, logging
from typing import Callable

logger = logging.getLogger(__name__)

class FileChangeHandler(FileSystemEventHandler):
    def __init__(self, callback):
        self._callback = callback
        self._restart = False
    
    def on_any_event(self, event: FileSystemEvent):
        if event.is_directory or event.src_path.endswith(".py"):
            if not self._restart:
                logger.debug(f"Changes in {event.src_path}. Restart!")
                self._restart = True
                self._callback()
    
def observer_changes(entry_func: Callable) -> None:
    def on_change_file_callback():
        os.execv(sys.argv[0], sys.argv[:])


    event_handler = FileChangeHandler(on_change_file_callback)
    observer = Observer()
    observer.schedule(event_handler, path='.', recursive=True) 
    observer.start()

    try:
        entry_func()
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
    

autoreload = observer_changes
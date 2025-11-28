from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent
import sys, os, logging

logger = logging.basicConfig(__name__)

class FileChangeHandler(FileSystemEventHandler):
    def __init__(self, callback):
        self._callback = callback
        self._restart = False
    
    def on_any_event(self, event: FileSystemEvent):
        if event.is_directory or event.src_path.endswith(".py"):
            if not self._restart:
                logger.info(f"Changed in {event.src_path}. Restart")
                self._restart = True
                self._callback()
    
def watch_docs() -> None:
    def restart_bot():
        logger.info("[LOG] Bot restarting")
        os.execv(sys.executable, ['python3'] + sys.argv)
    
    event_handler = FileChangeHandler(restart_bot)
    observer = Observer()
    observer.schedule(event_handler, path='.', recursive=True) 
    observer.start()

    # TODO: Переписать это
    # try:
    #     main()
    # except KeyboardInterrupt:
    #     observer.stop()
    observer.join()
    

autoreload = lambda x: x
import logging

class ColorFormatter(logging.Formatter):
    COLORS = {
        'DEBUG': '\033[1m\033[94m',      # BRIGHT_BLUE
        'INFO': '\033[1m\033[96m',       # BRIGHT_CYAN  
        'WARNING': '\033[1m\033[93m',    # BRIGHT_YELLOW
        'ERROR': '\033[1m\033[91m',      # BRIGHT_RED
        'CRITICAL': '\033[1m\033[101m',   # BRIGHT_RED_BG
    }
    RESET = '\033[0m'
    LEVEL_WIDTH = 8
    
    def format(self, record):
        levelname = f"{record.levelname:<{self.LEVEL_WIDTH}}".lower()
        if record.levelname in self.COLORS:
            levelname = f"{self.COLORS[record.levelname]}{levelname}{self.RESET}"
            
        record.levelname = levelname
        return super().format(record)
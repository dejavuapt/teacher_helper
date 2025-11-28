from os import getenv, path
import dotenv

dotenv.load_dotenv(path.join('..', '.env'))


PROD: bool = getenv("IS_PROD", 0)
TG_BOT_TOKEN: str = getenv("TG_BOT_TOKEN", '')
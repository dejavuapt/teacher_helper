from typing import Dict, Any
from . import ru

LOCALES: Dict[str, Dict[str, any]] = {
    "ru": ru.TEXTS,
}

def get_text(key: str , lang: str = 'ru', **kwargs) -> str:
    if not lang:
        lang = 'ru' 
    val = LOCALES.get(lang, {})
    keys = key.split('.')
    for k in keys:
        if isinstance(val, Dict):
            val = val.get(k)
            if val is None:
                return f'[{key}]'

    if isinstance(val, str) and kwargs:
        try:
            return val.format(**kwargs)
        except KeyError:
            return val
        
    return str(val) if val else f"[{key}]"



            
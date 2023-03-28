## src/logger_ansi_codes.py

```python
ATTRIBUTES = {
    "bold": 1,
    "dark": 2,
    "underline": 4,
    "blink": 5,
    "reverse": 7,
    "concealed": 8,
}


HIGHLIGHTS = {
    "on_black": 40,
    "on_grey": 40,
    "on_red": 41,
    "on_green": 42,
    "on_yellow": 43,
    "on_blue": 44,
    "on_magenta": 45,
    "on_cyan": 46,
    "on_light_grey": 47,
    "on_dark_grey": 100,
    "on_light_red": 101,
    "on_light_green": 102,
    "on_light_yellow": 103,
    "on_light_blue": 104,
    "on_light_magenta": 105,
    "on_light_cyan": 106,
    "on_white": 107,
}

COLORS = {
    "black": 30,
    "grey": 30, 
    "red": 31,
    "green": 32,
    "yellow": 33,
    "blue": 34,
    "magenta": 35,
    "cyan": 36,
    "light_grey": 37,
    "dark_grey": 90,
    "light_red": 91,
    "light_green": 92,
    "light_yellow": 93,
    "light_blue": 94,
    "light_magenta": 95,
    "light_cyan": 96,
    "white": 97,
}

RESET = "\033[0m"
```

## src/custom_logger.py

```python
import logging
import sys
import os
from logging.handlers import RotatingFileHandler
from typing import Iterable, Union
import coloredlogs
from colorama import Fore, Style
from src.my_logger.logger_ansi_codes import ATTRIBUTES, COLORS, HIGHLIGHTS, RESET

def colored(
    text: str,
    color: Union[str, None] = None,
    on_color: Union[str, None] = None,
    attrs: Union[Iterable[str], None] = None,
) -> str:
    if text == "": return " "
    fmt_str = "\033[%dm%s"
    if color is not None:
        text = fmt_str % (COLORS[color], text)

    if on_color is not None:
        text = fmt_str % (HIGHLIGHTS[on_color], text)

    if attrs is not None:
        for attr in attrs:
            text = fmt_str % (ATTRIBUTES[attr], text)

    return text + RESET

class CustomFormatter(coloredlogs.ColoredFormatter):
    FORMATS = {
        logging.DEBUG: (f"[\033[1m%(asctime)s] [%(levelname)s{RESET}]\u001b[4m%(audit_path)s\u001b[0m%(message)s", {}),
        logging.INFO: (f"[\033[1m%(asctime)s] [%(levelname)s{RESET}]\u001b[4m%(audit_path)s\u001b[0m%(message)s", {}),
        logging.WARNING: (f"[\033[1m%(asctime)s] [%(levelname)s{RESET}]\u001b[4m%(audit_path)s\u001b[0m%(message)s", {}),
        logging.ERROR: (f"[\033[1m%(asctime)s] [%(levelname)s{RESET}]\u001b[4m%(audit_path)s\u001b[0m%(message)s", {}),
        logging.CRITICAL: (f"[\033[1m%(asctime)s] [%(levelname)s{RESET}]\u001b[4m%(audit_path)s\u001b[0m%(message)s", {})
    }

    COLOR_MAP = {
        logging.DEBUG: "cyan",
        logging.INFO: "green",
        logging.WARNING:"yellow",
        logging.ERROR: "red",
        logging.CRITICAL: "magenta",
    }

    def get_audit(self, record):
        try:
            return f"{record.audit_filename}:{record.audit_lineno}"
        except:
            return ""

    def format(self, record):
        fmt, kwargs = self.FORMATS.get(record.levelno)
        record.levelname = colored(record.levelname, color=self.COLOR_MAP.get(record.levelno))
        record.audit_path = colored(self.get_audit(record), color=self.COLOR_MAP.get(record.levelno), attrs=['underline'])
        if fmt:
            self._fmt = fmt
            self._style = logging.PercentStyle(fmt)
        if record.audit_path != "":
            record.audit_path = f" [{record.audit_path}] "

        return super().format(record, **kwargs)

class CustomLogger:

    @staticmethod
    def setup_custom_logging(logfile=None):
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)

        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.DEBUG)

        formatter = CustomFormatter()
        ch.setFormatter(formatter)

        logger.addHandler(ch)

        if logfile:
            fh = RotatingFileHandler(logfile, maxBytes=10*1024*1024, backupCount=5)
            fh.setLevel(logging.DEBUG)
            fh.setFormatter(formatter)
            logger.addHandler(fh)
```

## src/audit_decorators.py

```python
import logging
import functools
import asyncio
import os

logger = logging.getLogger(__name__)

class AuditBase:
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        for name, method in cls.__dict__.items():
            if callable(method):
                if asyncio.iscoroutinefunction(method):
                    setattr(cls, name, audit_async(method))
                else:
                    if name == "__init__":
                        cls = audit_init(cls)
                    else:
                        setattr(cls, name, audit(method))

def audit_init(cls):
    original_init = cls.__init__

    @functools.wraps(original_init)
    def wrapper(self, *args, **kwargs):
        logger.debug(f"{cls.__name__}.__init__ called with args: {args}, kwargs: {kwargs}")
        original_init(self, *args, **kwargs)

    cls.__init__ = wrapper
    return cls

def get_extra(func):
    audit_func_path = f"{func.__module__}.{func.__qualname__}"
    audit_filename = os.path.basename(func.__code__.co_filename)  
    audit_lineno = func.__code__.co_firstlineno  
    extra={"audit_func_path": audit_func_path, "audit_filename": audit_filename, "audit_lineno": audit_lineno}
    return extra

def audit(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            extra = get_extra(func)
            logger.debug(f"Called with args: {args}, kwargs: {kwargs}", extra=extra)
            result = func(*args, **kwargs)
            logger.debug(f"Returned: {result}", extra=extra)
            return result
        except Exception as e:
            logger.exception(f"Exception in {func.__module__}.{func.__qualname__}: {e}")
            raise

    return wrapper

def audit_async(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            extra = get_extra(func)
            logger.debug(f"{func.__module__}.{func.__qualname__} called with args: {args}, kwargs: {kwargs}", extra=extra)
            result = await func(*args, **kwargs)
            logger.debug(f"{func.__module__}.{func.__qualname__} returned: {result}", extra=extra)
            return result
        except Exception as e:
            logger.exception(f"Exception in {func.__module__}.{func.__qualname__}: {e}")
            raise

    return wrapper

def audit_async_task(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            extra = get_extra(func)
            logger.debug(f"{func.__module__}.{func.__qualname__} called with args: {args}, kwargs: {kwargs}", extra=extra)
            result = await asyncio.create_task(func(*args, **kwargs))
            logger.debug(f"{func.__module__}.{func.__qualname__} returned: {result}")
            return result
        except Exception as e:
            logger.exception(f"Exception in {func.__module__}.{func.__qualname__}: {e}", extra=extra)
            raise

    return wrapper
```

## src/setup.py

```python
from setuptools import setup, find_packages

setup(
    name="logcleanaudit",
    version="0.1.0",
    description="A simple and efficient decorator-based package for auditing and debugging Python programs",
    author="8ByteSword",
    author_email="8bytesword@gmail.com",
    url="https://github.com/8bytesword/logcleanaudit",
    packages=find_packages(),
    install_requires=[
        "coloredlogs",
        "colorama"
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
)
```

## src/__init__.py

```python
from .custom_logger import CustomLogger
from .audit_decorators import audit, audit_async, audit_async_task
```


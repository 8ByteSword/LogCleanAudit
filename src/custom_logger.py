import logging
import sys
from logging.handlers import RotatingFileHandler
from typing import Dict, Iterable, Tuple, Union
import coloredlogs
import json
from logger_ansi_codes import ATTRIBUTES, COLORS, HIGHLIGHTS, RESET
from logging_loki import LokiHandler


def colored(
    text: str,
    color: Union[str, None] = None,
    on_color: Union[str, None] = None,
    attrs: Union[Iterable[str], None] = None,
) -> str:
    if not text:
        return " "
    fmt_str = "\033[%dm%s"
    if color:
        text = fmt_str % (COLORS[color], text)

    if on_color:
        text = fmt_str % (HIGHLIGHTS[on_color], text)

    if attrs:
        for attr in attrs:
            text = fmt_str % (ATTRIBUTES[attr], text)

    return text + RESET


class CustomFormatter(logging.Formatter):
    def __init__(self, *args, output_format="colored", level_formats=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.output_format = output_format
        self.level_formats = level_formats or {}
        
    FORMATS: Dict[int, Tuple[str, Dict]] = {
        logging.DEBUG: (f"[{{asctime}}] [{{levelname}}{RESET}]\u001b[4m{{audit_path}}\u001b[0m{{message}}", {}),
        logging.INFO: (f"[{{asctime}}] [{{levelname}}{RESET}]\u001b[4m{{audit_path}}\u001b[0m{{message}}", {}),
        logging.WARNING: (f"[{{asctime}}] [{{levelname}}{RESET}]\u001b[4m{{audit_path}}\u001b[0m{{message}}", {}),
        logging.ERROR: (f"[{{asctime}}] [{{levelname}}{RESET}]\u001b[4m{{audit_path}}\u001b[0m{{message}}", {}),
        logging.CRITICAL: (f"[{{asctime}}] [{{levelname}}{RESET}]\u001b[4m{{audit_path}}\u001b[0m{{message}}", {})
    }
    
    COLOR_MAP = {
        logging.DEBUG: "cyan",
        logging.INFO: "green",
        logging.WARNING:"yellow",
        logging.ERROR: "red",
        logging.CRITICAL: "magenta",
    }

    def format(self, record):
        if self.output_format == "colored":
            fmt = self.level_formats.get(record.levelno, "[%(asctime)s] [%(levelname_color)s] [%(audit_path)s]%(message)s")
            self._fmt = fmt
            self._style = logging.PercentStyle(fmt)

            record.levelname_color = colored(record.levelname, color=self.COLOR_MAP.get(record.levelno))
            record.audit_path = colored(getattr(record, 'audit_func_path', ''), color=self.COLOR_MAP.get(record.levelno), attrs=['underline'])

            return super().format(record)
        elif self.output_format == "json":
            log_data = {
                "timestamp": self.formatTime(record),
                "level": record.levelname,
                "message": record.getMessage(),
                "audit_path": getattr(record, "audit_path", ""),
            }
            return json.dumps(log_data)

class CustomLogger:
    @staticmethod
    def setup_custom_logging(logfile=None, output_format="colored", level_formats=None, logger_name=None, loki=None):
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.DEBUG)

        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.DEBUG)

        formatter = CustomFormatter(output_format=output_format, level_formats=level_formats)
        
        ch.setFormatter(formatter)

        logger.addHandler(ch)

        if logfile:
            fh = RotatingFileHandler(logfile, maxBytes=10*1024*1024, backupCount=5)
            fh.setLevel(logging.DEBUG)
            fh.setFormatter(formatter)
            logger.addHandler(fh)
        if loki is not None:
            json_formatter = CustomFormatter(output_format="json", level_formats=level_formats)
            handler = LokiHandler(
                url="http://localhost:3100/loki/api/v1/push", 
                tags={"application": "test"},
                auth=("admin", "admin"),
                version="1",
            )
            handler.setLevel(logging.DEBUG)
            handler.setFormatter(json_formatter)
            logger.addHandler(handler)


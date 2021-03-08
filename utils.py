from datetime import datetime, date, time, timedelta, timezone
import logging
from logging.handlers import SysLogHandler
from pydantic import BaseModel
from typing import List, Dict, Any, Union


def create_logger(
    name,
    level="info",
    fmt="%(asctime)s %(levelname)s %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    add_console_handler=True,
    add_sys_handler=True,
):
    """Create a formatted logger
    Args:
        fmt: Format of the log message
        datefmt: Datetime format of the log message
    Examples:
        logger = create_logger(__name__, level="info")
        logger.info("Hello world")
    """

    level = {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warn": logging.WARN,
        "error": logging.ERROR,
    }[level]

    logger = logging.getLogger(name)
    logger.setLevel(level)

    if add_console_handler:  # Output to stdout
        ch = logging.StreamHandler()
        ch.setLevel(level)
        chformatter = logging.Formatter(fmt=fmt, datefmt=datefmt)
        ch.setFormatter(chformatter)
        logger.addHandler(ch)

    if add_sys_handler:  # Output to syslog
        sh = SysLogHandler("/dev/log")
    # add syslog format to the handler
    formatter = logging.Formatter(
        fmt='Python: { "loggerName":"%(name)s", "timestamp":"%(asctime)s", "pathName":"%(pathname)s", '
        '"logRecordCreationTime":"%(created)f", "functionName":"%(funcName)s", "levelNo":"%(levelno)s"'
        ', "lineNo":"%(lineno)d", "time":"%(msecs)d", "levelName":"%(levelname)s", "message":"%(message)s"}',
        datefmt=datefmt,
    )
    sh.formatter = formatter
    logger.addHandler(sh)
    return logger


def serializable(input: Any) -> Union[List, Dict, str, int, float, bool, None]:
    """Warning: the returned object will be a combination of list and dict or
    basic data types: str, int, float, bool.  Class objects will be represented
    as dict
    """
    if input is None:
        return None
    if isinstance(input, (str, int, float, bool)):
        return input
    if isinstance(input, datetime):
        return input.strftime("%Y-%m-%d %H:%M:%S")
    if isinstance(input, date):
        return input.strftime("%Y-%m-%d")
    if isinstance(input, time):
        return input.strftime("%H:%M:%S")
    if isinstance(input, (timedelta, timezone)):
        return str(input)
    if isinstance(input, List):
        output = []
        for item in input:
            output.append(serializable(item))
        return output
    if isinstance(input, Dict):
        output = {}
        for k, v in input.items():
            output[k] = serializable(v)
        return output
    if isinstance(input, BaseModel):
        return input.dict()
    # For any other objects, if it has __dict__ attribute, then serialize
    try:
        return serializable(input.__dict__)
    except (AttributeError, SyntaxError):
        try:
            return str(input)
        except Exception:
            pass


def ifnone(a: Any, b: Any) -> Any:
    """`a` if `a` is not None, otherwise `b`."""
    return b if a is None else a

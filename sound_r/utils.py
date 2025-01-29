from __future__ import annotations

import argparse
import json
import logging
import pathlib
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Optional

from .sounds import types

TIME_FORMAT = "%H:%M:%S"

logger = None


def load_map(map_path: pathlib.Path):
    with map_path.open() as f:
        OBJECT_MAP: types.ObjectMap = json.load(f)
        OBJECT_MAP["root"] = map_path.parent


def parse_time_field(time_str: str):
    datetime_ = datetime.strptime(time_str, TIME_FORMAT)
    return datetime_.time()


default_log_level = logging.DEBUG


def get_log_level(level) -> int:
    """
    Returns the log level (int) for the given string or int.
    PARAMETERS
    ----------
    level
        The log level as either a string or an int.

    RETURNS
    -------
    -
        The log level as an int.
    """
    if isinstance(level, int):
        return level
    try:
        level = level.upper()
    except AttributeError:
        raise ValueError(
            f"level={level}\nlevel must be of type int or str. "
            f"{type(level)} given instead."
        )
    return logging.getLevelName(level)


def read_level_from_args() -> int:
    """
    Called when a module wants to get log level using arguments.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--log", default="INFO", type=str)
    args, _ = parser.parse_known_args()
    log_level = args.log
    numeric_level = get_log_level(log_level)
    if not isinstance(numeric_level, int):
        raise ValueError(f"Invalid log level: {log_level}")
    return numeric_level


def get_default_logger(
    name: str,
    format_: str = "[%(asctime)s] [%(name)s]: " "[%(levelname)s] %(message)s",
    filepath: Optional[str] = "./output.log",
    date_format: str = "%m-%d-%Y %H:%M:%S",
    truncate_name: bool = True,
) -> logging.Logger:
    """
    Using the provided arguments, gets an instance of a logger of the given
    name and sets it up.

    PARAMETERS
    ----------
    name
        The name of the module or component this logger is for.
    format_
        The format the messages should follow. See `format_`.
    filepath
        The path to the file to write the logs to. Set to None to not have a
        log file.
    date_format
        The format for the date in the logs.
    truncate_name
        Whether to truncate the name to the last phrase after the last '.'
        character.

    RETURNS
    -------
    -
        Returns the logger.
    """
    if logger:
        logger.info("Creating a logger for %s.", name)
    formatter = logging.Formatter(format_, datefmt=date_format)

    logger_ = logging.getLogger(name.split(".")[-1] if truncate_name else name)
    logger_.setLevel(default_log_level)

    ch = logging.StreamHandler()
    ch.setLevel(default_log_level)
    ch.setFormatter(formatter)
    logger_.addHandler(ch)

    if filepath is not None:
        fh = logging.FileHandler(filepath)
        fh.setLevel(logging.INFO)
        fh.setFormatter(formatter)
        logger_.addHandler(fh)
    if logger:
        logger.info("Logger created for %s.", name)

    return logger_


logger = get_default_logger(__name__, filepath=None)
logger.setLevel(logging.ERROR)

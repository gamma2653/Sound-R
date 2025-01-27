from __future__ import annotations

import argparse
import logging
import subprocess
import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import NoReturn, Optional


logger = None


def install_ffmpeg() -> int:
    install_shell = subprocess.Popen(
        "winget install --id Gyan.FFmpeg --source winget",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    stdout, stderr = install_shell.communicate()
    print(f"Out: {stdout}")
    print(f"Err: {stderr}")
    return install_shell.returncode


def prompt_install_ffmpeg() -> int:
    userin = input("FFmpeg not detected, install? [Y/n]")
    if userin.lower() == "y" or not userin:
        return install_ffmpeg()
    return 0


def ensure_ffmpeg(no_interaction: bool = False) -> NoReturn | None:
    # Check if ffmpeg is installed:
    try:
        subprocess.Popen(
            "ffmpeg -version",
        )
    except FileNotFoundError:
        # error, no ffmpeg
        return (
            sys.exit(install_ffmpeg())
            if no_interaction
            else sys.exit(prompt_install_ffmpeg())
        )


default_log_level = logging.WARNING


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

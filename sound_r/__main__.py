from __future__ import annotations

import argparse
import json
import os
import pathlib
import sys

from PySide6 import QtGui, QtWidgets

from .gui.app import MainWindow
from .sounds import types
from .utils import get_default_logger

logger = get_default_logger(__name__)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--data_map",
        "-dm",
        action="store",
        default=str(pathlib.Path(os.getcwd(), ".cache")),
    )
    known_args, _ = parser.parse_known_args()
    DATA_FOLDER = known_args.data_map
    DATA_PATH = pathlib.Path(DATA_FOLDER)
    MAP_PATH = DATA_PATH / "map.json"
    with MAP_PATH.open() as f:
        OBJECT_MAP: types.ObjectMap = json.load(f)
        OBJECT_MAP["root"] = MAP_PATH.parent

    app = QtWidgets.QApplication(sys.argv)
    icon = QtGui.QIcon(
        str(pathlib.Path(__file__).parent / "gui" / "assets" / "d20.png")
    )
    app.setWindowIcon(icon)

    window = MainWindow(OBJECT_MAP)
    window.start()
    sys.exit(app.exec())

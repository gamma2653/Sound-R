from __future__ import annotations

import os
from typing import TYPE_CHECKING

os.environ["QT_MULTIMEDIA_PREFERRED_PLUGINS"] = "windowsmediafoundation"
from PySide6 import QtWidgets

from ..sounds import types
from ..sounds.sound_engine import SoundEngine
from ..utils import get_default_logger

if TYPE_CHECKING:
    from typing import Optional

logger = get_default_logger(__name__)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(
        self,
        data_map: types.ObjectMap,
        parent: Optional[QtWidgets.QWidget] = None,
        starting_id: str = "start",
    ):
        logger.info("Initializing MainWindow")
        super().__init__(parent)
        self.setWindowTitle("D&D Sound-R")
        self.sound_engine = SoundEngine(starting_id=starting_id, data_map=data_map)
        self.step_btn = QtWidgets.QPushButton(text="Step")
        self.step_btn.clicked.connect(self.sound_engine.step)

        central_widget = QtWidgets.QWidget(self)

        layout = QtWidgets.QHBoxLayout(central_widget)
        central_widget.setLayout(layout)

        self.setCentralWidget(central_widget)
        layout.addWidget(self.step_btn)
        logger.debug("MainWindow initialized")

    def start(self):
        logger.info("Starting MainWindow")
        self.showMaximized()
        self.sound_engine.start()
        logger.info("MainWindow started")

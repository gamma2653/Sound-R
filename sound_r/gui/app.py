from __future__ import annotations

import logging
import os
from typing import TYPE_CHECKING

os.environ["QT_MULTIMEDIA_PREFERRED_PLUGINS"] = "windowsmediafoundation"
from PySide6 import QtWidgets

from ..sounds import types
from ..sounds.sound_engine import SoundEngine, SoundPlayer
from ..utils import get_default_logger

if TYPE_CHECKING:
    from typing import Optional

logger = get_default_logger(__name__)


class MainWindowLogHandler(logging.Handler):

    def __init__(self, parent: MainWindow):
        super().__init__()
        self.parent = parent

    def emit(self, record):
        msg = self.format(record)
        self.parent.status_box.append(msg)


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
        self.sound_engine = SoundEngine(
            starting_id=starting_id, data_map=data_map, parent=self
        )
        # logger.addHandler(QtLogHandler(self))

        central_widget = QtWidgets.QWidget(self)
        layout = QtWidgets.QHBoxLayout(central_widget)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        self.actions_panel = QtWidgets.QWidget(self)
        actions_layout = QtWidgets.QVBoxLayout(self.actions_panel)
        self.actions_panel.setLayout(actions_layout)

        self.step_btn = QtWidgets.QPushButton(text="Step")
        self.step_btn.clicked.connect(self.step)

        self.status_panel = QtWidgets.QWidget(self)
        status_layout = QtWidgets.QVBoxLayout(self.status_panel)
        self.status_panel.setLayout(status_layout)
        self.status_box = QtWidgets.QTextEdit(self)
        self.status_box.setReadOnly(True)
        self.sound_engine.sound_looped.connect(
            lambda scene_sound: self.status_box.append(
                f"Looped [{scene_sound[0]}: {scene_sound[1]}]"
            )
        )

        actions_layout.addWidget(self.step_btn)
        status_layout.addWidget(self.status_box)
        layout.addWidget(self.status_panel)
        layout.addWidget(self.actions_panel)
        logger.debug("MainWindow initialized")

    def start(self):
        logger.info("Starting MainWindow")
        self.showMaximized()
        self.sound_engine.start()
        scene_id, sound_id = self.sound_engine.get_scene_and_sound()
        self.status_box.append(f"Starting [{scene_id}: {sound_id}]")
        logger.info("MainWindow started")

    def step(self):
        scene_id, sound_id = self.sound_engine.get_scene_and_sound()
        self.sound_engine.step()
        new_scene_id, new_sound_id = self.sound_engine.get_scene_and_sound()
        self.status_box.append(
            f"[{sound_id}: {scene_id}] -> [{new_sound_id}: {new_scene_id}]"
        )

    def add_sound_playing(self, sound_id: str):
        pass

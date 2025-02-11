from __future__ import annotations

import logging
import os
from typing import TYPE_CHECKING

os.environ["QT_MULTIMEDIA_PREFERRED_PLUGINS"] = "windowsmediafoundation"
from PySide6 import QtCore, QtGui, QtWidgets

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


class ImageView(QtWidgets.QLabel):
    def __init__(
        self,
        parent: Optional[QtWidgets.QWidget] = None,
        img: Optional[QtGui.QImage] = None,
    ):
        super().__init__(parent)
        # self.setScaledContents(True)
        self.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        if img:
            self.set_image(img)

    def set_image(self, img: QtGui.QImage):
        self.setPixmap(QtGui.QPixmap.fromImage(img))

    def load_image(self, img_path: str):
        img = QtGui.QImage(img_path)
        self.set_image(img)


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
        # Primary setup
        self.sound_engine = SoundEngine(
            starting_id=starting_id, data_map=data_map, parent=self
        )
        central_widget = QtWidgets.QWidget(self)
        layout = QtWidgets.QHBoxLayout(central_widget)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # Art panel
        self.art_panel = QtWidgets.QWidget(self)
        art_layout = QtWidgets.QVBoxLayout(self.art_panel)
        self.art_panel.setLayout(art_layout)
        self.art_image = ImageView(self.art_panel)
        art_layout.addWidget(self.art_image)

        # Actions panel
        self.actions_panel = QtWidgets.QWidget(self)
        actions_layout = QtWidgets.QVBoxLayout(self.actions_panel)
        self.actions_panel.setLayout(actions_layout)

        self.step_btn = QtWidgets.QPushButton(text="Step")
        self.step_btn.clicked.connect(self.step)

        # Status panel
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
        self.sound_engine.clear_loop.connect(
            lambda: self.sound_engine.sound_looped.disconnect()
        )
        self.sound_engine.select_image.connect(self.display_image)

        actions_layout.addWidget(self.step_btn)
        status_layout.addWidget(self.status_box)
        layout.addWidget(self.art_panel)
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

    def display_image(self, art_id: str, scale: float):
        logger.debug(f"Displaying image: {art_id}")
        try:
            sound_path = (
                self.sound_engine.art_path.resolve(strict=True)
                / self.sound_engine.data_map["artIDs"][art_id]
            )
            print(art_id)
            image = QtGui.QImage(sound_path)
            if scale != 1.0:
                print(image.width(), image.height())
                image = image.scaled(image.width() * scale, image.height() * scale)
                print(image.width(), image.height())
            print(image)
            self.art_image.set_image(image)
            self.art_image.show()
            # self.art_image.setStyleSheet("border: 1px solid black;")
        except FileNotFoundError:
            logger.error(f"Image not found: {art_id}")
            self.status_box.append(f"Image not found: {art_id}")

    def add_sound_playing(self, sound_id: str):
        pass

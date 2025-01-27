from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6 import QtCore, QtGui, QtWidgets

from ..sounds import types
from ..sounds.sound_engine import SoundEngine

if TYPE_CHECKING:
    from typing import Optional


class MainWindow(QtWidgets.QMainWindow):
    def __init__(
        self,
        data_map: types.ObjectMap,
        parent: Optional[QtWidgets.QWidget] = None,
        starting_id: str = "start",
    ):
        super().__init__(parent)
        self.setWindowTitle("D&D Sound-R")
        self.sound_engine = SoundEngine(starting_id=starting_id, data_map=data_map)
        self.step_btn = QtWidgets.QPushButton(text="Step")
        self.step_btn.clicked.connect(self.sound_engine.step)

        central_widget = QtWidgets.QWidget(self)

        layout = QtWidgets.QHBoxLayout(self)
        central_widget.setLayout(layout)

        self.setCentralWidget(central_widget)
        layout.addWidget(self.step_btn)

    def start(self):
        self.showMaximized()
        self.sound_engine.start()

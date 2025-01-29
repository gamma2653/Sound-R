from __future__ import annotations

from copy import deepcopy
from pprint import pformat
from typing import TYPE_CHECKING

# from pygame import mixer
from PySide6 import QtCore, QtMultimedia
from tqdm import tqdm

from ..utils import get_default_logger
from . import types

if TYPE_CHECKING:
    from typing import Optional

logger = get_default_logger(__name__)


def validate_mapping(data_map: types.ObjectMap, update_map: bool = True):
    # Check for scenes key
    errors: dict[str, str] = {}
    data_map_copy = deepcopy(data_map)
    if "scenes" not in data_map:
        errors["scenes_missing"] = "Sound Mapping is missing a `scenes` mapping."
    else:
        # Check if all scenes propery formatted
        scenes_data = data_map["scenes"]
        for scene, scene_data in scenes_data.items():
            for i, obj in enumerate(scene_data):
                remove_key = False
                if "type" not in obj:
                    errors[f"scenes_{scene}_{i}_notype"] = (
                        f"Scene `{scene}` obj `{i}` is missing a type."
                    )
                    remove_key = True
                if "id" not in obj:
                    errors[f"scenes_{scene}_{i}_noid"] = (
                        f"Scene `{scene}` obj {i} is missing an id."
                    )
                    remove_key = True
                if "payload" not in obj:
                    errors[f"scenes_{scene}_{i}_nopayload"] = (
                        f"Scene `{scene}` obj {i} is missing a payload."
                    )
                    remove_key = True
                if "loop" in obj and not isinstance(obj.get("loop"), bool):
                    errors[f"scenes_{scene}_{i}_loop_badtype"] = (
                        f"Scene `{scene}` obj {i} has an unexpected type for `loop`."
                    )
                    remove_key = True
                # remove invalid scene obj
                if remove_key and update_map:
                    # hur hur deleted scene
                    del data_map_copy["scenes"][scene][i]
    if errors:
        logger.warning(
            f"Encountered the following errors in data_map: \n{pformat(errors)}\nobject_map: {pformat(data_map)}"
        )
    return data_map_copy if update_map else data_map


class SoundPlayer(QtMultimedia.QMediaPlayer):

    def __init__(
        self,
        sound_url: QtCore.QUrl,
        parent: Optional[QtCore.QObject] = None,
        fadein: Optional[int] = None,
        fadeout: Optional[int] = None,
    ):
        super().__init__(parent)
        self.audio_out = QtMultimedia.QAudioOutput()
        self.setAudioOutput(self.audio_out)
        self.audio_out.setVolume(0.5)
        self.audio_out.volume()
        self.setSource(sound_url)
        self.fadeinT = fadein
        self.fadeoutT = fadeout
        self.fadeoutProp = QtCore.QPropertyAnimation(self.audio_out, b"volume")
        self.fadeinProp = QtCore.QPropertyAnimation(self.audio_out, b"volume")
        self.fadeoutProp.setEasingCurve(QtCore.QEasingCurve.Type.Linear)
        self.fadeinProp.setEasingCurve(QtCore.QEasingCurve.Type.Linear)

    def fadeout_pre(self):
        if self.fadeoutT is None:
            return
        self.fadeoutProp.setDuration(self.fadeoutT)
        self.fadeoutProp.setStartValue(self.audioOutput().volume())
        self.fadeoutProp.setEndValue(0)

    def fadeout_post(self):
        self.fadeoutProp.start()

    def fadein_pre(self):
        if self.fadeinT is None:
            return
        self.fadeinProp.setDuration(self.fadeinT)
        self.fadeinProp.setStartValue(0.01)
        self.fadeinProp.setEndValue(self.audioOutput().volume())

    def fadein_post(self):
        self.fadeinProp.start()

    def play(self):
        if self.fadeinT is not None:
            self.fadein_pre()
        super().play()
        if self.fadeinT is not None:
            self.fadein_post()

    def stop(self):
        if self.fadeoutT is not None:
            self.fadeout_pre()
        super().stop()
        if self.fadeoutT is not None:
            self.fadeout_post()


class SoundEngine:

    def __init__(
        self,
        data_map: types.ObjectMap,
        starting_id: str,
        load: bool = True,
        validate: bool = True,
    ):
        self.data_map = (
            validate_mapping(data_map)
            if validate
            else validate_mapping(data_map, update_map=False)
        )
        self.sounds: dict[str, SoundPlayer] = {}
        self.audioDevice = QtMultimedia.QAudioOutput()
        # self.channels: dict[tuple[str, int], mixer.Channel] = {}
        self.starting_id = starting_id
        if load:
            self.load()

    def load(self):
        logger.info("Loading sound engine...")
        self.sounds_root = self.data_map["root"] / "sounds"
        print("Loading sounds...")
        for id_, sound_path in tqdm(self.data_map["shortHands"].items()):
            self.sounds[id_] = SoundPlayer(
                QtCore.QUrl.fromLocalFile(self.sounds_root / sound_path),
                self.audioDevice,
            )
            # time.sleep(3)
        print("Sounds loaded.")

    def __str__(self):
        return pformat(self.data_map)

    def play_obj(self, scene_id: str, idx: int):
        scene_data = self.data_map["scenes"][scene_id]
        scene_obj = scene_data[idx]
        match scene_obj["type"]:
            case "sound":
                self.play_sound(scene_id, idx)
            case "cue":
                self.play_scene(scene_obj["payload"])
            case scene_obj_type:
                logger.warning(f"Unknown scene object type: {scene_obj_type}")

    def play_scene(self, scene_id: str):
        self.idx = 0
        self.scene_id = scene_id
        self.play_obj(scene_id, self.idx)

    def check_stop(self):
        obj_data = self.data_map["scenes"][self.scene_id][self.idx]
        if obj_data["type"] == "sound" and not obj_data.get("retain", False):
            if "fadeout" in obj_data.keys():
                self.sounds[obj_data["payload"]].fadeoutT = obj_data["fadeout"]
            self.sounds[obj_data["payload"]].stop()

    def step(self):
        # clear previous if should be cleared
        self.check_stop()
        self.idx += 1
        self.play_obj(self.scene_id, self.idx)

    def play_sound(self, scene_id, idx):
        scene_obj = self.data_map["scenes"][scene_id][idx]
        # self.channels[(scene_id, idx)] = self.sounds[scene_obj["payload"]].play()
        self.sounds[scene_obj["payload"]].play()
        print(f"Playing {scene_id}: [{idx}]")
        # time.sleep(10)

    def start(self):
        logger.debug("Starting sound engine...")
        self.play_scene(self.starting_id)
        logger.info("Sound engine started")

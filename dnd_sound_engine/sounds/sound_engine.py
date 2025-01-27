from __future__ import annotations

import pathlib
import time
from copy import deepcopy
from pprint import pformat
from typing import TYPE_CHECKING

from pygame import mixer
from tqdm import tqdm

from ..utils import get_default_logger
from . import types

if TYPE_CHECKING:
    from typing import Any, MutableMapping

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


class SoundEngine:

    def __init__(
        self, data_map: dict, starting_id: str, load: bool = True, validate: bool = True
    ):
        self.data_map = validate_mapping(data_map) if validate else data_map
        self.sounds: dict[str, mixer.Sound] = {}
        self.channels: dict[tuple[str, int], mixer.Channel] = {}
        self.starting_id = starting_id
        if load:
            self.load()

    def load(self):
        if not mixer.get_init():
            mixer.init()
        self.sounds_root = self.data_map["root"] / "sounds"
        print("Loading sounds...")
        for id_, sound_path in tqdm(self.data_map["shortHands"].items()):
            self.sounds[id_] = mixer.Sound(str(self.sounds_root / sound_path))

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
                self.channels[(self.scene_id, self.idx)].fadeout(obj_data["fadeout"])
                time.sleep(obj_data["fadeout"])
            else:
                self.channels[(self.scene_id, self.idx)].stop()
            del self.channels[(self.scene_id, self.idx)]

    def step(self):
        # clear previous if should be cleared
        self.check_stop()
        self.idx += 1
        self.play_obj(self.scene_id, self.idx)

    def play_sound(self, scene_id, idx):
        scene_obj = self.data_map["scenes"][scene_id][idx]
        self.channels[(scene_id, idx)] = self.sounds[scene_obj["payload"]].play()
        print(f"Playing {scene_id}: [{idx}]")
        # time.sleep(10)

    def start(self):
        self.play_scene(self.starting_id)

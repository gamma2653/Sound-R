from __future__ import annotations

from copy import deepcopy
from pprint import pformat
from typing import TYPE_CHECKING

from pydub import AudioSegment
from pydub.playback import play

from . import types
from .utils import get_default_logger

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

    def __init__(self, data_map: dict):
        self.data_map = validate_mapping(data_map)

    def __str__(self):
        return pformat(self.data_map)

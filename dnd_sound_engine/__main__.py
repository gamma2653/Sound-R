from __future__ import annotations

import argparse
import json
import os
import pathlib

from . import utils

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-interaction", "-ni", action="store_true", default=False)
    parser.add_argument(
        "--data_map",
        "-dm",
        action="store",
        default=str(pathlib.Path(os.getcwd(), "dnd_sound_engine", ".cache")),
    )
    known_args, _ = parser.parse_known_args()
    utils.ensure_ffmpeg(known_args.no_interaction)

from . import sound_engine, types

if __name__ == "__main__":
    DATA_FOLDER = known_args.data_map
    DATA_PATH = pathlib.Path(DATA_FOLDER)
    MAP_PATH = DATA_PATH / "map.json"
    with MAP_PATH.open() as f:
        OBJECT_MAP: types.ObjectMap = json.load(f)
    se = sound_engine.SoundEngine(OBJECT_MAP)
    print(se)

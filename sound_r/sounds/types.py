from __future__ import annotations

import pathlib
from typing import TYPE_CHECKING, Literal, Mapping, MutableMapping, TypedDict

if TYPE_CHECKING:
    from typing import Optional, TypeAlias

_ImplementedObjTypes: TypeAlias = Literal["sound", "cue", "art"]


# TODO: Change Optional for NotRequired (PEP 655)
class SceneObject(TypedDict):
    type: _ImplementedObjTypes
    id: str
    payload: str
    loop: Optional[bool]
    step: Optional[bool]  # default False for sound, True for art
    scale: Optional[float]  # only for art


ScenesData: TypeAlias = MutableMapping[str, list[SceneObject]]


# TODO: Change Optional for NotRequired (PEP 655)
class GlobalOptions(TypedDict):
    loopScenes: Optional[bool]


# TODO: Change Optional for NotRequired (PEP 655)
class ObjectMap(TypedDict):
    soundIDs: Mapping[str, str]
    artIDs: Mapping[str, str]
    scenes: ScenesData
    root: pathlib.Path
    globalOptions: Optional[GlobalOptions]

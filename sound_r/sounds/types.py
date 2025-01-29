from __future__ import annotations

import pathlib
from typing import TYPE_CHECKING, Literal, Mapping, MutableMapping, TypedDict

if TYPE_CHECKING:
    from typing import Optional, TypeAlias

_ImplementedObjTypes: TypeAlias = Literal["sound", "cue"]


# SceneObject: TypeAlias = MutableMapping[str, str | bool]
class SceneObject(TypedDict):
    type: _ImplementedObjTypes
    id: str
    payload: str
    loop: Optional[bool]


ScenesData: TypeAlias = MutableMapping[str, list[SceneObject]]


class ObjectMap(TypedDict):
    shortHands: Mapping[str, str]
    scenes: ScenesData
    root: pathlib.Path

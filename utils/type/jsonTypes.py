from __future__ import annotations

from typing import Union

JsonBaseType = Union[int, float, str, bool, None]
JsonType = Union[dict[str, 'JsonType'], list['JsonType'], JsonBaseType]

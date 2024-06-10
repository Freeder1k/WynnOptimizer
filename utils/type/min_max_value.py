from __future__ import annotations

from dataclasses import dataclass

@dataclass
class MinMaxValue:
    raw: int
    min: int
    max: int

    def __init__(self, raw: int, min_val: int = None, max_val: int = None):
        self.raw = raw
        if min_val is None or max_val is None:
            self.min = raw
            self.max = raw
            return
        if min_val > max_val:
            min_val, max_val = max_val, min_val
        self.min = min_val
        self.max = max_val

    @property
    def abs_max(self):
        return self.min if abs(self.min) > abs(self.max) else self.max

    @property
    def abs_min(self):
        return self.min if abs(self.min) < abs(self.max) else self.max

    @classmethod
    def from_api_data(cls, data: int | dict):
        if isinstance(data, int):
            return cls(data)
        else:
            return cls(data.get('raw', 0.5 * (data['min'] + data['max'])), data['min'], data['max'])

    def __add__(self, other: MinMaxValue):
        if other is None:
            return self
        if not isinstance(other, MinMaxValue):
            raise TypeError(f"unsupported operand type(s) for +: '{type(self)}' and '{type(other)}'")

        return MinMaxValue(self.raw + other.raw, self.min + other.min, self.max + other.max)

    def __radd__(self, other):
        return self + other

    def __mul__(self, scale: int):
        if not isinstance(scale, int):
            raise TypeError(f"unsupported operand type(s) for *: '{type(self)}' and '{type(scale)}'")

        if scale < 0:
            return MinMaxValue(int(self.raw * scale), int(self.max * scale), int(self.min * scale))
        else:
            return MinMaxValue(int(self.raw * scale), int(self.min * scale), int(self.max * scale))
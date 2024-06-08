from __future__ import annotations

from dataclasses import dataclass

@dataclass
class MinMaxValue:
    raw: int
    min: int
    max: int

    def __init__(self, raw: int, min: int = None, max: int = None):
        self.raw = raw
        self.min = min if min is not None else raw
        self.max = max if max is not None else raw

    @classmethod
    def from_api_data(cls, data: int | dict):
        if isinstance(data, int):
            return cls(data)
        else:
            return cls(data.get('raw', 0.5 * (data['min'] + data['max'])), data['min'], data['max'])

    @property
    def high(self):
        if self.max < 0:
            return self.min
        return self.max

    @property
    def low(self):
        if self.max < 0:
            return self.max
        return self.min

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
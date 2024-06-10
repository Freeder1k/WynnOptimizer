from __future__ import annotations

from dataclasses import dataclass

from wynndata.base import SkillpointsTuple


@dataclass
class Requirements:
    strength: int = 0
    dexterity: int = 0
    intelligence: int = 0
    defence: int = 0
    agility: int = 0
    level: int = 0

    def __add__(self, other: Requirements):
        if not isinstance(other, Requirements):
            raise TypeError(f"unsupported operand type(s) for +: '{type(self)}' and '{type(other)}'")

        return Requirements(
            self.strength + other.strength,
            self.dexterity + other.dexterity,
            self.intelligence + other.intelligence,
            self.defence + other.defence,
            self.agility + other.agility,
            max(self.level, other.level),
        )

    def __mul__(self, scale: float):
        if not isinstance(scale, float) and not isinstance(scale, int):
            raise TypeError(f"unsupported operand type(s) for *: '{type(self)}' and '{type(scale)}'")

        return Requirements(
            int(self.strength * scale),
            int(self.dexterity * scale),
            int(self.intelligence * scale),
            int(self.defence * scale),
            int(self.agility * scale),
            self.level,
        )

    def __getattr__(self, item):
        match item:
            case 'str':
                return self.strength
            case 'dex':
                return self.dexterity
            case 'int':
                return self.intelligence
            case 'def':
                return self.defence
            case 'agi':
                return self.agility
            case 'lvl':
                return self.level
            case _:
                raise AttributeError(f"'{type(self).__name__}' object has no attribute '{item}'")

    def __getitem__(self, key):
        try:
            return getattr(self, key)
        except AttributeError:
            raise KeyError(key)

    def __lt__(self, other):
        return [r1 < r2 for r1, r2 in zip(self.skillpoints, other.skillpoints)]

    def __le__(self, other):
        return [r1 <= r2 for r1, r2 in zip(self.skillpoints, other.skillpoints)]

    def __eq__(self, other):
        return [r1 == r2 for r1, r2 in zip(self.skillpoints, other.skillpoints)]

    def __ge__(self, other):
        return [r1 >= r2 for r1, r2 in zip(self.skillpoints, other.skillpoints)]

    def __gt__(self, other):
        return [r1 > r2 for r1, r2 in zip(self.skillpoints, other.skillpoints)]

    @property
    def skillpoints(self) -> SkillpointsTuple[int]:
        return SkillpointsTuple(self.strength, self.dexterity, self.intelligence, self.defence, self.agility)

    @property
    def sp_total(self):
        return sum(sp for sp in self.skillpoints if sp > 0)

    @classmethod
    def from_api_data(cls, requirements: dict, item_only_ids: dict = None):
        if item_only_ids is None:
            return cls(
                requirements.get('strength', 0),
                requirements.get('dexterity', 0),
                requirements.get('intelligence', 0),
                requirements.get('defence', 0),
                requirements.get('agility', 0),
                requirements.get('level', 0))
        else:
            return cls(
                item_only_ids.get('strengthRequirement', 0),
                item_only_ids.get('dexterityRequirement', 0),
                item_only_ids.get('intelligenceRequirement', 0),
                item_only_ids.get('defenceRequirement', 0),
                item_only_ids.get('agilityRequirement', 0),
                requirements.get('level', 0))

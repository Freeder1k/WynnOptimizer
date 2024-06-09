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

    def __mul__(self, scale: int):
        if not isinstance(scale, int):
            raise TypeError(f"unsupported operand type(s) for *: '{type(self)}' and '{type(scale)}'")

        return Requirements(
            self.strength * scale // 100,
            self.dexterity * scale // 100,
            self.intelligence * scale // 100,
            self.defence * scale // 100,
            self.agility * scale // 100,
            self.level,
        )

    def __getitem__(self, key):
        if key == 'strength' or key == 'str':
            return self.strength
        elif key == 'dexterity' or key == 'dex':
            return self.dexterity
        elif key == 'intelligence' or key == 'int':
            return self.intelligence
        elif key == 'defence' or key == 'def':
            return self.defence
        elif key == 'agility' or key == 'agi':
            return self.agility
        elif key == 'level':
            return self.level
        else:
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
            str = requirements.get('strength', 0)
            dex = requirements.get('dexterity', 0)
            int = requirements.get('intelligence', 0)
            defe = requirements.get('defence', 0)
            agi = requirements.get('agility', 0)
        else:
            str = item_only_ids.get('strengthRequirement', 0)
            dex = item_only_ids.get('dexterityRequirement', 0)
            int = item_only_ids.get('intelligenceRequirement', 0)
            defe = item_only_ids.get('defenceRequirement', 0)
            agi = item_only_ids.get('agilityRequirement', 0)
        return cls(
            str,
            dex,
            int,
            defe,
            agi,
            requirements.get('level', 0),
        )


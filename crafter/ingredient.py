from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


@dataclass
class Identification:
    raw: int
    min: int = 0
    max: int = 0

    @classmethod
    def from_api_data(cls, data: int | dict):
        if isinstance(data, int):
            return cls(data)
        else:
            return cls(data.get('raw', 0.5 * (data['min'] + data['max'])), data['min'], data['max'])

    def __add__(self, other: Identification):
        if other is None:
            return self
        if not isinstance(other, Identification):
            raise TypeError(f"unsupported operand type(s) for +: '{type(self)}' and '{type(other)}'")

        return Identification(self.raw + other.raw, self.min + other.min, self.max + other.max)

    def __radd__(self, other):
        return self + other

    def __mul__(self, scale: int):
        if not isinstance(scale, int):
            raise TypeError(f"unsupported operand type(s) for *: '{type(self)}' and '{type(scale)}'")

        return Identification(self.raw * scale // 100, self.min * scale // 100, self.max * scale // 100)


@dataclass
class Modifier:
    left: int = 0
    right: int = 0
    above: int = 0
    under: int = 0
    touching: int = 0
    notTouching: int = 0


class Skill(StrEnum):
    WEAPONSMITHING = "weaponsmithing"
    WOODWORKING = "woodworking"
    ARMOURING = "armouring"
    TAILORING = "tailoring"
    JEWELING = "jeweling"
    COOKING = "cooking"
    ALCHEMISM = "alchemism"
    SCRIBING = "scribing"


@dataclass
class Requirements:
    skills: set[Skill]
    strength: int = 0
    dexterity: int = 0
    intelligence: int = 0
    defence: int = 0
    agility: int = 0
    level: int = 0

    @classmethod
    def from_api_data(cls, item_only_ids: dict, requirements: dict):
        return cls(
            {Skill(skill) for skill in requirements['skills']},
            item_only_ids.get('strength', 0),
            item_only_ids.get('dexterity', 0),
            item_only_ids.get('intelligence', 0),
            item_only_ids.get('defence', 0),
            item_only_ids.get('agility', 0),
            requirements.get('level', 0)
        )

    def __add__(self, other: Requirements):
        if not isinstance(other, Requirements):
            raise TypeError(f"unsupported operand type(s) for +: '{type(self)}' and '{type(other)}'")

        return Requirements(
            self.skills & other.skills,
            self.strength + other.strength,
            self.dexterity + other.dexterity,
            self.intelligence + other.intelligence,
            self.defence + other.defence,
            self.agility + other.agility,
            max(self.level, other.level)
        )

    def __mul__(self, scale: int):
        if not isinstance(scale, int):
            raise TypeError(f"unsupported operand type(s) for *: '{type(self)}' and '{type(scale)}'")

        return Requirements(
            self.skills,
            self.strength * scale // 100,
            self.dexterity * scale // 100,
            self.intelligence * scale // 100,
            self.defence * scale // 100,
            self.agility * scale // 100,
            self.level
        )


@dataclass
class Ingredient:
    name: str
    charges: int
    duration: int
    durability: int
    identifications: dict[str, Identification]
    modifiers: Modifier
    requirements: Requirements

    @classmethod
    def from_api_json(cls, name, data: dict):
        try:
            return cls(
                name,
                data['consumableOnlyIDs']['charges'] if 'consumableOnlyIDs' in data else 0,
                data['consumableOnlyIDs']['duration'] if 'consumableOnlyIDs' in data else 0,
                data['itemOnlyIDs']['durabilityModifier'] if 'itemOnlyIDs' in data else 0,
                {k: Identification.from_api_data(v) for k, v in
                 data['identifications'].items()} if 'identifications' in data else {},
                Modifier(**data['ingredientPositionModifiers']),
                Requirements.from_api_data(data['itemOnlyIDs'], data['requirements']),
            )
        except Exception as e:
            print(name)
            raise e

    def __add__(self, other: Ingredient):
        if not isinstance(other, Ingredient):
            raise TypeError(f"unsupported operand type(s) for +: '{type(self)}' and '{type(other)}'")

        return Ingredient(
            "Merged Ingredient",
            self.charges + other.charges,
            self.duration + other.duration,
            self.durability + other.durability,
            {k: self.identifications.get(k, None) + other.identifications.get(k, None) for k in
             self.identifications.keys() | other.identifications.keys()},
            Modifier(),
            self.requirements + other.requirements
        )

    def __mul__(self, scale: int):
        if not isinstance(scale, int):
            raise TypeError(f"unsupported operand type(s) for *: '{type(self)}' and '{type(scale)}'")

        return Ingredient(
            "Multiplied Ingredient",
            self.charges,
            self.duration,
            self.durability,
            {k: v * scale for k, v in self.identifications.items()},
            self.modifiers,
            self.requirements * scale
        )


NO_INGREDIENT = Ingredient("No Ingredient", 0, 0, 0, {}, Modifier(),
                           Requirements(set(Skill(s) for s in Skill), 0, 0, 0, 0, 0, 0))

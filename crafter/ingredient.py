from __future__ import annotations

import json
from dataclasses import dataclass, field
from enum import StrEnum

from async_lru import alru_cache

from core.wynnAPI import item


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

        if scale < 0:
            return Identification(self.raw * scale // 100, self.max * scale // 100, self.min * scale // 100)
        else:
            return Identification(self.raw * scale // 100, self.min * scale // 100, self.max * scale // 100)


@dataclass
class IdentificationList:
    identifications: dict[str, Identification] = field(default_factory=dict)

    @classmethod
    def from_api_data(cls, data: dict):
        return cls({k: Identification.from_api_data(v) for k, v in data.items()})

    def __getitem__(self, key):
        if key in self.identifications:
            return self.identifications[key]
        return Identification(0)

    def __add__(self, other: IdentificationList):
        if other is None:
            return self
        if not isinstance(other, IdentificationList):
            raise TypeError(f"unsupported operand type(s) for +: '{type(self)}' and '{type(other)}'")

        return IdentificationList({k: self.identifications.get(k, None) + other.identifications.get(k, None) for k in
                                   self.identifications.keys() | other.identifications.keys()})

    def __mul__(self, scale: int):
        if not isinstance(scale, int):
            raise TypeError(f"unsupported operand type(s) for *: '{type(self)}' and '{type(scale)}'")

        return IdentificationList({k: v * scale for k, v in self.identifications.items()})


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
    skills: set[Skill] = field(default_factory=set)
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
            item_only_ids.get('strengthRequirement', 0),
            item_only_ids.get('dexterityRequirement', 0),
            item_only_ids.get('intelligenceRequirement', 0),
            item_only_ids.get('defenceRequirement', 0),
            item_only_ids.get('agilityRequirement', 0),
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
    identifications: IdentificationList
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
                IdentificationList.from_api_data(data['identifications'] if 'identifications' in data else {}),
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
            self.identifications + other.identifications,
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
            self.identifications * scale,
            self.modifiers,
            self.requirements * scale
        )

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name


NO_INGREDIENT = Ingredient("No Ingredient", 0, 0, 0, IdentificationList(), Modifier(),
                           Requirements(set(Skill(s) for s in Skill), 0, 0, 0, 0, 0, 0))


@alru_cache(ttl=3600)
async def get_all_ingredients():
    items = await item.database()

    return {k: Ingredient.from_api_json(k, v) for k, v in items.items()
            if 'itemOnlyIDs' in v or 'consumableOnlyIDs' in v}


async def get_ingredient(name: str):
    ingredients = await get_all_ingredients()
    return ingredients.get(name, None)


_ing_ids = {}


def _get_ing_ids():
    if not _ing_ids:
        with open("crafter/ingreds_clean.json") as f:
            _ing_ids.update({i['name']: i['id'] for i in json.load(f)})
        _ing_ids["No Ingredient"] = 4000
    return _ing_ids


def get_ing_id(name: str):
    return _get_ing_ids().get(name, 4095)

from __future__ import annotations

import itertools
import json
from dataclasses import dataclass, field
from enum import Enum

import numpy as np

from core.wynnAPI import item
from utils.decorators import ttl
from .requirements import Requirements
from .identifications import Identifications


@dataclass
class Modifier:
    left: int = 0
    right: int = 0
    above: int = 0
    under: int = 0
    touching: int = 0
    notTouching: int = 0

    def abs_total(self):
        return abs(self.left) + abs(self.right) + abs(self.above) + abs(self.under) + abs(self.touching) + abs(
            self.notTouching)


class Profession(Enum):
    WEAPONSMITHING = "weaponsmithing"
    WOODWORKING = "woodworking"
    ARMOURING = "armouring"
    TAILORING = "tailoring"
    JEWELING = "jeweling"
    COOKING = "cooking"
    ALCHEMISM = "alchemism"
    SCRIBING = "scribing"


@dataclass
class Ingredient:
    name: str
    id: int
    charges: int
    duration: int
    durability: int
    requirements: Requirements
    identifications: Identifications
    modifiers: Modifier
    skills: set[Profession] = field(default_factory=set)

    @classmethod
    def from_api_json(cls, name, data: dict):
        try:
            return cls(
                name,
                get_ing_id(name),
                data['consumableOnlyIDs']['charges'] if 'consumableOnlyIDs' in data else 0,
                data['consumableOnlyIDs']['duration'] if 'consumableOnlyIDs' in data else 0,
                data['itemOnlyIDs']['durabilityModifier'] if 'itemOnlyIDs' in data else 0,
                Requirements.from_api_data(data['requirements'], data['itemOnlyIDs']),
                Identifications.from_api_data(data['identifications'] if 'identifications' in data else {}),
                Modifier(**data['ingredientPositionModifiers']),
                {Profession(skill) for skill in data['requirements']['skills']}
            )
        except Exception as e:
            print(name)
            raise e

    def to_np_array(self, *ids):
        return np.array([self.charges,
                         self.duration,
                         self.durability,
                         self.requirements.strength,
                         self.requirements.dexterity,
                         self.requirements.intelligence,
                         self.requirements.defence,
                         self.requirements.agility,
                         self.modifiers.left,
                         self.modifiers.right,
                         self.modifiers.above,
                         self.modifiers.under,
                         self.modifiers.touching,
                         self.modifiers.notTouching,
                         *itertools.chain(*((self.identifications[i].min, self.identifications[i].max)
                                            for i in ids))
                         ],
                        dtype=np.intc
                        )

    def __add__(self, other: Ingredient):
        if not isinstance(other, Ingredient):
            raise TypeError(f"unsupported operand type(s) for +: '{type(self)}' and '{type(other)}'")

        return Ingredient(
            "Modified Ingredient",
            4095,
            self.charges + other.charges,
            self.duration + other.duration,
            self.durability + other.durability,
            self.requirements + other.requirements,
            self.identifications + other.identifications,
            Modifier(),
            self.skills & other.skills
        )

    def __mul__(self, scale: int):
        if not isinstance(scale, int):
            raise TypeError(f"unsupported operand type(s) for *: '{type(self)}' and '{type(scale)}'")

        return Ingredient(
            "Modified Ingredient",
            4095,
            self.charges,
            self.duration,
            self.durability,
            self.requirements * scale,
            self.identifications * scale,
            self.modifiers,
            self.skills
        )

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name


NO_INGREDIENT = Ingredient(
    "No Ingredient",
    4095,
    0,
    0,
    0,
    Requirements(0, 0, 0, 0, 0, 0),
    Identifications({}),
    Modifier(),
    set(Profession(s) for s in Profession)
)


@ttl(3600)
def get_all_ingredients() -> dict[str, Ingredient]:
    try:
        items = item.database()
    except TimeoutError:
        with open("data/database.json", "r") as f:
            items = json.load(f)

    return {k: Ingredient.from_api_json(k, v) for k, v in items.items()
            if 'itemOnlyIDs' in v or 'consumableOnlyIDs' in v}


def get_ingredient(name: str):
    ingredients = get_all_ingredients()
    return ingredients.get(name, None)


_ing_ids = {}


def _get_ing_ids():
    if not _ing_ids:
        with open("data/ingreds_clean.json") as f:
            _ing_ids.update({i['name']: i['id'] for i in json.load(f)})
        _ing_ids["No Ingredient"] = 4000
    return _ing_ids


def get_ing_id(name: str):
    return _get_ing_ids().get(name, 4095)

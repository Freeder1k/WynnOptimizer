from __future__ import annotations

import json
from collections import namedtuple
from dataclasses import dataclass

from core.wynnAPI import item
from utils.decorators import ttl
from utils.integer import Base64
from utils.type.min_max_value import MinMaxValue
from .base import ElementsTuple
from .identifications import Identifications
from .requirements import Requirements


@dataclass
class Base:
    health: int
    defences: ElementsTuple[int]
    damages: ElementsTuple[MinMaxValue]

    def __add__(self, other: Base):
        if not isinstance(other, Base):
            raise TypeError(f"unsupported operand type(s) for +: '{type(self)}' and '{type(other)}'")

        return Base(
            self.health + other.health,
            ElementsTuple(*(def1 + def2 for def1, def2 in zip(self.defences, other.defences))),
            ElementsTuple(*(dmg1 + dmg2 for dmg1, dmg2 in zip(self.damages, other.damages)))
        )

    @classmethod
    def from_api_data(cls, data: dict):
        return cls(
            data.get('health', 0),
            ElementsTuple(
                0,
                data.get('earthDefence', 0),
                data.get('thunderDefence', 0),
                data.get('waterDefence', 0),
                data.get('fireDefence', 0),
                data.get('airDefence', 0)),
            ElementsTuple(*(MinMaxValue.from_api_data(val) for val in (
                data.get('damage', 0),
                data.get('earthDamage', 0),
                data.get('thunderDamage', 0),
                data.get('waterDamage', 0),
                data.get('fireDamage', 0),
                data.get('airDamage', 0))))
        )

    @classmethod
    def none(cls):
        return cls(0, ElementsTuple(0, 0, 0, 0, 0, 0), ElementsTuple(*((MinMaxValue(0),) * 6)))


@dataclass
class Item:
    name: str
    id: int
    type: str
    base: Base
    requirements: Requirements
    identifications: Identifications

    @classmethod
    def from_api_json(cls, name, data: dict):
        try:
            return cls(
                name,
                get_item_id(name),
                data['type'] if 'type' in data else data['accessoryType'],
                Base.from_api_data(data['base']) if 'base' in data else Base.none(),
                Requirements.from_api_data(data['requirements']),
                Identifications.from_api_data(data['identifications'] if 'identifications' in data else {})
            )
        except Exception as e:
            print(name)
            raise e

    def b64_hash(self):
        return Base64.fromInt(self.id, 3)

    def __add__(self, other: Item):
        if not isinstance(other, Item):
            raise TypeError(f"unsupported operand type(s) for +: '{type(self)}' and '{type(other)}'")

        return Item(
            "Modified Item",
            10000,
            "modified",
            self.base + other.base,
            self.requirements + other.requirements,
            self.identifications + other.identifications
        )

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name


NO_ITEM = Item("No Item", 10000, "none", Base.none(), Requirements(0, 0, 0, 0, 0, 0), Identifications({}))


@dataclass
class Weapon(Item):
    attack_speed: str

    @classmethod
    def from_api_json(cls, name, data: dict):
        try:
            instance = super().from_api_json(name, data)
            attack_speed = data["attackSpeed"]
            return cls(instance.name,
                       instance.id,
                       instance.type,
                       instance.base,
                       instance.requirements,
                       instance.identifications,
                       attack_speed)
        except Exception as e:
            print(name)
            raise e


@dataclass
class Crafted(Item):
    charges: int
    duration: int
    durability: int

    def __init__(self, id, type, base, requirements, identifications, charges, duration, durability):
        name = "CR-"
        super().__init__(name, id, type, base, requirements, identifications)
        self.name += self.b64_hash()
        self.charges = charges
        self.duration = duration
        self.durability = durability

    def b64_hash(self):
        return f'{Base64.fromInt(self.id, 12)}{Base64.fromInt(get_recipe_id(self.type, self.requirements.level), 2)}91'


@ttl(3600)
def get_all_items() -> dict[str, Item]:
    try:
        items = item.database()
    except TimeoutError:
        items = item.database()

    items_ = {}
    for k, v in items.items():
        if v.get('type', '') in ['helmet', 'chestplate', 'leggings', 'boots'] or 'accessoryType' in v:
            items_[k] = Item.from_api_json(k, v)
    return items_


def get_item(name: str):
    items = get_all_items()
    return items.get(name, None)


def get_weapon(name: str):
    try:
        items = item.database()
    except TimeoutError:
        with open("data/database.json", "r") as f:
            items = json.load(f)
    it = items.get(name, {})
    if "base" not in it:
        raise ValueError(f"{name} not a weapon")
    return Weapon.from_api_json(name, it)


SkillpointsTuple = namedtuple('SkillpointsTuple', ['str', 'dex', 'int', 'defe', 'agi'])

_item_ids = {}


def _get_item_ids():
    if not _item_ids:
        with open("data/items_clean.json") as f:
            _item_ids.update({i['name']: i['id'] for i in json.load(f)})
        _item_ids["No Item"] = 10000
    return _item_ids


def get_item_id(name: str):
    return _get_item_ids().get(name, 10000)


_recipe_ids = {}


def _get_recipe_ids():
    if not _recipe_ids:
        with open("data/recipes_clean.json") as f:
            for i in json.load(f)['recipes']:
                r_type = i['type'].lower()
                if r_type not in _recipe_ids:
                    _recipe_ids[i['type'].lower()] = [0] * 106
                for j in range(i['lvl']['min'], i['lvl']['max'] + 1):
                    _recipe_ids[r_type][j] = i['id']
            _recipe_ids["none"] = [0] * 106
    return _recipe_ids


def get_recipe_id(type: str, lvl: int):
    return _get_recipe_ids().get(type, 10000)[lvl]

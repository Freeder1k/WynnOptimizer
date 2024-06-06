from __future__ import annotations

import itertools
from dataclasses import dataclass, field
from enum import StrEnum

import numpy as np
from attr import attr

from core.wynnAPI import item
from utils.decorators import ttl
from utils.skillpoints import SkillpointsTuple

class IdentificationType(StrEnum):
    NEUTRAL_DAMAGE = "damage"
    MAIN_ATTACK_DAMAGE = "mainAttackDamage"
    LOOT_BONUS = "lootBonus"
    RAW_DEFENCE = "rawDefence"
    RAW_MAIN_ATTACK_DAMAGE = "rawMainAttackDamage"
    LIFE_STEAL = "lifeSteal"
    EARTH_DAMAGE = "earthDamage"
    THUNDER_DAMAGE = "thunderDamage"
    RAW_INTELLIGENCE = "rawIntelligence"
    SPELL_DAMAGE = "spellDamage"
    EXPLODING = "exploding"
    SOUL_POINT_REGEN = "soulPointRegen"
    WATER_DAMAGE = "waterDamage"
    FIRE_DAMAGE = "fireDamage"
    WATER_DEFENCE = "waterDefence"
    RAW_AGILITY = "rawAgility"
    WALK_SPEED = "walkSpeed"
    AIR_DAMAGE = "airDamage"
    FIRE_DEFENCE = "fireDefence"
    RAW_DEXTERITY = "rawDexterity"
    POISON = "poison"
    MANA_STEAL = "manaSteal"
    RAW_STRENGTH = "rawStrength"
    EARTH_DEFENCE = "earthDefence"
    RAW_ATTACK_SPEED = "rawAttackSpeed"
    HEALTH_REGEN_RAW = "healthRegenRaw"
    REFLECTION = "reflection"
    XP_BONUS = "xpBonus"
    STEALING = "stealing"
    HEALTH_REGEN = "healthRegen"
    MANA_REGEN = "manaRegen"
    THORNS = "thorns"
    AIR_DEFENCE = "airDefence"
    THUNDER_DEFENCE = "thunderDefence"
    RAW_SPELL_DAMAGE = "rawSpellDamage"
    SPRINT_REGEN = "sprintRegen"
    HEALING_EFFICIENCY = "healingEfficiency"
    RAW_HEALTH = "rawHealth"
    RAW_2ND_SPELL_COST = "raw2ndSpellCost"
    FIRST_SPELL_COST = "1stSpellCost"
    RAW_4TH_SPELL_COST = "raw4thSpellCost"
    ELEMENTAL_DEFENCE = "elementalDefence"
    SECOND_SPELL_COST = "2ndSpellCost"
    THIRD_SPELL_COST = "3rdSpellCost"
    FOURTH_SPELL_COST = "4thSpellCost"
    RAW_1ST_SPELL_COST = "raw1stSpellCost"
    RAW_3RD_SPELL_COST = "raw3rdSpellCost"
    SPRINT = "sprint"
    JUMP_HEIGHT = "jumpHeight"
    AIR_MAIN_ATTACK_DAMAGE = "airMainAttackDamage"
    ELEMENTAL_SPELL_DAMAGE = "elementalSpellDamage"
    AIR_SPELL_DAMAGE = "airSpellDamage"
    WATER_SPELL_DAMAGE = "waterSpellDamage"
    KNOCKBACK = "knockback"
    RAW_THUNDER_MAIN_ATTACK_DAMAGE = "rawThunderMainAttackDamage"
    RAW_FIRE_MAIN_ATTACK_DAMAGE = "rawFireMainAttackDamage"
    THUNDER_SPELL_DAMAGE = "thunderSpellDamage"
    ELEMENTAL_DAMAGE = "elementalDamage"
    EARTH_SPELL_DAMAGE = "earthSpellDamage"
    RAW_THUNDER_SPELL_DAMAGE = "rawThunderSpellDamage"
    RAW_AIR_SPELL_DAMAGE = "rawAirSpellDamage"
    RAW_NEUTRAL_SPELL_DAMAGE = "rawNeutralSpellDamage"
    RAW_ELEMENTAL_MAIN_ATTACK_DAMAGE = "rawElementalMainAttackDamage"
    RAW_EARTH_SPELL_DAMAGE = "rawEarthSpellDamage"
    RAW_ELEMENTAL_DAMAGE = "rawElementalDamage"
    RAW_ELEMENTAL_SPELL_DAMAGE = "rawElementalSpellDamage"
    RAW_AIR_MAIN_ATTACK_DAMAGE = "rawAirMainAttackDamage"
    RAW_WATER_SPELL_DAMAGE = "rawWaterSpellDamage"
    RAW_FIRE_SPELL_DAMAGE = "rawFireSpellDamage"
    RAW_THUNDER_DAMAGE = "rawThunderDamage"
    RAW_WATER_DAMAGE = "rawWaterDamage"
    EARTH_MAIN_ATTACK_DAMAGE = "earthMainAttackDamage"
    THUNDER_MAIN_ATTACK_DAMAGE = "thunderMainAttackDamage"
    SLOW_ENEMY = "slowEnemy"
    FIRE_SPELL_DAMAGE = "fireSpellDamage"
    WEAKEN_ENEMY = "weakenEnemy"
    LEVELED_XP_BONUS = "leveledXpBonus"
    DAMAGE_FROM_MOBS = "damageFromMobs"
    LEVELED_LOOT_BONUS = "leveledLootBonus"
    ELEMENTAL_DEFENSE = "elementalDefense"
    RAW_FIRE_DAMAGE = "rawFireDamage"
    RAW_NEUTRAL_DAMAGE = "rawNeutralDamage"
    RAW_AIR_DAMAGE = "rawAirDamage"
    RAW_EARTH_DAMAGE = "rawEarthDamage"
    GATHER_XP_BONUS = "gatherXpBonus"
    RAW_WATER_MAIN_ATTACK_DAMAGE = "rawWaterMainAttackDamage"
    GATHER_SPEED = "gatherSpeed"
    LOOT_QUALITY = "lootQuality"
    RAW_EARTH_MAIN_ATTACK_DAMAGE = "rawEarthMainAttackDamage"


@dataclass
class Identification:
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
    def pos_max(self):
        if self.max < 0:
            return self.min
        return self.max

    def __add__(self, other):
        if other is None:
            return self
        if isinstance(other, Identification):
            return Identification(self.raw + other.raw, self.min + other.min, self.max + other.max)
        if isinstance(other, int):
            return Identification(self.raw + other, self.min + other, self.max + other)

        raise TypeError(f"unsupported operand type(s) for +: '{type(self)}' and '{type(other)}'")

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

    def __setitem__(self, key, value):
        self.identifications[key] = value

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

    @property
    def skillpoints(self):
        str = self['rawStrength'].raw
        dex = self['rawDexterity'].raw
        int = self['rawIntelligence'].raw
        def_ = self['rawDefence'].raw
        agi = self['rawAgility'].raw
        return SkillpointsTuple(str, dex, int, def_, agi)


@dataclass
class Requirements:
    strength: int = 0
    dexterity: int = 0
    intelligence: int = 0
    defence: int = 0
    agility: int = 0
    level: int = 0

    @classmethod
    def from_api_data(cls, requirements: dict):
        return cls(
            requirements.get('strength', 0),
            requirements.get('dexterity', 0),
            requirements.get('intelligence', 0),
            requirements.get('defence', 0),
            requirements.get('agility', 0),
            requirements.get('level', 0)
        )

    def __add__(self, other: Requirements):
        if not isinstance(other, Requirements):
            raise TypeError(f"unsupported operand type(s) for +: '{type(self)}' and '{type(other)}'")

        return Requirements(
            max(self.strength, other.strength),
            max(self.dexterity, other.dexterity),
            max(self.intelligence, other.intelligence),
            max(self.defence, other.defence),
            max(self.agility, other.agility),
            max(self.level, other.level)
        )

    @property
    def skillpoints(self):
        return SkillpointsTuple(self.strength, self.dexterity, self.intelligence, self.defence, self.agility)

    @property
    def total_sp(self):
        return (max(0, self.strength) + max(0, self.dexterity) + max(0, self.intelligence) + max(0, self.defence)
                + max(0, self.agility))

    def get_requirements(self):
        return [self.strength, self.dexterity, self.intelligence, self.defence, self.agility]

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


@dataclass
class Item:  # TODO: Add base stats (like base HP)
    name: str
    type: str
    identifications: IdentificationList
    requirements: Requirements

    @classmethod
    def from_api_json(cls, name, data: dict):
        try:
            if 'type' in data:
                type = data['type']
            else:
                type = data['accessoryType']
            return cls(
                name,
                type,
                IdentificationList.from_api_data(data['identifications'] if 'identifications' in data else {}),
                Requirements.from_api_data(data['requirements']),
            )
        except Exception as e:
            print(name)
            raise e

    def to_np_array(self, *ids):
        return np.array([
                         self.requirements.strength,
                         self.requirements.dexterity,
                         self.requirements.intelligence,
                         self.requirements.defence,
                         self.requirements.agility,
                         *itertools.chain(*((self.identifications[i].min, self.identifications[i].max)
                                            for i in ids))
                         ],
                        dtype=np.intc
                        )

    def __add__(self, other: Item):
        if not isinstance(other, Item):
            raise TypeError(f"unsupported operand type(s) for +: '{type(self)}' and '{type(other)}'")

        return Item(
            "Merged Item",
            "merged",
            self.identifications + other.identifications,
            self.requirements + other.requirements
        )

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name


NO_ITEM = Item("No Item", "none", IdentificationList(), Requirements(0, 0, 0, 0, 0, 0))


@dataclass
class Weapon(Item):
    attackSpeed: str
    damage: IdentificationList

    @classmethod
    def from_api_json(cls, name, data: dict):
        try:
            instance = Item.from_api_json(name, data)
            damage = IdentificationList.from_api_data(data.get("base", {}))
            attackSpeed = data["attackSpeed"]
            return cls(instance.name, instance.type, instance.identifications, instance.requirements, attackSpeed, damage)
        except Exception as e:
            print(name)
            raise e


@dataclass
class Crafted(Item):
    charges: int
    duration: int
    durability: int


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
        items = item.database()
    it = items.get(name, {})
    if "base" not in it:
        raise ValueError(f"{name} not a weapon")
    return Weapon.from_api_json(name, it)

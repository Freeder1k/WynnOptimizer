from __future__ import annotations

import itertools
import json
from dataclasses import dataclass, field
from enum import StrEnum

import numpy as np
from async_lru import alru_cache

from core.wynnAPI import item


class IdentificationType(StrEnum):
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

    def abs_total(self):
        return abs(self.left) + abs(self.right) + abs(self.above) + abs(self.under) + abs(self.touching) + abs(
            self.notTouching)


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
async def get_all_ingredients() -> dict[str, Ingredient]:
    try:
        items = await item.database()
    except TimeoutError:
        items = await item.database()

    return {k: Ingredient.from_api_json(k, v) for k, v in items.items()
            if 'itemOnlyIDs' in v or 'consumableOnlyIDs' in v}


async def get_ingredient(name: str):
    ingredients = await get_all_ingredients()
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

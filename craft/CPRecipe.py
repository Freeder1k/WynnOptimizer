from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Callable

from ortools.sat.python.cp_model import LinearExpr

from wynndata.base import SkillpointsTuple
from wynndata.ingredient import Ingredient


class LinearExprGenerator(ABC):
    @abstractmethod
    def generate(self, value_func: Callable[[Ingredient], int], raw: bool = False) -> LinearExpr:
        """
        Generate a linear expression from a value function.
        :param value_func: Function that returns the desired value of an ingredient.
        :param raw: Whether the value is modified by other ingredient's modifiers or just the raw value.
        """
        pass


@dataclass
class CPRequirements:
    strength: LinearExpr
    dexterity: LinearExpr
    intelligence: LinearExpr
    defence: LinearExpr
    agility: LinearExpr

    def __init__(self, lin_expr_gen: LinearExprGenerator):
        self.lin_expr_gen = lin_expr_gen

    def __getattr__(self, item):
        expr = self.lin_expr_gen.generate(lambda i: getattr(i.requirements, item))
        setattr(self, item, expr)
        return expr

    def __getitem__(self, key):
        match key:
            case 'strength', 'str':
                return self.strength
            case 'dexterity', 'dex':
                return self.dexterity
            case 'intelligence', 'int':
                return self.intelligence
            case 'defence', 'def':
                return self.defence
            case 'agility', 'agi':
                return self.agility
            case _:
                raise KeyError(key)

    @property
    def skillpoints(self) -> SkillpointsTuple[LinearExpr]:
        return SkillpointsTuple(self.strength, self.dexterity, self.intelligence, self.defence, self.agility)


class CPIdentificationValue:
    raw: LinearExpr
    min: LinearExpr
    max: LinearExpr
    abs_max: LinearExpr
    abs_min: LinearExpr

    def __init__(self, lin_expr_gen: LinearExprGenerator, name: str):
        self.lin_expr_gen = lin_expr_gen
        self.name = name

    def __getattr__(self, item):
        expr = self.lin_expr_gen.generate(lambda i: getattr(i.identifications[self.name], item))
        setattr(self, item, expr)
        return expr


class CPIdentifications:
    rawMainAttackDamage: CPIdentificationValue
    rawSpellDamage: CPIdentificationValue
    healthRegenRaw: CPIdentificationValue
    manaSteal: CPIdentificationValue
    walkSpeed: CPIdentificationValue
    thunderDamage: CPIdentificationValue
    rawStrength: CPIdentificationValue
    rawDexterity: CPIdentificationValue
    rawIntelligence: CPIdentificationValue
    rawDefence: CPIdentificationValue
    rawAgility: CPIdentificationValue
    lootBonus: CPIdentificationValue
    fireDefence: CPIdentificationValue
    airDefence: CPIdentificationValue
    mainAttackDamage: CPIdentificationValue
    spellDamage: CPIdentificationValue
    exploding: CPIdentificationValue
    airDamage: CPIdentificationValue
    rawHealth: CPIdentificationValue
    reflection: CPIdentificationValue
    earthDefence: CPIdentificationValue
    earthDamage: CPIdentificationValue
    waterDamage: CPIdentificationValue
    waterDefence: CPIdentificationValue
    healthRegen: CPIdentificationValue
    manaRegen: CPIdentificationValue
    fireDamage: CPIdentificationValue
    lifeSteal: CPIdentificationValue
    rawAttackSpeed: CPIdentificationValue
    xpBonus: CPIdentificationValue
    thunderDefence: CPIdentificationValue
    thorns: CPIdentificationValue
    soulPointRegen: CPIdentificationValue
    stealing: CPIdentificationValue
    firstSpellCost: CPIdentificationValue
    secondSpellCost: CPIdentificationValue
    rawfirstSpellCost: CPIdentificationValue
    rawthirdSpellCost: CPIdentificationValue
    jumpHeight: CPIdentificationValue
    airSpellDamage: CPIdentificationValue
    poison: CPIdentificationValue
    elementalDamage: CPIdentificationValue
    healingEfficiency: CPIdentificationValue
    rawfourthSpellCost: CPIdentificationValue
    rawsecondSpellCost: CPIdentificationValue
    sprintRegen: CPIdentificationValue
    slowEnemy: CPIdentificationValue
    thirdSpellCost: CPIdentificationValue
    sprint: CPIdentificationValue
    elementalSpellDamage: CPIdentificationValue
    rawNeutralSpellDamage: CPIdentificationValue
    fourthSpellCost: CPIdentificationValue
    knockback: CPIdentificationValue
    waterSpellDamage: CPIdentificationValue
    fireSpellDamage: CPIdentificationValue
    rawAirMainAttackDamage: CPIdentificationValue
    rawAirSpellDamage: CPIdentificationValue
    earthSpellDamage: CPIdentificationValue
    rawThunderDamage: CPIdentificationValue
    rawWaterDamage: CPIdentificationValue
    rawElementalDamage: CPIdentificationValue
    rawEarthSpellDamage: CPIdentificationValue
    elementalDefence: CPIdentificationValue
    rawThunderMainAttackDamage: CPIdentificationValue
    thunderSpellDamage: CPIdentificationValue
    rawThunderSpellDamage: CPIdentificationValue
    rawFireMainAttackDamage: CPIdentificationValue
    weakenEnemy: CPIdentificationValue
    rawWaterSpellDamage: CPIdentificationValue
    earthMainAttackDamage: CPIdentificationValue
    rawFireSpellDamage: CPIdentificationValue
    rawElementalSpellDamage: CPIdentificationValue
    healing: CPIdentificationValue
    rawElementalMainAttackDamage: CPIdentificationValue
    airMainAttackDamage: CPIdentificationValue
    thunderMainAttackDamage: CPIdentificationValue
    leveledLootBonus: CPIdentificationValue
    damageFromMobs: CPIdentificationValue
    leveledXpBonus: CPIdentificationValue
    elementalDefense: CPIdentificationValue
    rawAirDamage: CPIdentificationValue
    rawEarthDamage: CPIdentificationValue
    rawFireDamage: CPIdentificationValue
    rawNeutralDamage: CPIdentificationValue
    lootQuality: CPIdentificationValue
    gatherXpBonus: CPIdentificationValue
    gatherSpeed: CPIdentificationValue
    rawWaterMainAttackDamage: CPIdentificationValue
    rawEarthMainAttackDamage: CPIdentificationValue

    def __init__(self, lin_expr_gen: LinearExprGenerator):
        self.lin_expr_gen = lin_expr_gen

    def __getattr__(self, item):
        setattr(self, item, CPIdentificationValue(self.lin_expr_gen, item))
        return getattr(self, item)

    def __getitem__(self, item: str) -> CPIdentificationValue:
        return getattr(self, item)

    @property
    def skillpoints(self) -> SkillpointsTuple[LinearExpr]:
        str = self.rawStrength.raw
        dex = self.rawDexterity.raw
        int = self.rawIntelligence.raw
        defe = self.rawDefence.raw
        agi = self.rawAgility.raw
        return SkillpointsTuple(str, dex, int, defe, agi)


class CPRecipe:
    def __init__(self, lin_expr_gen: LinearExprGenerator):
        self.lin_expr_gen = lin_expr_gen
        self.requirements = CPRequirements(lin_expr_gen)
        self.identifications = CPIdentifications(lin_expr_gen)
        self._charges = None
        self._duration = None
        self._durability = None

    @property
    def charges(self):
        if self._charges is None:
            self._charges = self.lin_expr_gen.generate(lambda i: i.charges, True) + 3
        return self._charges

    @property
    def duration(self):
        if self._duration is None:
            self._duration = self.lin_expr_gen.generate(lambda i: i.duration, True)
        return self._duration

    @property
    def durability(self):
        if self._durability is None:
            self._durability = self.lin_expr_gen.generate(lambda i: i.durability // 1000, True) + 735
        return self._durability

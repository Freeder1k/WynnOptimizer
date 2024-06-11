from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Any

from ortools.sat.python.cp_model import LinearExpr

from craft.optimizerCP2 import CPRecipeOptimizer
from wynndata.base import SkillpointsTuple
from wynndata.ingredient import Ingredient


class LinearExprGenerator:
    def __init__(self, optimizer: CPRecipeOptimizer, accessor: Callable[[Ingredient], Any]):
        self._optimizer = optimizer
        self._accessor = accessor

    def _gen_lin_expr(self, attr: str) -> LinearExpr:
        return (LinearExpr().sum([getattr(self._accessor(self._optimizer.ingrs_mod[i][j]), attr)
                                  * self._optimizer.ingredient_variables[i][j]
                                  for i in range(self._optimizer.mod_amt)
                                  for j in range(self._optimizer.ingr_count)
                                  if getattr(self._accessor(self._optimizer.ingrs_mod[i][j]), attr) != 0])
                + LinearExpr().sum([getattr(self._accessor(self._optimizer.base_items[i]), attr)
                                    * self._optimizer.base_variables[i]
                                    for i in range(len(self._optimizer.base_items))]))

    def __getattr__(self, item) -> LinearExpr:
        expr = self._get_lin_expr(item)
        setattr(self, item, expr)
        return expr


@dataclass
class CPRequirements(LinearExprGenerator):
    strength: LinearExpr
    dexterity: LinearExpr
    intelligence: LinearExpr
    defence: LinearExpr
    agility: LinearExpr
    level: LinearExpr

    def __init__(self, optimizer: CPRecipeOptimizer):
        super().__init__(optimizer, lambda ingr: ingr.requirements)

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
            case 'level':
                return self.level
            case _:
                raise KeyError(key)

    @property
    def skillpoints(self) -> SkillpointsTuple[LinearExpr]:
        return SkillpointsTuple(self.strength, self.dexterity, self.intelligence, self.defence, self.agility)


class CPIdentificationValue(LinearExprGenerator):
    raw: LinearExpr
    min: LinearExpr
    max: LinearExpr
    abs_max: LinearExpr
    abs_min: LinearExpr

    def __init__(self, optimizer: CPRecipeOptimizer, id_name: str):
        super().__init__(optimizer, lambda ingr: ingr.identifications[id_name])


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

    def __init__(self, optimizer: CPRecipeOptimizer):
        super().__init__(optimizer)

    def __getattr__(self, item):
        setattr(self, item, CPIdentificationValue(self.optimizer, item))
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


class CPIngredient(LinearExprGenerator):
    charges: LinearExpr
    duration: LinearExpr
    durability: LinearExpr

    def __init__(self, optimizer: CPRecipeOptimizer):
        super().__init__(optimizer, lambda ingr: ingr)
        self.requirements = CPRequirements(optimizer)
        self.identifications = CPIdentifications(optimizer)

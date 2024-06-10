from __future__ import annotations

from dataclasses import dataclass

from utils.type.min_max_value import MinMaxValue
from .base import SkillpointsTuple


def replace_num(s: str):
    return s.replace('1st', 'first').replace('2nd', 'second').replace('3rd', 'third').replace('4th', 'fourth')


@dataclass
class Identifications:
    rawMainAttackDamage: MinMaxValue
    rawSpellDamage: MinMaxValue
    healthRegenRaw: MinMaxValue
    manaSteal: MinMaxValue
    walkSpeed: MinMaxValue
    thunderDamage: MinMaxValue
    rawStrength: MinMaxValue
    rawDexterity: MinMaxValue
    rawIntelligence: MinMaxValue
    rawDefence: MinMaxValue
    rawAgility: MinMaxValue
    lootBonus: MinMaxValue
    fireDefence: MinMaxValue
    airDefence: MinMaxValue
    mainAttackDamage: MinMaxValue
    spellDamage: MinMaxValue
    exploding: MinMaxValue
    airDamage: MinMaxValue
    rawHealth: MinMaxValue
    reflection: MinMaxValue
    earthDefence: MinMaxValue
    earthDamage: MinMaxValue
    waterDamage: MinMaxValue
    waterDefence: MinMaxValue
    healthRegen: MinMaxValue
    manaRegen: MinMaxValue
    fireDamage: MinMaxValue
    lifeSteal: MinMaxValue
    rawAttackSpeed: MinMaxValue
    xpBonus: MinMaxValue
    thunderDefence: MinMaxValue
    thorns: MinMaxValue
    soulPointRegen: MinMaxValue
    stealing: MinMaxValue
    firstSpellCost: MinMaxValue
    secondSpellCost: MinMaxValue
    rawfirstSpellCost: MinMaxValue
    rawthirdSpellCost: MinMaxValue
    jumpHeight: MinMaxValue
    airSpellDamage: MinMaxValue
    poison: MinMaxValue
    elementalDamage: MinMaxValue
    healingEfficiency: MinMaxValue
    rawfourthSpellCost: MinMaxValue
    rawsecondSpellCost: MinMaxValue
    sprintRegen: MinMaxValue
    slowEnemy: MinMaxValue
    thirdSpellCost: MinMaxValue
    sprint: MinMaxValue
    elementalSpellDamage: MinMaxValue
    rawNeutralSpellDamage: MinMaxValue
    fourthSpellCost: MinMaxValue
    knockback: MinMaxValue
    waterSpellDamage: MinMaxValue
    fireSpellDamage: MinMaxValue
    rawAirMainAttackDamage: MinMaxValue
    rawAirSpellDamage: MinMaxValue
    earthSpellDamage: MinMaxValue
    rawThunderDamage: MinMaxValue
    rawWaterDamage: MinMaxValue
    rawElementalDamage: MinMaxValue
    rawEarthSpellDamage: MinMaxValue
    elementalDefence: MinMaxValue
    rawThunderMainAttackDamage: MinMaxValue
    thunderSpellDamage: MinMaxValue
    rawThunderSpellDamage: MinMaxValue
    rawFireMainAttackDamage: MinMaxValue
    weakenEnemy: MinMaxValue
    rawWaterSpellDamage: MinMaxValue
    earthMainAttackDamage: MinMaxValue
    rawFireSpellDamage: MinMaxValue
    rawElementalSpellDamage: MinMaxValue
    healing: MinMaxValue
    rawElementalMainAttackDamage: MinMaxValue
    airMainAttackDamage: MinMaxValue
    thunderMainAttackDamage: MinMaxValue
    leveledLootBonus: MinMaxValue
    damageFromMobs: MinMaxValue
    leveledXpBonus: MinMaxValue
    elementalDefense: MinMaxValue
    rawAirDamage: MinMaxValue
    rawEarthDamage: MinMaxValue
    rawFireDamage: MinMaxValue
    rawNeutralDamage: MinMaxValue
    lootQuality: MinMaxValue
    gatherXpBonus: MinMaxValue
    gatherSpeed: MinMaxValue
    rawWaterMainAttackDamage: MinMaxValue
    rawEarthMainAttackDamage: MinMaxValue

    def __init__(self, ids: dict[str, MinMaxValue]):
        self._ids = ids

    def __getattr__(self, item):
        return self._ids.get(item, MinMaxValue(0))

    def __getitem__(self, item: str) -> MinMaxValue:
        return getattr(self, item)

    def __add__(self, other: Identifications):
        if other is None:
            return self
        if not isinstance(other, Identifications):
            raise TypeError(f"unsupported operand type(s) for +: '{type(self)}' and '{type(other)}'")

        return Identifications({k: self._ids.get(k, None) + other._ids.get(k, None) for k in
                                self._ids.keys() | other._ids.keys()})

    def __mul__(self, scale: int):
        if not isinstance(scale, int):
            raise TypeError(f"unsupported operand type(s) for *: '{type(self)}' and '{type(scale)}'")

        return Identifications({k: v * scale for k, v in self._ids.items()})

    @property
    def skillpoints(self) -> SkillpointsTuple[MinMaxValue]:
        str = self.rawStrength.raw
        dex = self.rawDexterity.raw
        int = self.rawIntelligence.raw
        defe = self.rawDefence.raw
        agi = self.rawAgility.raw
        return SkillpointsTuple(str, dex, int, defe, agi)

    @classmethod
    def from_api_data(cls, data: dict):
        return cls({replace_num(k): MinMaxValue.from_api_data(v) for k, v in data.items()})

from __future__ import annotations

from dataclasses import dataclass

from utils.type.min_max_value import MinMaxValue
from .base import SkillpointsTuple


def replace_num(s: str):
    return s.replace('1st', 'first').replace('2nd', 'second').replace('3rd', 'third').replace('4th', 'fourth')


@dataclass
class Identifications:
    rawMainAttackDamage = MinMaxValue(0)
    rawSpellDamage = MinMaxValue(0)
    healthRegenRaw = MinMaxValue(0)
    manaSteal = MinMaxValue(0)
    walkSpeed = MinMaxValue(0)
    thunderDamage = MinMaxValue(0)
    rawStrength = MinMaxValue(0)
    rawDexterity = MinMaxValue(0)
    rawIntelligence = MinMaxValue(0)
    rawDefence = MinMaxValue(0)
    rawAgility = MinMaxValue(0)
    lootBonus = MinMaxValue(0)
    fireDefence = MinMaxValue(0)
    airDefence = MinMaxValue(0)
    mainAttackDamage = MinMaxValue(0)
    spellDamage = MinMaxValue(0)
    exploding = MinMaxValue(0)
    airDamage = MinMaxValue(0)
    rawHealth = MinMaxValue(0)
    reflection = MinMaxValue(0)
    earthDefence = MinMaxValue(0)
    earthDamage = MinMaxValue(0)
    waterDamage = MinMaxValue(0)
    waterDefence = MinMaxValue(0)
    healthRegen = MinMaxValue(0)
    manaRegen = MinMaxValue(0)
    fireDamage = MinMaxValue(0)
    lifeSteal = MinMaxValue(0)
    rawAttackSpeed = MinMaxValue(0)
    xpBonus = MinMaxValue(0)
    thunderDefence = MinMaxValue(0)
    thorns = MinMaxValue(0)
    soulPointRegen = MinMaxValue(0)
    stealing = MinMaxValue(0)
    firstSpellCost = MinMaxValue(0)
    secondSpellCost = MinMaxValue(0)
    rawfirstSpellCost = MinMaxValue(0)
    rawthirdSpellCost = MinMaxValue(0)
    jumpHeight = MinMaxValue(0)
    airSpellDamage = MinMaxValue(0)
    poison = MinMaxValue(0)
    elementalDamage = MinMaxValue(0)
    healingEfficiency = MinMaxValue(0)
    rawfourthSpellCost = MinMaxValue(0)
    rawsecondSpellCost = MinMaxValue(0)
    sprintRegen = MinMaxValue(0)
    slowEnemy = MinMaxValue(0)
    thirdSpellCost = MinMaxValue(0)
    sprint = MinMaxValue(0)
    elementalSpellDamage = MinMaxValue(0)
    rawNeutralSpellDamage = MinMaxValue(0)
    fourthSpellCost = MinMaxValue(0)
    knockback = MinMaxValue(0)
    waterSpellDamage = MinMaxValue(0)
    fireSpellDamage = MinMaxValue(0)
    rawAirMainAttackDamage = MinMaxValue(0)
    rawAirSpellDamage = MinMaxValue(0)
    earthSpellDamage = MinMaxValue(0)
    rawThunderDamage = MinMaxValue(0)
    rawWaterDamage = MinMaxValue(0)
    rawElementalDamage = MinMaxValue(0)
    rawEarthSpellDamage = MinMaxValue(0)
    elementalDefence = MinMaxValue(0)
    rawThunderMainAttackDamage = MinMaxValue(0)
    thunderSpellDamage = MinMaxValue(0)
    rawThunderSpellDamage = MinMaxValue(0)
    rawFireMainAttackDamage = MinMaxValue(0)
    weakenEnemy = MinMaxValue(0)
    rawWaterSpellDamage = MinMaxValue(0)
    earthMainAttackDamage = MinMaxValue(0)
    rawFireSpellDamage = MinMaxValue(0)
    rawElementalSpellDamage = MinMaxValue(0)
    healing = MinMaxValue(0)
    rawElementalMainAttackDamage = MinMaxValue(0)
    airMainAttackDamage = MinMaxValue(0)
    thunderMainAttackDamage = MinMaxValue(0)
    leveledLootBonus = MinMaxValue(0)
    damageFromMobs = MinMaxValue(0)
    leveledXpBonus = MinMaxValue(0)
    elementalDefense = MinMaxValue(0)
    rawAirDamage = MinMaxValue(0)
    rawEarthDamage = MinMaxValue(0)
    rawFireDamage = MinMaxValue(0)
    rawNeutralDamage = MinMaxValue(0)
    lootQuality = MinMaxValue(0)
    gatherXpBonus = MinMaxValue(0)
    gatherSpeed = MinMaxValue(0)
    rawWaterMainAttackDamage = MinMaxValue(0)
    rawEarthMainAttackDamage = MinMaxValue(0)

    def __init__(self, ids: dict[str, MinMaxValue]):
        self._ids = ids
        for k, v in ids.items():
            setattr(self, k, v)

    def __getitem__(self, item: str) -> MinMaxValue:
        return self._ids.get(item, MinMaxValue(0))

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

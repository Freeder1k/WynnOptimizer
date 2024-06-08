from __future__ import annotations

from dataclasses import dataclass

from utils.type.min_max_value import MinMaxValue

from .base import SkillpointsTuple


def replace_num(s: str):
    return s.replace('1st', 'first').replace('2nd', 'second').replace('3rd', 'third').replace('4th', 'fourth')


@dataclass
class Identifications:
    rawMainAttackDamage: MinMaxValue = None
    rawSpellDamage: MinMaxValue = None
    healthRegenRaw: MinMaxValue = None
    manaSteal: MinMaxValue = None
    walkSpeed: MinMaxValue = None
    thunderDamage: MinMaxValue = None
    rawStrength: MinMaxValue = None
    rawDexterity: MinMaxValue = None
    rawIntelligence: MinMaxValue = None
    rawDefence: MinMaxValue = None
    rawAgility: MinMaxValue = None
    lootBonus: MinMaxValue = None
    fireDefence: MinMaxValue = None
    airDefence: MinMaxValue = None
    mainAttackDamage: MinMaxValue = None
    spellDamage: MinMaxValue = None
    exploding: MinMaxValue = None
    airDamage: MinMaxValue = None
    rawHealth: MinMaxValue = None
    reflection: MinMaxValue = None
    earthDefence: MinMaxValue = None
    earthDamage: MinMaxValue = None
    waterDamage: MinMaxValue = None
    waterDefence: MinMaxValue = None
    healthRegen: MinMaxValue = None
    manaRegen: MinMaxValue = None
    fireDamage: MinMaxValue = None
    lifeSteal: MinMaxValue = None
    rawAttackSpeed: MinMaxValue = None
    xpBonus: MinMaxValue = None
    thunderDefence: MinMaxValue = None
    thorns: MinMaxValue = None
    soulPointRegen: MinMaxValue = None
    stealing: MinMaxValue = None
    firstSpellCost: MinMaxValue = None
    secondSpellCost: MinMaxValue = None
    rawfirstSpellCost: MinMaxValue = None
    rawthirdSpellCost: MinMaxValue = None
    jumpHeight: MinMaxValue = None
    airSpellDamage: MinMaxValue = None
    poison: MinMaxValue = None
    elementalDamage: MinMaxValue = None
    healingEfficiency: MinMaxValue = None
    rawfourthSpellCost: MinMaxValue = None
    rawsecondSpellCost: MinMaxValue = None
    sprintRegen: MinMaxValue = None
    slowEnemy: MinMaxValue = None
    thirdSpellCost: MinMaxValue = None
    sprint: MinMaxValue = None
    elementalSpellDamage: MinMaxValue = None
    rawNeutralSpellDamage: MinMaxValue = None
    fourthSpellCost: MinMaxValue = None
    knockback: MinMaxValue = None
    waterSpellDamage: MinMaxValue = None
    fireSpellDamage: MinMaxValue = None
    rawAirMainAttackDamage: MinMaxValue = None
    rawAirSpellDamage: MinMaxValue = None
    earthSpellDamage: MinMaxValue = None
    rawThunderDamage: MinMaxValue = None
    rawWaterDamage: MinMaxValue = None
    rawElementalDamage: MinMaxValue = None
    rawEarthSpellDamage: MinMaxValue = None
    elementalDefence: MinMaxValue = None
    rawThunderMainAttackDamage: MinMaxValue = None
    thunderSpellDamage: MinMaxValue = None
    rawThunderSpellDamage: MinMaxValue = None
    rawFireMainAttackDamage: MinMaxValue = None
    weakenEnemy: MinMaxValue = None
    rawWaterSpellDamage: MinMaxValue = None
    earthMainAttackDamage: MinMaxValue = None
    rawFireSpellDamage: MinMaxValue = None
    rawElementalSpellDamage: MinMaxValue = None
    healing: MinMaxValue = None
    rawElementalMainAttackDamage: MinMaxValue = None
    airMainAttackDamage: MinMaxValue = None
    thunderMainAttackDamage: MinMaxValue = None
    leveledLootBonus: MinMaxValue = None
    damageFromMobs: MinMaxValue = None
    leveledXpBonus: MinMaxValue = None
    elementalDefense: MinMaxValue = None
    rawAirDamage: MinMaxValue = None
    rawEarthDamage: MinMaxValue = None
    rawFireDamage: MinMaxValue = None
    rawNeutralDamage: MinMaxValue = None
    lootQuality: MinMaxValue = None
    gatherXpBonus: MinMaxValue = None
    gatherSpeed: MinMaxValue = None
    rawWaterMainAttackDamage: MinMaxValue = None
    rawEarthMainAttackDamage: MinMaxValue = None

    def __init__(self, ids: dict[str, MinMaxValue]):
        self._ids = ids

    def __getattr__(self, name):
        if name in ['_ids', 'skillpoints']:
            return object.__getattribute__(self, name)
        return self._ids.get(name, MinMaxValue(0))


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

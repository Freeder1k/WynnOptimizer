from __future__ import annotations

from dataclasses import dataclass

from utils.type.min_max_value import MinMaxValue
from .base import SkillpointsTuple


def replace_num(s: str):
    return s.replace('1st', 'first').replace('2nd', 'second').replace('3rd', 'third').replace('4th', 'fourth')


@dataclass
class Identifications:
    baseHealth: MinMaxValue
    baseEarthDefence: MinMaxValue
    healthRegen: MinMaxValue
    thorns: MinMaxValue
    reflection: MinMaxValue
    exploding: MinMaxValue
    baseWaterDefence: MinMaxValue
    rawIntelligence: MinMaxValue
    manaRegen: MinMaxValue
    dexterity: MinMaxValue
    rawDexterity: MinMaxValue
    rawThunderMainAttackDamage: MinMaxValue
    mainAttackRange: MinMaxValue
    thunderDefence: MinMaxValue
    baseThunderDamage: MinMaxValue
    baseFireDamage: MinMaxValue
    defence: MinMaxValue
    rawSpellDamage: MinMaxValue
    manaSteal: MinMaxValue
    airDamage: MinMaxValue
    fireDefence: MinMaxValue
    rawStrength: MinMaxValue
    rawDefence: MinMaxValue
    rawAgility: MinMaxValue
    baseDamage: MinMaxValue
    baseEarthDamage: MinMaxValue
    strength: MinMaxValue
    lootBonus: MinMaxValue
    earthDamage: MinMaxValue
    waterDamage: MinMaxValue
    baseThunderDefence: MinMaxValue
    baseFireDefence: MinMaxValue
    baseAirDefence: MinMaxValue
    mainAttackDamage: MinMaxValue
    rawMainAttackDamage: MinMaxValue
    spellDamage: MinMaxValue
    healthRegenRaw: MinMaxValue
    rawAttackSpeed: MinMaxValue
    thunderDamage: MinMaxValue
    fireDamage: MinMaxValue
    rawHealth: MinMaxValue
    lifeSteal: MinMaxValue
    waterDefence: MinMaxValue
    earthMainAttackDamage: MinMaxValue
    fireMainAttackDamage: MinMaxValue
    earthDefence: MinMaxValue
    damage: MinMaxValue
    firstSpellCost: MinMaxValue
    knockback: MinMaxValue
    slowEnemy: MinMaxValue
    poison: MinMaxValue
    xpBonus: MinMaxValue
    agility: MinMaxValue
    elementalSpellDamage: MinMaxValue
    baseAirDamage: MinMaxValue
    walkSpeed: MinMaxValue
    weakenEnemy: MinMaxValue
    sprintRegen: MinMaxValue
    jumpHeight: MinMaxValue
    baseWaterDamage: MinMaxValue
    intelligence: MinMaxValue
    airDefence: MinMaxValue
    rawsecondSpellCost: MinMaxValue
    rawElementalDamage: MinMaxValue
    healingEfficiency: MinMaxValue
    rawDamage: MinMaxValue
    elementalDefence: MinMaxValue
    stealing: MinMaxValue
    thirdSpellCost: MinMaxValue
    secondSpellCost: MinMaxValue
    elementalDamage: MinMaxValue
    sprint: MinMaxValue
    rawMaxMana: MinMaxValue
    rawthirdSpellCost: MinMaxValue
    rawFireMainAttackDamage: MinMaxValue
    earthSpellDamage: MinMaxValue
    airSpellDamage: MinMaxValue
    rawfourthSpellCost: MinMaxValue
    rawFireDamage: MinMaxValue
    rawThunderDamage: MinMaxValue
    rawfirstSpellCost: MinMaxValue
    fourthSpellCost: MinMaxValue
    rawEarthMainAttackDamage: MinMaxValue
    rawAirMainAttackDamage: MinMaxValue
    rawAirDamage: MinMaxValue
    rawWaterSpellDamage: MinMaxValue
    waterSpellDamage: MinMaxValue
    rawThunderSpellDamage: MinMaxValue
    neutralDamage: MinMaxValue
    rawNeutralDamage: MinMaxValue
    rawElementalMainAttackDamage: MinMaxValue
    thunderMainAttackDamage: MinMaxValue
    rawEarthDamage: MinMaxValue
    fireSpellDamage: MinMaxValue
    rawElementalSpellDamage: MinMaxValue
    criticalDamageBonus: MinMaxValue
    rawFireSpellDamage: MinMaxValue
    rawAirSpellDamage: MinMaxValue
    thunderSpellDamage: MinMaxValue
    rawNeutralMainAttackDamage: MinMaxValue
    airMainAttackDamage: MinMaxValue
    rawNeutralSpellDamage: MinMaxValue
    rawWaterDamage: MinMaxValue
    elementalMainAttackDamage: MinMaxValue
    rawEarthSpellDamage: MinMaxValue
    neutralMainAttackDamage: MinMaxValue
    neutralSpellDamage: MinMaxValue
    leveledXpBonus: MinMaxValue
    damageFromMobs: MinMaxValue
    gatherXpBonus: MinMaxValue
    leveledLootBonus: MinMaxValue
    lootQuality: MinMaxValue
    gatherSpeed: MinMaxValue
    rawWaterMainAttackDamage: MinMaxValue
    combatExperience: MinMaxValue
    gatheringExperience: MinMaxValue
    waterMainAttackDamage: MinMaxValue


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

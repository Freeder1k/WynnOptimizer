from ortools.sat.python.cp_model import LinearExpr

from cp_utils.linear_expr_factory import LinearExprFactory
from wynndata.base import SkillpointsTuple


class CPIdentificationValue:
    raw: LinearExpr
    min: LinearExpr
    max: LinearExpr
    abs_max: LinearExpr
    abs_min: LinearExpr

    def __init__(self, lin_expr_fac: LinearExprFactory, name: str):
        self.lin_expr_fac = lin_expr_fac
        self.name = name

    def __getattr__(self, item):
        expr = self.lin_expr_fac.generate(lambda i: getattr(i.identifications[self.name], item),
                                          name=f"identifications.{self.name}.{item}")
        setattr(self, item, expr)
        return expr

    @property
    def avg(self) -> LinearExpr:
        """
        Wrapper for self.min + self.max
        """
        return self.min + self.max


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
    rawAirDamage: CPIdentificationValue
    rawEarthDamage: CPIdentificationValue
    rawFireDamage: CPIdentificationValue
    rawNeutralDamage: CPIdentificationValue
    lootQuality: CPIdentificationValue
    gatherXpBonus: CPIdentificationValue
    gatherSpeed: CPIdentificationValue
    rawWaterMainAttackDamage: CPIdentificationValue
    rawEarthMainAttackDamage: CPIdentificationValue

    def __init__(self, lin_expr_fac: LinearExprFactory):
        self.lin_expr_fac = lin_expr_fac

    def __getattr__(self, item):
        setattr(self, item, CPIdentificationValue(self.lin_expr_fac, item))
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

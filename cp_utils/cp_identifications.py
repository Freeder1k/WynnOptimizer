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
    baseHealth: CPIdentificationValue
    baseEarthDefence: CPIdentificationValue
    healthRegen: CPIdentificationValue
    thorns: CPIdentificationValue
    reflection: CPIdentificationValue
    exploding: CPIdentificationValue
    baseWaterDefence: CPIdentificationValue
    rawIntelligence: CPIdentificationValue
    manaRegen: CPIdentificationValue
    dexterity: CPIdentificationValue
    rawDexterity: CPIdentificationValue
    rawThunderMainAttackDamage: CPIdentificationValue
    mainAttackRange: CPIdentificationValue
    thunderDefence: CPIdentificationValue
    baseThunderDamage: CPIdentificationValue
    baseFireDamage: CPIdentificationValue
    defence: CPIdentificationValue
    rawSpellDamage: CPIdentificationValue
    manaSteal: CPIdentificationValue
    airDamage: CPIdentificationValue
    fireDefence: CPIdentificationValue
    rawStrength: CPIdentificationValue
    rawDefence: CPIdentificationValue
    rawAgility: CPIdentificationValue
    baseDamage: CPIdentificationValue
    baseEarthDamage: CPIdentificationValue
    strength: CPIdentificationValue
    lootBonus: CPIdentificationValue
    earthDamage: CPIdentificationValue
    waterDamage: CPIdentificationValue
    baseThunderDefence: CPIdentificationValue
    baseFireDefence: CPIdentificationValue
    baseAirDefence: CPIdentificationValue
    mainAttackDamage: CPIdentificationValue
    rawMainAttackDamage: CPIdentificationValue
    spellDamage: CPIdentificationValue
    healthRegenRaw: CPIdentificationValue
    rawAttackSpeed: CPIdentificationValue
    thunderDamage: CPIdentificationValue
    fireDamage: CPIdentificationValue
    rawHealth: CPIdentificationValue
    lifeSteal: CPIdentificationValue
    waterDefence: CPIdentificationValue
    earthMainAttackDamage: CPIdentificationValue
    fireMainAttackDamage: CPIdentificationValue
    earthDefence: CPIdentificationValue
    damage: CPIdentificationValue
    firstSpellCost: CPIdentificationValue
    knockback: CPIdentificationValue
    slowEnemy: CPIdentificationValue
    poison: CPIdentificationValue
    xpBonus: CPIdentificationValue
    agility: CPIdentificationValue
    elementalSpellDamage: CPIdentificationValue
    baseAirDamage: CPIdentificationValue
    walkSpeed: CPIdentificationValue
    weakenEnemy: CPIdentificationValue
    sprintRegen: CPIdentificationValue
    jumpHeight: CPIdentificationValue
    baseWaterDamage: CPIdentificationValue
    intelligence: CPIdentificationValue
    airDefence: CPIdentificationValue
    rawsecondSpellCost: CPIdentificationValue
    rawElementalDamage: CPIdentificationValue
    healingEfficiency: CPIdentificationValue
    rawDamage: CPIdentificationValue
    elementalDefence: CPIdentificationValue
    stealing: CPIdentificationValue
    thirdSpellCost: CPIdentificationValue
    secondSpellCost: CPIdentificationValue
    elementalDamage: CPIdentificationValue
    sprint: CPIdentificationValue
    rawMaxMana: CPIdentificationValue
    rawthirdSpellCost: CPIdentificationValue
    rawFireMainAttackDamage: CPIdentificationValue
    earthSpellDamage: CPIdentificationValue
    airSpellDamage: CPIdentificationValue
    rawfourthSpellCost: CPIdentificationValue
    rawFireDamage: CPIdentificationValue
    rawThunderDamage: CPIdentificationValue
    rawfirstSpellCost: CPIdentificationValue
    fourthSpellCost: CPIdentificationValue
    rawEarthMainAttackDamage: CPIdentificationValue
    rawAirMainAttackDamage: CPIdentificationValue
    rawAirDamage: CPIdentificationValue
    rawWaterSpellDamage: CPIdentificationValue
    waterSpellDamage: CPIdentificationValue
    rawThunderSpellDamage: CPIdentificationValue
    neutralDamage: CPIdentificationValue
    rawNeutralDamage: CPIdentificationValue
    rawElementalMainAttackDamage: CPIdentificationValue
    thunderMainAttackDamage: CPIdentificationValue
    rawEarthDamage: CPIdentificationValue
    fireSpellDamage: CPIdentificationValue
    rawElementalSpellDamage: CPIdentificationValue
    criticalDamageBonus: CPIdentificationValue
    rawFireSpellDamage: CPIdentificationValue
    rawAirSpellDamage: CPIdentificationValue
    thunderSpellDamage: CPIdentificationValue
    rawNeutralMainAttackDamage: CPIdentificationValue
    airMainAttackDamage: CPIdentificationValue
    rawNeutralSpellDamage: CPIdentificationValue
    rawWaterDamage: CPIdentificationValue
    elementalMainAttackDamage: CPIdentificationValue
    rawEarthSpellDamage: CPIdentificationValue
    neutralMainAttackDamage: CPIdentificationValue
    neutralSpellDamage: CPIdentificationValue
    leveledXpBonus: CPIdentificationValue
    damageFromMobs: CPIdentificationValue
    gatherXpBonus: CPIdentificationValue
    leveledLootBonus: CPIdentificationValue
    lootQuality: CPIdentificationValue
    gatherSpeed: CPIdentificationValue
    rawWaterMainAttackDamage: CPIdentificationValue
    combatExperience: CPIdentificationValue
    gatheringExperience: CPIdentificationValue
    waterMainAttackDamage: CPIdentificationValue

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

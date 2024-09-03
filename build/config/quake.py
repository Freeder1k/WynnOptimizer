from build.config.base import OptimizerConfig
import build.item
from utils import dmgcalc
from utils import itemfilter


# quake converts all weapon dmg to earth!
# melee % and raw work
# elemental modifiers, only earth

# so first everything into earth and then modifiers! so this should just be a spell mod?
# earth master is not multiplied by 4?? tbh this is insignificant, ill ignore it, other masteries are irrelevant
# weapon powders dont seem to cause issues.
# is still affected by crit
# melee has no speedmod

spellmod = [0, 4, 0, 0, 0, 0]
weapon = build.item.get_weapon("Animosity").set_powders(["e", "e", "e"])
# weapon = build.item.get_weapon("Inferno").set_powders(["e", "f", "e"])
skilltree = '1T-p-1zUfv0' #'1T-p-XUlKY1'
weapon.identifications['rawMainAttackDamage'] += 5 # dagger proficiency skill
mastery = [True, True, False, True, False] # Elemental masteries from skilltree [ETWFA]
base_dmg_max, base_dmg_min = dmgcalc.base_dmg(weapon, spellmod, mastery, melee=True)
spellmodsum = sum(spellmod)

def score(itm: build.item.Item, ) -> float:
    return dmgcalc.avg_dmg(base_dmg_min, base_dmg_max, itm.identifications, spellmodsum, melee=True)


items = list(itm for itm in build.item.get_all_items().values() if score(itm) > score(build.item.NO_ITEM))
items = itemfilter.remove_bad_items(base_dmg_max, items, melee=True, extra=['walkSpeed','manaRegen'])
# items = itemfilter.remove_item(items, 'Writing Growth')
# print(items)
# itemnames = ("Darksteel Full Helm", "Taurus", "Earth Breaker", "Dawnbreak", "Downfall", "Downfall", "Momentum", "Contrast")
# items = []
# for i in itemnames:
#     items.append(build.item.get_item(i))
# https://hppeng-wynn.github.io/builder/?v=8#9_0D80oY0Ek0QR0EE0EE0SL0Ji01jCI-100009Animosity02404010305A0907133-1660D07360-9600E07666-6660F00M01010j013QE0l010Bl0m0202XAu0t013UG0u013C61i1h0011001g10003601000361000361001Z60z0z0+0+0+0+0-1T-p-1zUf43

class DmgConfig(OptimizerConfig):

    def __init__(self):
        super().__init__(items, score)
        self.set_identification_min("manaRegen", -5)
        self.set_identification_min("walkSpeed", 0)
        self.set_identification_max("raw1stSpellCost", 0)
        self.set_identification_max("raw2ndSpellCost", 0)
        self.set_identification_max("raw3rdSpellCost", 0)
        self.set_identification_max("raw4thSpellCost", 0)
        self.set_identification_max("1stSpellCost", 0)
        self.set_identification_max("2ndSpellCost", 0)
        self.set_identification_max("3rdSpellCost", 0)
        self.set_identification_max("4thSpellCost", 0)
        self.set_weapon(weapon)
        self.set_elemental_mastery(mastery)
        self.set_skilltree(skilltree)
        self.set_sdfactor(0)
        self.set_sp_max('str', 150)
        self.set_sp_min('str', 40)
        self.set_sp_max('dex', 150)
        self.set_sp_min('dex', 40)
        self.set_sp_min('def', 50)
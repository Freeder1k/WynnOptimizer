from build.config.base import OptimizerConfig
import build.item
from utils import dmgcalc
from utils import itemfilter


spellmod = [0, 4, 0, 0, 0, 0] # Quake is 400% earth
spellmodsum = sum(spellmod)
# weapon = build.item.get_weapon("Animosity").set_powders(["e", "e", "e"])
# weapon = build.item.get_weapon("Inferno").set_powders(["e", "f", "e"])
weapon = build.item.get_weapon("Oblivion").set_powders(["e", "e", "e", "e"])
skilltree = '1TzZkVsxs20'
weapon.identifications['rawMainAttackDamage'] += 5 # dagger proficiency skill
mastery = [True, True, True, False, False] # Elemental masteries from skilltree [ETWFA]
base_dmg_max, base_dmg_min = dmgcalc.base_dmg(weapon, spellmod, mastery, melee=True)

def score(itm: build.item.Item, ) -> float:
    return dmgcalc.avg_dmg(base_dmg_min, base_dmg_max, itm.identifications, spellmodsum, melee=True)

rel_ids = ['walkSpeed','manaRegen','manaSteal','lifeSteal']

items = list(itm for itm in build.item.get_all_items().values() if (score(itm) > score(build.item.NO_ITEM) or any(itm.identifications[i].max > 0 for i in rel_ids)))
items = itemfilter.remove_bad_items(base_dmg_max, items, melee=True, extra=rel_ids)
items = itemfilter.set_item(items, build.item.get_item('Galleon'))
# print(items)
# itemnames = ("Darksteel Full Helm", "Taurus", "Earth Breaker", "Dawnbreak", "Downfall", "Downfall", "Momentum", "Contrast")
# items = []
# for i in itemnames:
#     items.append(build.item.get_item(i))
# https://hppeng-wynn.github.io/builder/?v=8#9_0D80oY0Ek0QR0EE0EE0SL0Ji01s1f1k0011001g10003601000361000361001Z60z0z0+0+0+0+0-1TzZkVsxs20


class DmgConfig(OptimizerConfig):

    def __init__(self):
        super().__init__(items, score)
        self.set_identification_min("manaRegen", -5)
        self.set_identification_min("manaSteal", 20)
        self.set_identification_min("lifeSteal", 1000)
        self.set_identification_min("walkSpeed", 100)
        # self.set_identification_max("raw1stSpellCost", 0)
        # self.set_identification_max("raw2ndSpellCost", 0)
        # self.set_identification_max("raw3rdSpellCost", 0)
        # self.set_identification_max("raw4thSpellCost", 0)
        # self.set_identification_max("1stSpellCost", 0)
        # self.set_identification_max("2ndSpellCost", 0)
        # self.set_identification_max("3rdSpellCost", 0)
        # self.set_identification_max("4thSpellCost", 0)
        self.set_weapon(weapon)
        self.set_elemental_mastery(mastery)
        self.set_skilltree(skilltree)
        self.set_sdfactor(0)
        self.set_sp_max('str', 150)
        # self.set_sp_min('str', 40)
        self.set_sp_max('dex', 150)
        # self.set_sp_min('dex', 40)
        # self.set_sp_min('def', 65)
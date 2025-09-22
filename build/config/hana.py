from build.config.base import OptimizerConfig
import build.item
from utils import dmgcalc
from utils import itemfilter


spellmod = [1, 0.1, 0.1, 0.1, 0.1, 0.1]  # kinda random but acrobat has a lot of neutral modifiers with a bit of each element sprinkled in
# skilltree = '1TldxagIZu07'  # TODO: actual calculations with skilltree (THIS WILL BE PAIN)
# mastery = [False, False, True, True, True]  # Elemental masteries from skilltree [ETWFA]
weapon = build.item.get_weapon("Hanafubuki")
skilltree = '1Tjdxa+LQK30'
mastery = [False, False, True, True, False]  # Elemental masteries from skilltree [ETWFA]
base_dmg_max, base_dmg_min = dmgcalc.base_dmg(weapon, spellmod, mastery)
spellmodsum = sum(spellmod)


def score(itm: build.item.Item, ) -> float:
    return dmgcalc.avg_dmg(base_dmg_min, base_dmg_max, itm.identifications, spellmodsum)


items = list(itm for itm in build.item.get_all_items().values() if score(itm) > score(build.item.NO_ITEM))
items = itemfilter.remove_bad_items(base_dmg_max, items)
# itemnames = ("Caesura", "Soul Signal", "Chaos-Woven Greaves", "Broken Balance", "Yang", "Yang", "Diamond Hydro Bracelet", "Amanuensis")
# items = []
# for i in itemnames:
#     items.append(build.item.get_item(i))


class DmgConfig(OptimizerConfig):

    def __init__(self):
        super().__init__(items, score)
        # self.set_requirement_max('def', 0)
        # self.set_requirement_max('agi', 0)
        self.set_identification_min("manaRegen", 70)
        self.set_weapon(weapon)
        self.set_elemental_mastery(mastery)
        self.set_skilltree(skilltree)
        self.set_sdfactor(2)
        self.set_sp_max('str', 150)
        # self.set_sp_min('str', 40)
        self.set_sp_max('dex', 150)
        # self.set_sp_min('dex', 40)
        # self.set_sp_min('def', 50)

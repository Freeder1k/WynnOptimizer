import copy

from build.config.base import OptimizerConfig
import build.item
from utils import dmgcalc
from utils import itemfilter


spellmod = [0.3, 0, 0.15, 0.1, 0, 0]  # multihit https://wynnbuilder.github.io/builder/#8_2SG2SH2SI2SJ2SK2SL2SM2SN0Qm00000000001g00001004fI0z0z0+0+0+0+0-ldxagIZu07
# powders = ["t", "t", "t"]
# mastery = [False] + [False, False, False, True, False]  # Elemental masteries from skilltree (ignore first false) [ETWFA]
# weapon = build.item.get_weapon("Cataclysm")
powders = ["w", "w", "w"]
mastery = [False] + [False, False, True, True, True]  # Elemental masteries from skilltree (ignore first false) [ETWFA]
weapon = build.item.get_weapon("Nirvana").set_powders(powders)

base_dmg_max, base_dmg_min = dmgcalc.base_dmg(weapon, spellmod, mastery)
spellmodsum = sum(spellmod)


def score(itm: build.item.Item, ) -> float:
    return dmgcalc.avg_dmg(base_dmg_min, base_dmg_max, itm.identifications, spellmodsum)


items = list(itm for itm in build.item.get_all_items().values() if score(itm) > score(build.item.NO_ITEM))
#items = itemfilter.set_item_of_type(items, build.item.get_item("Stratosphere"), 'chestplate')
items = itemfilter.remove_bad_items(base_dmg_max, items)
extra_rings = []
for item in items:
    if item.type == 'ring':
        item2 = copy.deepcopy(item)
        item2.type = 'ring_'
        extra_rings.append(item2)
items += extra_rings


class DmgConfig(OptimizerConfig):

    def __init__(self):
        super().__init__(items, score)
        self.set_requirement_max('def', 0)
        self.set_requirement_max('agi', 0)
        self.set_identification_min("manaRegen", 0)
        self.set_weapon(weapon)
        self.set_elemental_mastery(mastery)

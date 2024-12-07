from build.config.base import OptimizerConfig
import build.item
from utils import dmgcalc
from utils import itemfilter


spellmod = [7, 0, 0, 0.2, 0, 0]
weapon = build.item.get_weapon("Resonance").set_powders(["w", "w", "w"])
skilltree = '1T-xUqzOkL0'
mastery = [True, False, True, True, False]  # Elemental masteries from skilltree [ETWFA]
base_dmg_max, base_dmg_min = dmgcalc.base_dmg(weapon, spellmod, mastery)
spellmodsum = sum(spellmod)


def score(itm: build.item.Item, ) -> float:
    return dmgcalc.avg_dmg(base_dmg_min, base_dmg_max, itm.identifications, spellmodsum)

# Not compatible
# quilted_carapace = build.item.Item.from_api_json("Quilted Carapace",
#                                                 {
#                                                         "type": "armour",
#                                                         "armourType": "chestplate",
#                                                         "requirements": {
#                                                             "level": 90,
#                                                             "intelligence": 85,
#                                                             "defence": 85,
#                                                         },
#                                                         "identifications": {}})

items = list(itm for itm in build.item.get_all_items().values() if score(itm) > score(build.item.NO_ITEM))
items = itemfilter.remove_bad_items(base_dmg_max, items)
items = itemfilter.remove_item(items, "Blue Mask")
items = itemfilter.set_item(items, build.item.get_item("Brilliant Diamond Chestplate"))
items = itemfilter.set_item(items, build.item.get_item("Crusade Sabatons"))


class DmgConfig(OptimizerConfig):

    def __init__(self):
        super().__init__(items, score)
        # self.set_requirement_max('def', 0)
        # self.set_requirement_max('agi', 0)
        # self.set_identification_min("manaRegen", 30)
        self.set_weapon(weapon)
        self.set_elemental_mastery(mastery)
        self.set_skilltree(skilltree)
        self.set_sdfactor(2)
        # self.set_sp_max('str', 150)
        self.set_sp_min('str', 85)
        self.set_sp_min('int', 85)
        # self.set_sp_max('dex', 150)
        # self.set_sp_min('dex', 40)
        self.set_sp_min('def', 115)

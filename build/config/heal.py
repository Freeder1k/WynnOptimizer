from build.config.base import OptimizerConfig
import build.item
from utils import itemfilter


weapon = build.item.get_weapon("Absolution")
skilltree = '1Tj-RR-XT1'
mastery = [True, True, True, False, True] # Elemental masteries from skilltree [ETWFA]

def score(itm: build.item.Item, ) -> float:
    return ((535 + itm.identifications['baseHealth'].max + itm.identifications['rawHealth'].max)*0.18
            * (1 + itm.identifications['healingEfficiency'].max/100)
            * (1 + min(itm.identifications['waterDamage'].max,250)/100*0.3))


def score_model(model, items, item_vars, sp_assignment_vars):
    healths = []
    healeffs = []
    waterdmgs = [45]
    for itm, x in zip(items + [weapon], item_vars + [1]):
        healths.append((itm.identifications['baseHealth'].max + itm.identifications['rawHealth'].max) * x)
        healeffs.append(itm.identifications['healingEfficiency'].max * x)
        waterdmgs.append(itm.identifications['waterDamage'].max * 3 * x)

    health = model.new_int_var(0, 50000, "health")
    model.add(health == sum(healths) + 535)
    healeff = model.new_int_var(-500, 500, "healeff")
    model.add(healeff == sum(healeffs) + 100)
    waterdmg = model.new_int_var(-1500, 1500, "waterdmg")
    model.add_min_equality(waterdmg, [1225, sum(waterdmgs) + 1000])

    heal = model.new_int_var(0, 100000000000, "heal")
    model.add_multiplication_equality(heal, [health, healeff, waterdmg])

    return heal


rel_ids = ['rawHealth','baseHealth','healingEfficiency','waterDamage'] + ['manaRegen','raw3rdSpellCost','3rdSpellCost']

items = list(itm for itm in build.item.get_all_items().values() if (score(itm) > score(build.item.NO_ITEM) or any(itm.identifications[i].max > 0 for i in rel_ids)))
items = itemfilter.remove_bad_items([0,0,0,0,0,0], items, melee=True, extra=rel_ids)
# items = itemfilter.set_item(items, build.item.get_item('Earth Breaker'))
# print(items)
# itemnames = ("Darksteel Full Helm", "Taurus", "Earth Breaker", "Dawnbreak", "Downfall", "Downfall", "Momentum", "Contrast")
# items = []
# for i in itemnames:
#     items.append(build.item.get_item(i))


class DmgConfig(OptimizerConfig):

    def __init__(self):
        super().__init__(items, score)
        self.set_model_function(score_model)
        self.set_useModelFunction(True)
        # self.set_identification_min("manaRegen", 40)
        # self.set_identification_max("raw3rdSpellCost", 0)
        # self.set_identification_max("3rdSpellCost", 0)
        self.set_weapon(weapon)
        self.set_skilltree(skilltree)
        self.set_elemental_mastery(mastery)
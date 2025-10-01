from build.config.base import OptimizerConfig
import build.item
from utils import dmgcalc
from utils import itemfilter
from utils import regression
import pandas as pd
import numpy as np


spellmod = [0.15, 0.05, 0, 0, 0.1, 0.05]  # Smoke bomb
melee = False
weapon = build.item.get_weapon("Grimtrap").set_powders(["e","e","e"])
skilltree = ''
mastery = [True, True, False, True, False]  # Elemental masteries from skilltree [ETWFA]
base_dmg_max, base_dmg_min = dmgcalc.base_dmg(weapon, spellmod, mastery)
spellmodsum = sum(spellmod)

requirements_min = [
    ("manaRegen", 40),
    ("lifeSteal", 1000),
    ("walkSpeed", 50)
]
requirements_max = []
req_ids = [req[0] for req in requirements_min]
relevant_ids = regression.relevant_ids(base_dmg_max, melee=melee)
sp_ids = ["rawStrength", "rawDexterity", "rawIntelligence", "rawDefence", "rawAgility"]

def score(itm: build.item.Item, ) -> float:
    return dmgcalc.avg_dmg(base_dmg_min, base_dmg_max, itm.identifications, spellmodsum)


items = list(itm for itm in build.item.get_all_items().values() if score(itm) > score(build.item.NO_ITEM) or any(itm.identifications[r].max > 0 for r in req_ids))
items = itemfilter.remove_bad_items(base_dmg_max, items, melee=melee, extra=req_ids)
# items = [itm for itm in items if not itm.name == "Broken Balance"]
items = [itm for itm in items if not itm.name == "Titanomachia"]
items = itemfilter.set_item(items, build.item.get_item("Crusade Sabatons"))

def score_model(model, items, item_vars, sp_vars):
    print("Generating training data")
    X_random, y_random = regression.generate_valid_dataset(weapon, items, score, mastery, relevant_ids + sp_ids + ['freesp','itmscore'], n=5000)
    # X_data, y_data = regression.get_dataset(weapon, 'output/results.txt', score, mastery, relevant_ids + sp_ids + ['freesp','itmscore'], n=5000, random=True)
    # X, y = pd.concat([X_data, X_random]), np.concatenate([y_data, y_random])
    X, y = X_random, y_random
    print("Training regression")
    net = regression.train_model(X, y)
    net = regression.quantize_model(net)
    mins = net.named_steps["scaler"].min_
    scales = net.named_steps["scaler"].scale_

    # Skillpoints
    skillpoints = [0,0,0,0,0,0]
    free_sp = 204 - sum(sp_vars) # probably dont need this
    item_sp = [] # This array represents the total skillpoints of a build
    for i in range(5):
        a = [weapon.identifications[dmgcalc.skillPoints[i+1]].max, sp_vars[i]]
        for itm, x in zip(items, item_vars):
            if itm.identifications[dmgcalc.skillPoints[i+1]].max != 0:
                a.append(itm.identifications[dmgcalc.skillPoints[i+1]].max * x)
        item_sp.append(sum(a)*int(scales[-7+i]) + int(mins[-7+i]))
    item_sp.append(free_sp)

    item_ids = []
    for i, id in enumerate(relevant_ids):
        a = []
        for itm, x in zip(items + [weapon], item_vars + [1]):
            if itm.identifications[id].max != 0:
                a.append(itm.identifications[id].max * x)
        item_ids.append(sum(a)*int(scales[i]) + int(mins[i]))

    itemscores = [sum(int(score(itm))*x for itm, x in zip(items, item_vars))]

    X = item_ids + item_sp + itemscores

    weights = net.named_steps["model"].coefs_
    biases = net.named_steps["model"].intercepts_
    for W, b in zip(weights, biases):
        X_ = []
        for i in range(W.shape[1]):
            X_.append(sum(x*int(w) for x, w in zip(X, W[:, i])) + int(b[i]))
        X = X_

    return sum(X)


class DmgConfig(OptimizerConfig):

    def __init__(self):
        super().__init__(items, score)
        self.set_model_function(score_model)
        self.set_useModelFunction(True)
        # self.set_requirement_max('def', 0)
        # self.set_requirement_max('agi', 0)
        self.add_lower_bound(lambda itm: itm.identifications['baseHealth'].max + itm.identifications['rawHealth'].max, 10000)
        for req in requirements_min:
            self.set_identification_min(*req)
        for req in requirements_max:
            self.set_identification_max(*req)
        self.set_weapon(weapon)
        self.set_elemental_mastery(mastery)
        self.set_skilltree(skilltree)
        # self.set_sp_max('str', 150)
        self.set_sp_min('int', 40)
        # self.set_sp_max('dex', 150)
        # self.set_sp_min('dex', 40)
        self.set_sp_min('def', 60)
        # self.set_sp_min('agi', 0)

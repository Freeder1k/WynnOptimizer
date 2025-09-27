from build.config.base import OptimizerConfig
import build.item
from utils import dmgcalc
from utils import itemfilter
from utils import aproxdmg


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
relevant_ids = aproxdmg.relevant_ids(base_dmg_max)
sp_ids = ["rawStrength", "rawDexterity", "rawIntelligence", "rawDefense", "rawAgility"]


def score_model(model, items, item_vars, sp_vars):
    print("Generating training data")
    X, y = aproxdmg.generate_valid_dataset(weapon, items, score, mastery, relevant_ids + sp_ids, n=10000)
    print("Training regression")
    net = aproxdmg.train_model(X, y)
    net = aproxdmg.quantize_model(net)
    mins = net.named_steps["scaler"].min_
    scales = net.named_steps["scaler"].scale_

    # Skillpoints
    skillpoints = [0,0,0,0,0,0]
    # free_sp = 204 - sum(sp_vars) # probably dont need this
    item_sp = [] # This array represents the total skillpoints of a build
    for i in range(5):
        a = [weapon.identifications[dmgcalc.skillPoints[i+1]].max, sp_vars[i]]
        for itm, x in zip(items, item_vars):
            if itm.identifications[dmgcalc.skillPoints[i+1]].max != 0:
                a.append(itm.identifications[dmgcalc.skillPoints[i+1]].max * x)
        item_sp.append(sum(a)*int(scales[-5+i]) + int(mins[-5+i]))

    item_ids = []
    for i, id in enumerate(relevant_ids):
        a = []
        for itm, x in zip(items + [weapon], item_vars + [1]):
            if itm.identifications[id].max != 0:
                a.append(itm.identifications[id].max * x)
        item_ids.append(sum(a)*int(scales[i]) + int(mins[i]))

    X = item_ids + item_sp

    weights = net.named_steps["mlp"].coefs_
    biases = net.named_steps["mlp"].intercepts_
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
        self.add_lower_bound(lambda itm: itm.identifications['baseHealth'].max + itm.identifications['rawHealth'].max, 5000)
        self.set_identification_min("manaRegen", 60)
        self.set_weapon(weapon)
        self.set_elemental_mastery(mastery)
        self.set_skilltree(skilltree)
        self.set_sdfactor(2)
        # self.set_sp_max('str', 150)
        # self.set_sp_min('str', 40)
        # self.set_sp_max('dex', 150)
        # self.set_sp_min('dex', 40)
        # self.set_sp_min('def', 50)

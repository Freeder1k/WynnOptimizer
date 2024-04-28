import time

import numpy as np
import scipy.optimize as opt

from crafting import ingredient, base_recipes
from crafting.config.base import LinearOptimizerConfigBase


def sp_req_sum(ingr: ingredient.Ingredient):
    return (ingr.requirements.strength + ingr.requirements.dexterity + ingr.requirements.intelligence
            + ingr.requirements.defence + ingr.requirements.agility)


def true_indx(lst):
    return [i for i, x in enumerate(lst) if x == 1][0]


def optimize(cfg: LinearOptimizerConfigBase):
    t = time.time()
    mods = cfg.mods
    mod_count = len(mods)
    ingrs_flat = [ingr * m for m in mods for ingr in cfg.ingredients]
    c = [-cfg.score(ingr) for ingr in ingrs_flat]
    A_ub = []
    b_ub = []
    if cfg.profession in base_recipes.item_profs:
        A_ub.append([-ingr.durability // 1000 for ingr in ingrs_flat])
        b_ub.append(-(cfg.min_durability - 735))
    else:
        A_ub.append([-ingr.charges for ingr in ingrs_flat])
        b_ub.append(-(cfg.min_charges - 0))
        A_ub.append([-ingr.duration for ingr in ingrs_flat])
        b_ub.append(-(cfg.min_duration - 1344))

    A_ub.append([ingr.requirements.strength for ingr in ingrs_flat])
    b_ub.append(cfg.sp_constr.strength)
    A_ub.append([ingr.requirements.dexterity for ingr in ingrs_flat])
    b_ub.append(cfg.sp_constr.dexterity)
    A_ub.append([ingr.requirements.intelligence for ingr in ingrs_flat])
    b_ub.append(cfg.sp_constr.intelligence)
    A_ub.append([ingr.requirements.defence for ingr in ingrs_flat])
    b_ub.append(cfg.sp_constr.defence)
    A_ub.append([ingr.requirements.agility for ingr in ingrs_flat])
    b_ub.append(cfg.sp_constr.agility)
    A_ub.append([sp_req_sum(ingr) for ingr in ingrs_flat])
    b_ub.append(cfg.sp_constr.total)

    for identification, req in cfg.id_reqs.items():
        A_ub.append([-ingr.identifications[identification].max for ingr in ingrs_flat])
        b_ub.append(-req)

    ing_count = len(cfg.ingredients)
    A_eq = np.zeros((mod_count, ing_count * mod_count), dtype=int)
    for i in range(mod_count):
        A_eq[i][i * ing_count: (i + 1) * ing_count] = 1

    b_eq = [1] * mod_count

    # # print(time.time() - t)
    # t = time.time()
    # print("solving ilp")
    res = opt.linprog(c, A_ub, b_ub, A_eq, b_eq, bounds=(0, 1), integrality=1)
    # print(time.time() - t)

    # print([cfg.ingredients[i % ing_count].name for i, x in enumerate(res.x) if x == 1])
    # print(res.fun)

    res_score = -res.fun if res.success else 0
    res_ingrs = [cfg.ingredients[i % ing_count] for i, x in enumerate(res.x) if x == 1] if res.success else []

    return res_score, res_ingrs

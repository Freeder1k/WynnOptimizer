from dataclasses import dataclass
from typing import Callable

import numpy as np
import scipy.optimize as opt

from crafting import ingredient, base_recipes


@dataclass
class MaxSPLoadout:
    str: int
    dex: int
    intl: int
    defn: int
    agi: int
    total: int


def sp_req_sum(ingr: ingredient.Ingredient):
    return (ingr.requirements.strength + ingr.requirements.dexterity + ingr.requirements.intelligence
            + ingr.requirements.defence + ingr.requirements.agility)

def true_indx(lst):
    return [i for i, x in enumerate(lst) if x == 1][0]

def optimize(score_fun: Callable[[ingredient.Ingredient], float], ingredients: list[ingredient.Ingredient],
             mods: list[float], profession: str, spl: MaxSPLoadout, id_reqs: dict[str, int]):
    mods = [round(m * 100) for m in mods]
    ingrs_flat = [ingr * m for m in mods for ingr in ingredients]
    c = [-score_fun(ingr) for ingr in ingrs_flat]
    A_ub = []
    b_ub = []
    if profession in base_recipes.item_profs:
        A_ub.append([-ingr.durability // 1000 for ingr in ingrs_flat])
        b_ub.append(-(30 - 735))
    else:
        A_ub.append([-ingr.charges for ingr in ingrs_flat])
        b_ub.append(-(3 - 0))
        A_ub.append([-ingr.duration for ingr in ingrs_flat])
        b_ub.append(-(60 - 1344))

    A_ub.append([ingr.requirements.strength for ingr in ingrs_flat])
    b_ub.append(spl.str)
    A_ub.append([ingr.requirements.dexterity for ingr in ingrs_flat])
    b_ub.append(spl.dex)
    A_ub.append([ingr.requirements.intelligence for ingr in ingrs_flat])
    b_ub.append(spl.intl)
    A_ub.append([ingr.requirements.defence for ingr in ingrs_flat])
    b_ub.append(spl.defn)
    A_ub.append([ingr.requirements.agility for ingr in ingrs_flat])
    b_ub.append(spl.agi)
    A_ub.append([sp_req_sum(ingr) for ingr in ingrs_flat])
    b_ub.append(spl.total)

    for identification, req in id_reqs.items():
        A_ub.append([-ingr.identifications[identification].max for ingr in ingrs_flat])
        b_ub.append(-req)

    ing_count = len(ingredients)
    A_eq = np.zeros((6, ing_count*6), dtype=int)
    for i in range(6):
        A_eq[i][i * ing_count: (i + 1) * ing_count] = 1

    print(A_eq)

    b_eq = [1] * 6

    print("solving ilp")
    res = opt.linprog(c, A_ub, b_ub, A_eq, b_eq, bounds=(0, 1), integrality=1)

    print([ingredients[i%ing_count].name for i, x in enumerate(res.x) if x == 1])


    return res.x, res.fun

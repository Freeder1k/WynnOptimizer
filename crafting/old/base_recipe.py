import math
import signal
import sys
from multiprocessing import Pool

import numba.cuda
import numpy
from numba import jit, cuda

from core.optimizer import bruteForce
from crafting import ingredient, recipe


def calc_base_recipes(ingredients: list[ingredient.Ingredient],
                      pool_size: int = 4,
                      strict=False) -> dict[tuple[int, ...], recipe.Recipe]:
    """
    Calculate the base recipes for the given ingredients.
     These ingredients should only include effectiveness and durability ingredients without any undesired requirements/ids.
    :param ingredients: The list of ingredients to use.
    :param pool_size: The number of processes to use.
    :param strict: If True, only exact sub-recipes will be removed.
    :return: Dictionary of tuples of effectiveness values of the free slots mapped to recipes.
    """
    ingredients.append(ingredient.NO_INGREDIENT)

    with Pool(pool_size, initializer=_initializer) as p:
        try:
            results = p.starmap(_get_combos, [(i, ingredients) for i in ingredients])
        except KeyboardInterrupt:
            p.terminate()
            raise KeyboardInterrupt

    res = {}
    for r in results:
        for k, v in r.items():
            if k not in res or v.build().durability > res[k].build().durability:
                res[k] = v

    if () in res:
        del res[()]

    print(f"Found {len(res)} unique recipes.")
    combo_amount = len(res)

    combos = sorted([(c, r.build().durability) for c, r in res.items() if sum((abs(x) for x in c)) >= 300],
                    key=lambda x: x[1],
                    reverse=True)

    print(f"Removed {combo_amount - len(combos)} bad recipes. -> Now {len(combos)} unique recipes.")
    combo_amount = len(combos)

    if not strict:
        combos2 = [combos[0]]
        for i in range(1, len(combos)):
            c1, dura1 = combos[i]
            passes = True
            for c2, dura2 in combos2:
                if dura1 > dura2:
                    break
                if len(c1) > len(c2):
                    continue
                if _is_worse_combo(c1, c2):
                    passes = False
                    break
            for j in range(i + 1, len(combos)):
                c2, dura2 = combos[j]
                if dura1 > dura2:
                    break
                if len(c1) > len(c2):
                    continue
                if _is_worse_combo(c1, c2):
                    passes = False
                    break

            if passes:
                combos2.append((c1, dura1))
        combos = sorted([c[0] for c in combos2], key=lambda x: sum(x), reverse=True)
    else:
        combos = {c: dura for c, dura in reversed(combos)}
        for combo, dura in list(combos.items()):
            for sub_combo in bruteForce.generate_all_subpermutations(*combo, ordered=True):
                if sub_combo in combos and combos[sub_combo] <= dura:
                    del combos[sub_combo]
        combos = sorted([c for c in combos.keys()], key=lambda x: sum(x), reverse=True)

    print(f"Removed {combo_amount - len(combos)} sub-recipes. -> Now {len(combos)} unique combos.")

    res = {c: res[c] for c in combos}
    _to_csv(res)

    return res


def _is_worse_combo(c1: tuple[int, ...], c2: tuple[int, ...]) -> bool:
    """
    Compare two combos. c1 is worse than c2 if all values are worse or equal.
    """
    if len(c1) > len(c2):
        return False

    n1 = tuple(x for x in c1 if x < 0)
    n2 = tuple(x for x in c2 if x < 0)
    p1 = tuple(x for x in c1 if x >= 0)
    p2 = tuple(x for x in c2 if x >= 0)
    if len(n1) > len(n2) or len(p1) > len(p2):
        return False

    n2 = n2[:len(n1)]
    p2 = p2[len(p2) - len(p1):]

    return (all(n1[i] >= n2[i] for i in range(len(n1)))
            and all(p1[i] <= p2[i] for i in range(len(p1))))


def _pad_r(t: tuple, n: int, val) -> tuple:
    return t + (val,) * (n - len(t))


def _to_csv(combos: dict[tuple[int, ...], recipe.Recipe]):
    with open("combos.csv", "w", encoding='utf8') as f:
        f.write("Combo,,,,,,Durability,I1,I2,I3,I4,I5,I6\n")
        for k, v in combos.items():
            f.write(
                f"{','.join(_pad_r(tuple(map(str, k)), 6, ''))},{(v.build().durability + 735000) // 1000},{','.join(map(str, v.ingredients))}\n")


async def from_csv():
    combos = {}
    with open("combos.csv", "r", encoding='utf8') as f:
        f.readline()
        for line in f:
            parts = line.strip().split(',')
            combo = tuple([int(val) for val in parts[:6] if val != ''])
            # durability = int(parts[6])
            ings = [ingredient.NO_INGREDIENT if name == 'No Ingredient' else await ingredient.get_ingredient(name) for
                    name in parts[7:]]
            combos[combo] = recipe.Recipe(*ings)
    return combos


def _initializer():
    signal.signal(signal.SIGINT, lambda: None)


def _get_combos(first_ing, ingredients) -> dict[tuple[int, ...], recipe.Recipe]:
    combos = {}

    for combination in bruteForce.generate_all_permutations(5, *ingredients, repeat=True):
        r = recipe.Recipe(first_ing, *combination)

        mods = r.calculate_modifiers()

        effs = []

        for i in range(6):
            if r.ingredients[i].name != "No Ingredient":
                continue

            effs.append(mods[i])

        effs = tuple(sorted(effs))

        if effs not in combos or r.build().durability > combos[effs].build().durability:
            combos[effs] = r

    return combos

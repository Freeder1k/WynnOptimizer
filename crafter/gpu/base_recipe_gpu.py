import itertools
import math
import time

import cupy
import numba
import numpy as np
from numba import cuda

from crafter import ingredient, recipe
from crafter.crafter import _replace_no_ing


# ingredient format:
# charges,                      # 0
# duration,                     # 1
# durability,                   # 2
# requirements.strength,        # 3
# requirements.dexterity,       # 4
# requirements.intelligence,    # 5
# requirements.defence,         # 6
# requirements.agility,         # 7
# modifiers.left,               # 8
# modifiers.right,              # 9
# modifiers.above,              # 10
# modifiers.under,              # 11
# modifiers.touching,           # 12
# modifiers.notTouching,        # 13
# id1.min                       # 14
# id1.max                       # 15
# id2.min                       # 16
# id2.max                       # 17
# id3.min                       # 18
# id3.max                       # 19
# id4.min                       # 20
# id4.max                       # 21
# id5.min                       # 22
# id5.max                       # 23


@cuda.jit(device=True)
def grid_pos(pos):
    x = pos & 1
    y = pos >> 1
    return x, y


@cuda.jit(device=True)
def flat_pos(x, y):
    if x < 0 or y < 0 or x >= 2 or y >= 3:
        return -1
    return y * 2 + x


@cuda.jit(device=True)
def add_maybe(vec, val, i):
    if i != -1:
        vec[i] += val


@cuda.jit(device=True)
def apply_modifier(effectiveness_vec, ingredient, pos):
    for i in range(6):
        effectiveness_vec[i] += ingredient[13]

    x, y = grid_pos(pos)

    add_maybe(effectiveness_vec,
              ingredient[8] + ingredient[12] - ingredient[13],
              flat_pos(x - 1, y))
    add_maybe(effectiveness_vec,
              ingredient[9] + ingredient[12] - ingredient[13],
              flat_pos(x + 1, y))

    add_maybe(effectiveness_vec,
              ingredient[10] + ingredient[12] - ingredient[13],
              flat_pos(x, y - 1))
    add_maybe(effectiveness_vec,
              ingredient[10],
              flat_pos(x, y - 2))

    add_maybe(effectiveness_vec,
              ingredient[11] + ingredient[12] - ingredient[13],
              flat_pos(x, y + 1))
    add_maybe(effectiveness_vec,
              ingredient[11],
              flat_pos(x, y + 2))

    effectiveness_vec[flat_pos(x, y)] -= ingredient[13]


@cuda.jit(device=True)
def score(charges, duration, durability, req_strength, req_dexterity, req_intelligence, req_defence, req_agility,
          id1_min, id1_max, id2_min, id2_max, id3_min, id3_max, id4_min, id4_max, id5_min, id5_max):
    return max(0, id1_max * 1000 + (durability + 735000) // 1000)


@cuda.jit(device=True)
def constraints(charges, duration, durability, req_strength, req_dexterity, req_intelligence, req_defence, req_agility,
                id1_min, id1_max, id2_min, id2_max, id3_min, id3_max, id4_min, id4_max, id5_min, id5_max):
    return (durability > -735000 + 10000
            and req_intelligence <= 150
            and id1_max > 0)


@cuda.jit(device=True)
def calc_recipe_score(recipe, recipe_len, effectiveness_vec):
    charges = 0
    duration = 0
    durability = 0
    req_strength = 0
    req_dexterity = 0
    req_intelligence = 0
    req_defence = 0
    req_agility = 0
    id1_min = 0
    id1_max = 0
    id2_min = 0
    id2_max = 0
    id3_min = 0
    id3_max = 0
    id4_min = 0
    id4_max = 0
    id5_min = 0
    id5_max = 0

    for i in range(recipe_len):
        ingr = recipe[i]
        charges += ingr[0]
        duration += ingr[1]
        durability += ingr[2]
        req_strength += ingr[3] * effectiveness_vec[i] // 100
        req_dexterity += ingr[4] * effectiveness_vec[i] // 100
        req_intelligence += ingr[5] * effectiveness_vec[i] // 100
        req_defence += ingr[6] * effectiveness_vec[i] // 100
        req_agility += ingr[7] * effectiveness_vec[i] // 100
        if effectiveness_vec[i] > 0:
            id1_min += ingr[14] * effectiveness_vec[i] // 100
            id1_max += ingr[15] * effectiveness_vec[i] // 100
            id2_min += ingr[16] * effectiveness_vec[i] // 100
            id2_max += ingr[17] * effectiveness_vec[i] // 100
            id3_min += ingr[18] * effectiveness_vec[i] // 100
            id3_max += ingr[19] * effectiveness_vec[i] // 100
            id4_min += ingr[20] * effectiveness_vec[i] // 100
            id4_max += ingr[21] * effectiveness_vec[i] // 100
            id5_min += ingr[22] * effectiveness_vec[i] // 100
            id5_max += ingr[23] * effectiveness_vec[i] // 100
        elif effectiveness_vec[i] < 0:
            id1_min += ingr[15] * effectiveness_vec[i] // 100
            id1_max += ingr[14] * effectiveness_vec[i] // 100
            id2_min += ingr[17] * effectiveness_vec[i] // 100
            id2_max += ingr[16] * effectiveness_vec[i] // 100
            id3_min += ingr[19] * effectiveness_vec[i] // 100
            id3_max += ingr[18] * effectiveness_vec[i] // 100
            id4_min += ingr[21] * effectiveness_vec[i] // 100
            id4_max += ingr[20] * effectiveness_vec[i] // 100
            id5_min += ingr[23] * effectiveness_vec[i] // 100
            id5_max += ingr[22] * effectiveness_vec[i] // 100

    if not constraints(charges, duration, durability, req_strength, req_dexterity, req_intelligence, req_defence,
                       req_agility, id1_min, id1_max, id2_min, id2_max, id3_min, id3_max, id4_min, id4_max, id5_min,
                       id5_max):
        return 0

    return score(charges, duration, durability, req_strength, req_dexterity, req_intelligence, req_defence, req_agility,
                 id1_min, id1_max, id2_min, id2_max, id3_min, id3_max, id4_min, id4_max, id5_min, id5_max)


def get_effectiveness_indx(ing_count, effectivenesses, pos):
    i = 0
    while pos > ing_count ** effectivenesses[i][0]:
        if i >= len(effectivenesses) - 1:
            return -1, 0
        i += 1
        pos //= ing_count ** effectivenesses[i][0]
    return i, pos


get_effectiveness_indx_cuda = cuda.jit(get_effectiveness_indx, device=True)


def get_recipe(ingredients, pos):
    base = len(ingredients)
    i1 = ingredients[pos % base]
    pos //= base
    i2 = ingredients[pos % base]
    pos //= base
    i3 = ingredients[pos % base]
    pos //= base
    i4 = ingredients[pos % base]
    pos //= base
    i5 = ingredients[pos % base]
    pos //= base
    i6 = ingredients[pos % base]
    return i1, i2, i3, i4, i5, i6


get_recipe_cuda = cuda.jit(get_recipe, device=True)


@cuda.jit
def scoring_kernel(ingredients, scores, offset, perm_amt, score_min):
    pos = cuda.grid(1)
    if pos < scores.shape[0]:
        if pos + offset >= perm_amt:
            scores[pos] = 0
            return
        recipe = get_recipe_cuda(ingredients, pos + offset)

        effectiveness_vec = cuda.local.array(shape=6, dtype=numba.intc)
        for i in range(6):
            effectiveness_vec[i] = 100

        for i in range(6):
            apply_modifier(effectiveness_vec, recipe[i], i)

        r_score = calc_recipe_score(recipe, 6, effectiveness_vec)
        if r_score > score_min:
            scores[pos] = r_score
        else:
            scores[pos] = 0


@cuda.jit(device=True)
def get_effectiveness_tuple(effectivenesses, indx):
    return effectivenesses[indx][1], effectivenesses[indx][2], effectivenesses[indx][3], effectivenesses[indx][4], \
        effectivenesses[indx][5], effectivenesses[indx][6]


@cuda.jit(device=True)
def recipe_from_base(base, mod_ingrs, ingrs):
    j = 0
    i = 0
    if base[i] < 0:
        i1 = ingrs[j]
        j += 1
    else:
        i1 = mod_ingrs[i]
    i += 1
    if base[i] < 0:
        i2 = ingrs[j]
        j += 1
    else:
        i2 = mod_ingrs[i]
    i += 1
    if base[i] < 0:
        i3 = ingrs[j]
        j += 1
    else:
        i3 = mod_ingrs[i]
    i += 1
    if base[i] < 0:
        i4 = ingrs[j]
        j += 1
    else:
        i4 = mod_ingrs[i]
    i += 1
    if base[i] < 0:
        i5 = ingrs[j]
        j += 1
    else:
        i5 = mod_ingrs[i]
    i += 1
    if base[i] < 0:
        i6 = ingrs[j]
        j += 1
    else:
        i6 = mod_ingrs[i]
    return i1, i2, i3, i4, i5, i6


@cuda.jit
def scoring_kernel2(ingredients, effectivenesses, effectiveness_ingrs, base_recipes, scores, offset, score_min):
    pos = cuda.grid(1)
    if pos < scores.shape[0]:
        eff_indx, recipe_pos = get_effectiveness_indx_cuda(len(ingredients), effectivenesses, pos + offset)
        if eff_indx == -1:
            scores[pos] = 0
            return

        r = get_recipe_cuda(ingredients, recipe_pos)
        r = recipe_from_base(base_recipes[eff_indx], effectiveness_ingrs, r)

        effectiveness_vec = cuda.local.array(shape=6, dtype=numba.intc)
        for i in range(6):
            effectiveness_vec[i] = 100

        for i in range(6):
            apply_modifier(effectiveness_vec, r[i], i)

        r_score = calc_recipe_score(r, 6, effectiveness_vec)
        if r_score > score_min:
            scores[pos] = r_score
        else:
            scores[pos] = 0


def homogenize(t, n):
    return (len(t),) + tuple(t) + (0,) * (n - len(t))


def get_best_recipes_gpu(ingredients: list[ingredient.Ingredient], combos: dict[tuple[int, ...], recipe.Recipe] = None,
                         ) -> list[recipe.Recipe]:
    if combos is None:
        combos = {(100,) * 6: recipe.Recipe(*((ingredient.NO_INGREDIENT,) * 6))}

    effectivenesses = list(combos.keys())

    effectivenesses = [homogenize(e, 6) for e in effectivenesses]
    effectiveness_ingredients = itertools.chain(*[r.ingredients for r in combos.values()])
    effectiveness_ingredients = list({i.name: i for i in effectiveness_ingredients}.values())
    effectiveness_ingr_indices = {i.name: idx for idx, i in enumerate(effectiveness_ingredients)}

    permutation_amt = (sum(len(ingredients) ** e[0] for e in effectivenesses))
    batch_size = min(2 ** 26, permutation_amt)

    print(f"Total permutation amount: {permutation_amt}")
    ingredients_array = np.array([i.to_np_array("rawHealth", "", "", "", "") for i in ingredients], dtype=np.intc)

    effectivenesses_array = np.array(effectivenesses, dtype=np.short)
    effectiveness_ingredients_array = np.array(
        [i.to_np_array("rawHealth", "", "", "", "") for i in effectiveness_ingredients], dtype=np.intc)
    base_recipes_array = np.array(
        [[effectiveness_ingr_indices.get(i.name, -1) for i in r.ingredients] for r in combos.values()], dtype=np.intc)

    device_ingreds = cuda.to_device(ingredients_array)
    device_effectivenesses = cuda.to_device(effectivenesses_array)
    device_effectiveness_ingredients = cuda.to_device(effectiveness_ingredients_array)
    device_base_recipes = cuda.to_device(base_recipes_array)

    scores = cupy.empty(batch_size, dtype=np.uint)

    batch_count = math.ceil(permutation_amt / batch_size)
    threadsperblock = 256
    blockspergrid = math.ceil(batch_size / threadsperblock)

    total_best = []

    scoring_time = 0
    zero_time = 0
    sort_time = 0
    select_time = 0

    for offset in range(0, permutation_amt, batch_size):
        score_min = 0 if len(total_best) < 20 else total_best[-1][0]
        print(
            f"\rCalculating scores for batch {offset // batch_size + 1}/{batch_count} (minimum score set to: {score_min})...        ",
            end="")

        t = time.time()
        scoring_kernel2[blockspergrid, threadsperblock](device_ingreds, device_effectivenesses,
                                                        device_effectiveness_ingredients, device_base_recipes, scores,
                                                        offset, score_min)
        cuda.synchronize()
        scoring_time += time.time() - t

        t = time.time()
        nonzero = cupy.nonzero(scores)[0]
        nonzero_scores = scores.take(nonzero)
        zero_time += time.time() - t

        t = time.time()
        best_idx = cupy.argsort(nonzero_scores)[-20:]
        sort_time += time.time() - t

        t = time.time()

        best = [(nonzero_scores[i].item(), nonzero[i].item() + offset) for i in best_idx]

        total_best = sorted(total_best + best, key=lambda x: x[0], reverse=True)[:20]
        select_time += time.time() - t

    print()
    print("Finished.")

    print(f"Scoring time: {scoring_time:.2f}s")
    print(f"Zero time: {zero_time:.2f}s")
    print(f"Sort time: {sort_time:.2f}s")
    print(f"Select time: {select_time:.2f}s")

    res = []
    for s, i in total_best:
        eff_indx, recipe_pos = get_effectiveness_indx(len(ingredients), effectivenesses, i)
        if eff_indx == -1:
            print("???")
            continue

        r = get_recipe(ingredients, recipe_pos)
        base = combos[effectivenesses[eff_indx][1:effectivenesses[eff_indx][0] + 1]]
        res.append(recipe.Recipe(*_replace_no_ing(base, *r)))

    return res

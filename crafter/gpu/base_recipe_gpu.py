import math
import time

import cupy
import numba
import numpy as np
from numba import cuda

from crafter import ingredient, recipe


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
def score(charges, duration, durability, req_str, req_dex, req_int, req_def, req_agi,
          id1_min, id1_max, id2_min, id2_max, id3_min, id3_max, id4_min, id4_max, id5_min, id5_max):
    return max(0, id1_max * 1000 + (durability + 735000) // 1000)


@cuda.jit(device=True)
def constraints(charges, duration, durability, req_str, req_dex, req_int, req_def, req_agi,
                id1_min, id1_max, id2_min, id2_max, id3_min, id3_max, id4_min, id4_max, id5_min, id5_max):
    return (durability > -735000 + 10000
            and req_int <= 150
            and id1_max > 0)


@cuda.jit(device=True)
def calc_recipe_score(r, mods):
    charges = 0
    duration = 0
    durability = 0
    req_str = 0
    req_dex = 0
    req_int = 0
    req_def = 0
    req_agi = 0
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

    for i in range(6):
        ingr = r[i]

        charges += ingr[0]
        duration += ingr[1]
        durability += ingr[2]
        req_str += ingr[3] * mods[i] // 100
        req_dex += ingr[4] * mods[i] // 100
        req_int += ingr[5] * mods[i] // 100
        req_def += ingr[6] * mods[i] // 100
        req_agi += ingr[7] * mods[i] // 100
        if mods[i] > 0:
            id1_min += ingr[14] * mods[i] // 100
            id1_max += ingr[15] * mods[i] // 100
            id2_min += ingr[16] * mods[i] // 100
            id2_max += ingr[17] * mods[i] // 100
            id3_min += ingr[18] * mods[i] // 100
            id3_max += ingr[19] * mods[i] // 100
            id4_min += ingr[20] * mods[i] // 100
            id4_max += ingr[21] * mods[i] // 100
            id5_min += ingr[22] * mods[i] // 100
            id5_max += ingr[23] * mods[i] // 100
        elif mods[i] < 0:
            id1_min += ingr[15] * mods[i] // 100
            id1_max += ingr[14] * mods[i] // 100
            id2_min += ingr[17] * mods[i] // 100
            id2_max += ingr[16] * mods[i] // 100
            id3_min += ingr[19] * mods[i] // 100
            id3_max += ingr[18] * mods[i] // 100
            id4_min += ingr[21] * mods[i] // 100
            id4_max += ingr[20] * mods[i] // 100
            id5_min += ingr[23] * mods[i] // 100
            id5_max += ingr[22] * mods[i] // 100

    if not constraints(charges, duration, durability, req_str, req_dex, req_int, req_def,
                       req_agi, id1_min, id1_max, id2_min, id2_max, id3_min, id3_max, id4_min, id4_max, id5_min,
                       id5_max):
        return 0

    return score(charges, duration, durability, req_str, req_dex, req_int, req_def, req_agi,
                 id1_min, id1_max, id2_min, id2_max, id3_min, id3_max, id4_min, id4_max, id5_min, id5_max)


@cuda.jit(device=True)
def get_mods(r):
    mod_arr = cuda.local.array(shape=6, dtype=numba.intc)
    for i in range(6):
        mod_arr[i] = 100

    for i in range(6):
        apply_modifier(mod_arr, r[i], i)

    return mod_arr[0], mod_arr[1], mod_arr[2], mod_arr[3], mod_arr[4], mod_arr[5]


def get_recipe(ingredients, permutation: int):
    base = len(ingredients)
    i1 = ingredients[permutation % base]
    permutation //= base
    i2 = ingredients[permutation % base]
    permutation //= base
    i3 = ingredients[permutation % base]
    permutation //= base
    i4 = ingredients[permutation % base]
    permutation //= base
    i5 = ingredients[permutation % base]
    permutation //= base
    i6 = ingredients[permutation % base]
    return i1, i2, i3, i4, i5, i6


get_recipe_cuda = cuda.jit(get_recipe, device=True)


@cuda.jit
def scoring_kernel(ingredients, scores, offset, perm_amt, score_min):
    pos = cuda.grid(1)
    if pos < scores.shape[0]:
        if pos + offset >= perm_amt:
            scores[pos] = 0
            return

        r = get_recipe_cuda(ingredients, pos + offset)
        
        mods = get_mods(r)
        r_score = calc_recipe_score(r, mods)

        if r_score > score_min:
            scores[pos] = r_score
        else:
            scores[pos] = 0


def get_best_recipes_gpu(ingredients: list[ingredient.Ingredient]) -> list[recipe.Recipe]:
    permutation_amt = len(ingredients) ** 6
    batch_size = min(2 ** 26, permutation_amt)

    print(f"Total permutation amount: {permutation_amt}")
    ingredients_array = np.array([i.to_np_array("rawHealth", "", "", "", "") for i in ingredients], dtype=np.intc)
    device_ingreds = cuda.to_device(ingredients_array)
    scores = cupy.empty(batch_size, dtype=np.uint)

    batch_count = math.ceil(permutation_amt / batch_size)
    threadsperblock = 128
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
        scoring_kernel[blockspergrid, threadsperblock](device_ingreds, scores, offset, permutation_amt, score_min)
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

    return [recipe.Recipe(*get_recipe(ingredients, i)) for s, i in total_best]

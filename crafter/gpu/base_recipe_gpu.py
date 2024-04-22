import inspect
import math
import time
from threading import Lock
from typing import Callable

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


BATCH_SIZE = 2 ** 24
THREADSPERBLOCK = 128
_running = Lock()

_score_fun: Callable = None
_constraint_fun: Callable = None


@cuda.jit(device=True)
def score(charges, duration, durability, req_str, req_dex, req_int, req_def, req_agi,
          id1_min, id1_max, id2_min, id2_max, id3_min, id3_max, id4_min, id4_max, id5_min, id5_max):
    return max(0, _score_fun(charges, duration, durability, req_str, req_dex, req_int, req_def, req_agi,
                             id1_min, id1_max, id2_min, id2_max, id3_min, id3_max, id4_min, id4_max, id5_min, id5_max))


@cuda.jit(device=True)
def constraints(charges, duration, durability, req_str, req_dex, req_int, req_def, req_agi,
                id1_min, id1_max, id2_min, id2_max, id3_min, id3_max, id4_min, id4_max, id5_min, id5_max):
    return _constraint_fun(charges, duration, durability, req_str, req_dex, req_int, req_def, req_agi,
                           id1_min, id1_max, id2_min, id2_max, id3_min, id3_max, id4_min, id4_max, id5_min, id5_max)


@cuda.jit(device=True)
def add_maybe(vec, x, y, val):
    if x < 0 or y < 0 or x >= 2 or y >= 3:
        return
    vec[(y << 1) + x] += val


@cuda.jit(device=True)
def apply_modifier(mod_vec, ingr, pos):
    for i in range(6):
        mod_vec[i] += ingr[13]

    x = pos & 1
    y = pos >> 1

    add_maybe(mod_vec, x - 1, y, ingr[8] + ingr[12] - ingr[13])
    add_maybe(mod_vec, x + 1, y, ingr[9] + ingr[12] - ingr[13])

    add_maybe(mod_vec, x, y - 1, ingr[10] + ingr[12] - ingr[13])
    add_maybe(mod_vec, x, y - 2, ingr[10])

    add_maybe(mod_vec, x, y + 1, ingr[11] + ingr[12] - ingr[13])
    add_maybe(mod_vec, x, y + 2, ingr[11])

    mod_vec[pos] -= ingr[13]


@cuda.jit(device=True)
def calc_recipe_score(ingredients, r, mods):
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
        ingr = ingredients[r[i]]

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

    passes = constraints(charges, duration, durability, req_str, req_dex, req_int, req_def,
                       req_agi, id1_min, id1_max, id2_min, id2_max, id3_min, id3_max, id4_min, id4_max, id5_min,
                       id5_max)

    return passes * score(charges, duration, durability, req_str, req_dex, req_int, req_def, req_agi,
                 id1_min, id1_max, id2_min, id2_max, id3_min, id3_max, id4_min, id4_max, id5_min, id5_max)


@cuda.jit(device=True)
def calc_mods(ingredients, r, mod_arr):
    for i in range(6):
        mod_arr[i] = 100

    for i in range(6):
        apply_modifier(mod_arr, ingredients[r[i]], i)


def get_permutation(base, pos, r_arr):
    for i in range(6):
        r_arr[i] = pos % base
        pos //= base


def get_permutation_py(base, pos):
    res = [0] * 6
    get_permutation(base, pos, res)
    return res


get_permutation_cuda = cuda.jit(get_permutation, device=True)


@cuda.jit
def scoring_kernel(ingredients, scores, offset, perm_amt, score_min):
    pos = cuda.grid(1)
    if pos < scores.shape[0]:
        if pos + offset >= perm_amt:
            scores[pos] = 0
            return

        r_arr = cuda.local.array(shape=6, dtype=numba.intc)
        get_permutation_cuda(len(ingredients), pos + offset, r_arr)

        mod_arr = cuda.local.array(shape=6, dtype=numba.intc)
        calc_mods(ingredients, r_arr, mod_arr)

        r_score = calc_recipe_score(ingredients, r_arr, mod_arr)

        scores[pos] = (r_score > score_min) * r_score


def get_best_recipes_gpu(ingredients: list[ingredient.Ingredient], score_fun: Callable, constraint_fun: Callable, ids: list[str]) -> list[
    recipe.Recipe]:
    with _running:
        # check if the score and constraint functions have the right signature
        sig = inspect.signature(score_fun)
        if len(sig.parameters) != 18:
            raise ValueError("Score function must have 24 parameters")
        sig = inspect.signature(constraint_fun)
        if len(sig.parameters) != 18:
            raise ValueError("Constraint function must have 24 parameters")

        global _score_fun, _constraint_fun
        _score_fun = cuda.jit(score_fun, device=True)
        _constraint_fun = cuda.jit(constraint_fun, device=True)

        permutation_amt = len(ingredients) ** 6
        batch_size = min(BATCH_SIZE, permutation_amt)
        print(f"Total permutation amount: {permutation_amt}")

        if len(ids) < 5:
            ids += [""] * (5 - len(ids))

        ingredients_array = np.array([i.to_np_array(*ids[:5]) for i in ingredients], dtype=np.intc)
        device_ingreds = cuda.to_device(ingredients_array)

        scores = cupy.empty(batch_size, dtype=np.uint)

        batch_count = math.ceil(permutation_amt / batch_size)
        blockspergrid = math.ceil(batch_size / THREADSPERBLOCK)

        total_best = []
        best_scores = set()

        scoring_time = 0
        zero_time = 0
        unique_time = 0
        sort_time = 0
        select_time = 0

        for offset in range(0, permutation_amt, batch_size):
            score_min = 0 if len(total_best) < 20 else total_best[-1][0]
            print(
                f"\rCalculating scores for batch {offset // batch_size + 1}/{batch_count} (minimum score set to: {score_min})...        ",
                end="")

            t = time.time()
            scoring_kernel[blockspergrid, THREADSPERBLOCK](device_ingreds, scores, offset, permutation_amt, score_min)
            cuda.synchronize()
            scoring_time += time.time() - t

            t = time.time()
            nonzero = cupy.nonzero(scores)[0]
            nonzero_scores = scores.take(nonzero)
            zero_time += time.time() - t

            t = time.time()
            unique_scores, unique_indxs = cupy.unique(nonzero_scores, return_index=True)
            unique_time = time.time() - t

            t = time.time()
            best_idx = cupy.argsort(unique_scores)
            sort_time += time.time() - t

            t = time.time()

            best = []
            i = len(best_idx) - 1
            while len(best) < 20:
                if i < 0:
                    break
                indx = best_idx[i]
                score = unique_scores[indx].item()
                if len(best) == 0 and score not in best_scores:
                    best.append((score, nonzero[unique_indxs[indx]].item() + offset))
                i -= 1

            total_best = sorted(total_best + best, key=lambda x: x[0], reverse=True)[:20]
            best_scores = {s for s, i in total_best}
            select_time += time.time() - t

        print()
        print("Finished.")

        print(f"Scoring time: {scoring_time:.2f}s")
        print(f"Zero time: {zero_time:.2f}s")
        print(f"Unique time: {unique_time:.2f}s")
        print(f"Sort time: {sort_time:.2f}s")
        print(f"Select time: {select_time:.2f}s")

        return [recipe.Recipe(*[ingredients[p] for p in get_permutation_py(len(ingredients), i)]) for s, i in
                total_best]

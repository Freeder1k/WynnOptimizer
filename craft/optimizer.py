import math
import time
from threading import Lock
from typing import Callable

import cupy
import numba
import numpy as np
from numba import cuda

from craft import recipe
from craft.config.base import OptimalCrafterConfigBase

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


@cuda.jit(device=True, fastmath=True)
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
        req_str += int(ingr[3] * mods[i])
        req_dex += int(ingr[4] * mods[i])
        req_int += int(ingr[5] * mods[i])
        req_def += int(ingr[6] * mods[i])
        req_agi += int(ingr[7] * mods[i])
        if mods[i] > 0:
            id1_min += int(ingr[14] * mods[i])
            id1_max += int(ingr[15] * mods[i])
            id2_min += int(ingr[16] * mods[i])
            id2_max += int(ingr[17] * mods[i])
            id3_min += int(ingr[18] * mods[i])
            id3_max += int(ingr[19] * mods[i])
            id4_min += int(ingr[20] * mods[i])
            id4_max += int(ingr[21] * mods[i])
            id5_min += int(ingr[22] * mods[i])
            id5_max += int(ingr[23] * mods[i])
        elif mods[i] < 0:
            id1_min += int(ingr[15] * mods[i])
            id1_max += int(ingr[14] * mods[i])
            id2_min += int(ingr[17] * mods[i])
            id2_max += int(ingr[16] * mods[i])
            id3_min += int(ingr[19] * mods[i])
            id3_max += int(ingr[18] * mods[i])
            id4_min += int(ingr[21] * mods[i])
            id4_max += int(ingr[20] * mods[i])
            id5_min += int(ingr[23] * mods[i])
            id5_max += int(ingr[22] * mods[i])

    passes = _constraint_fun(charges, duration, durability, req_str, req_dex, req_int, req_def,
                             req_agi, id1_min, id1_max, id2_min, id2_max, id3_min, id3_max, id4_min, id4_max, id5_min,
                             id5_max)

    return passes * _score_fun(charges, duration, durability, req_str, req_dex, req_int, req_def, req_agi,
                               id1_min, id1_max, id2_min, id2_max, id3_min, id3_max, id4_min, id4_max, id5_min, id5_max)


@cuda.jit(device=True, fastmath=True)
def calc_mods(ingredients, r, mod_arr):
    mod_arr[0] = ((100 + ingredients[r[1]][8] + ingredients[r[1]][12] + ingredients[r[2]][10] + ingredients[r[2]][12]
                   + ingredients[r[3]][13] + ingredients[r[4]][10] + ingredients[r[4]][13] + ingredients[r[5]][13])
                  / 100.)
    mod_arr[1] = ((100 + ingredients[r[0]][9] + ingredients[r[0]][12] + ingredients[r[2]][13] + ingredients[r[3]][10]
                   + ingredients[r[3]][12] + ingredients[r[4]][13] + ingredients[r[5]][10] + ingredients[r[5]][13])
                  / 100.)
    mod_arr[2] = ((100 + ingredients[r[0]][11] + ingredients[r[0]][12] + ingredients[r[1]][13] + ingredients[r[3]][8]
                   + ingredients[r[3]][12] + ingredients[r[4]][10] + ingredients[r[4]][12] + ingredients[r[5]][13])
                  / 100.)
    mod_arr[3] = ((100 + ingredients[r[0]][13] + ingredients[r[1]][11] + ingredients[r[1]][12] + ingredients[r[2]][9]
                   + ingredients[r[2]][12] + ingredients[r[4]][13] + ingredients[r[5]][10] + ingredients[r[5]][12])
                  / 100.)
    mod_arr[4] = ((100 + ingredients[r[0]][11] + ingredients[r[0]][13] + ingredients[r[1]][13] + ingredients[r[2]][11]
                   + ingredients[r[2]][12] + ingredients[r[3]][13] + ingredients[r[5]][8] + ingredients[r[5]][12])
                  / 100.)
    mod_arr[5] = ((100 + ingredients[r[0]][13] + ingredients[r[1]][11] + ingredients[r[1]][13] + ingredients[r[2]][13]
                   + ingredients[r[3]][11] + ingredients[r[3]][12] + ingredients[r[4]][9] + ingredients[r[4]][12])
                  / 100.)


def get_permutation(base, pos, r_arr):
    for i in range(6):
        r_arr[i] = pos % base
        pos //= base


def get_permutation_py(base, pos):
    res = [0] * 6
    get_permutation(base, pos, res)
    return res


get_permutation_cuda = cuda.jit(get_permutation, device=True)

from numba.cuda.extending import intrinsic
from llvmlite import ir


@intrinsic
def cuda_clock64(typingctx):
    sig = numba.types.uint64()

    def codegen(context, builder, sig, args):
        function_type = ir.FunctionType(ir.IntType(64), [])
        instruction = "mov.u64 $0, %clock64;"
        clock64 = ir.InlineAsm(function_type, instruction, "=l",
                               side_effect=True)
        return builder.call(clock64, [])

    return sig, codegen


@cuda.jit(fastmath=True)
def scoring_kernel(ingredients, scores, offset, perm_amt, score_min, times):
    pos = cuda.grid(1)
    if pos < scores.shape[0]:
        if pos + offset >= perm_amt:
            scores[pos] = 0
            return

        t1 = cuda_clock64()

        r_arr = cuda.local.array(shape=6, dtype=numba.intc)
        get_permutation_cuda(len(ingredients), pos + offset, r_arr)

        t2 = cuda_clock64()
        numba.cuda.atomic.add(times, 0, t2 - t1)
        t1 = cuda_clock64()

        mod_arr = cuda.local.array(shape=6, dtype=numba.float32)
        calc_mods(ingredients, r_arr, mod_arr)

        t2 = cuda_clock64()
        numba.cuda.atomic.add(times, 1, t2 - t1)
        t1 = cuda_clock64()

        r_score = calc_recipe_score(ingredients, r_arr, mod_arr)

        t2 = cuda_clock64()
        numba.cuda.atomic.add(times, 2, t2 - t1)

        scores[pos] = (r_score > score_min) * r_score


def get_best_recipes_gpu(config: OptimalCrafterConfigBase) -> list[recipe.Recipe]:
    with _running:
        ingredients = config.ingredients
        min_score = config.min_score
        ids = config.ids
        score_fun = config.score
        constraint_fun = config.constraints

        print(f"Calculating optimal recipe with {len(ingredients)} ingredients...")

        global _score_fun, _constraint_fun
        _score_fun = cuda.jit(score_fun, device=True, fastmath=True)
        _constraint_fun = cuda.jit(constraint_fun, device=True, fastmath=True)

        permutation_amt = len(ingredients) ** 6
        batch_size = min(BATCH_SIZE, permutation_amt)
        print(f"Total permutation amount: {permutation_amt}")

        if len(ids) < 5:
            ids += [""] * (5 - len(ids))

        ingredients_array = np.array([i.to_np_array(*ids[:5]) for i in ingredients], dtype=np.intc)
        device_ingreds = cuda.to_device(ingredients_array)

        scores = cupy.empty(batch_size, dtype=cupy.float32)

        kernel_times = np.zeros(3, dtype=np.uint64)
        kernel_times = cuda.to_device(kernel_times)

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
            score_min = max(0 if len(total_best) < 20 else total_best[-1][0], min_score)
            print(
                f"\rCalculating scores for batch {offset // batch_size + 1}/{batch_count} (minimum score set to: {score_min})...        ",
                end="")

            t = time.time()
            scoring_kernel[blockspergrid, THREADSPERBLOCK](device_ingreds, scores, offset, permutation_amt, score_min,
                                                           kernel_times)
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

        kernel_times = kernel_times.copy_to_host()
        print(f"Kernel times: {kernel_times}")

        return [recipe.Recipe(*[ingredients[p] for p in get_permutation_py(len(ingredients), i)]) for s, i in
                total_best]

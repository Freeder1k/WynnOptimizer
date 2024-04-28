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
from craft.cuda_utils import calc_mods, get_permutation_cuda, cuda_clock64, calc_recipe_cuda_function_factory
from craft.utils import get_permutation_py

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
_calc_recipe_cuda = calc_recipe_cuda_function_factory(5)


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

        res_recipe = cuda.local.array(shape=24, dtype=numba.int32)
        _calc_recipe_cuda(ingredients, r_arr, mod_arr, res_recipe)

        passes = _constraint_fun(res_recipe[0], res_recipe[1], res_recipe[2], res_recipe[3], res_recipe[4],
                                 res_recipe[5], res_recipe[6], res_recipe[7], res_recipe[14], res_recipe[15],
                                 res_recipe[16], res_recipe[17], res_recipe[18], res_recipe[19], res_recipe[20],
                                 res_recipe[21], res_recipe[22], res_recipe[23])

        r_score = passes * _score_fun(res_recipe[0], res_recipe[1], res_recipe[2], res_recipe[3], res_recipe[4],
                                      res_recipe[5], res_recipe[6], res_recipe[7], res_recipe[14], res_recipe[15],
                                      res_recipe[16], res_recipe[17], res_recipe[18], res_recipe[19], res_recipe[20],
                                      res_recipe[21], res_recipe[22], res_recipe[23])

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

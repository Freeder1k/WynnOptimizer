import math
import time
from threading import Lock

import cupy
import numba
import numpy as np
from numba import cuda

import craft.cuda_utils
from core.optimizer import bruteForce
from craft import ingredient, recipe
from craft.cuda_utils import calc_recipe_cuda
from craft.old.base_recipe import _pad_r
from craft.utils import get_permutation_py, item_profs, consu_profs

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
# id[k].max,                      # k * 2 + 14
# id[k].min,                      # k * 2 + 15
# ...

BATCH_SIZE = 2 ** 24
THREADSPERBLOCK = 128
_running = Lock()

_id_count = 0
_ingr_count = 0

_calc_recipe_cuda = calc_recipe_cuda[_id_count]


@cuda.jit(fastmath=True)
def _kernel(ingredients, recipes, viable, times):
    pos = cuda.grid(1)
    if pos < len(recipes):
        t1 = craft.cuda_utils.cuda_clock64()

        r_arr = cuda.local.array(shape=6, dtype=numba.intc)
        craft.cuda_utils.get_permutation_cuda(len(ingredients), pos, r_arr)

        t2 = craft.cuda_utils.cuda_clock64()
        numba.cuda.atomic.add(times, 0, t2 - t1)
        t1 = craft.cuda_utils.cuda_clock64()

        mod_arr = cuda.local.array(shape=6, dtype=numba.float32)
        craft.cuda_utils.calc_mods(ingredients, r_arr, mod_arr)

        t2 = craft.cuda_utils.cuda_clock64()
        numba.cuda.atomic.add(times, 1, t2 - t1)

        abs_mod = 0
        for i in range(6):
            if r_arr[i] == 0:
                abs_mod += abs(mod_arr[i])

        if abs_mod < 300:
            viable[pos] = False
            return
        else:
            viable[pos] = True
            recipes[pos][8] = mod_arr[0]
            recipes[pos][9] = mod_arr[1]
            recipes[pos][10] = mod_arr[2]
            recipes[pos][11] = mod_arr[3]
            recipes[pos][12] = mod_arr[4]
            recipes[pos][13] = mod_arr[5]

        t1 = craft.cuda_utils.cuda_clock64()

        _calc_recipe_cuda(ingredients, r_arr, mod_arr, recipes[pos])

        t2 = craft.cuda_utils.cuda_clock64()
        numba.cuda.atomic.add(times, 2, t2 - t1)


def is_worse(a, b, profession: str):
    return (((a[2] <= b[2] and all(a[i] >= b[i] for i in range(3, 8)) and profession in item_profs)
             or ((a[0] <= b[0] and a[1] <= b[1]) and profession in consu_profs))
            and all(a[i] <= b[i] for i in range(14, 14 + _id_count * 2))
            )


@cuda.jit()
def _mods_kernel(nonzero_indx, nonzero_res, mods):
    pos = cuda.grid(1)
    if pos < len(nonzero_indx):
        p_num = nonzero_indx[pos]

        r_arr = cuda.local.array(shape=6, dtype=numba.intc)
        craft.cuda_utils.get_permutation_cuda(_ingr_count, p_num, r_arr)
        j = 1
        for k in range(6):
            if r_arr[k] == 0:
                mods[pos][j] = nonzero_res[pos][k + 8]
                j += 1

        mods[pos][0] = j


async def get_base_recipes_gpu(skill: str):
    with _running:
        ingredients = [ingredient.NO_INGREDIENT]
        ingredients += [ingr for ingr in (await ingredient.get_all_ingredients()).values()
                        if ingr.modifiers.abs_total() > 0 and skill in ingr.requirements.skills]

        ids = ["manaRegen"]

        global _id_count, _ingr_count, _calc_recipe_cuda
        _id_count = len(ids)
        _ingr_count = len(ingredients)
        _calc_recipe_cuda = calc_recipe_cuda[_id_count]

        print(f"Calculating base recipes with {len(ingredients)} ingredients...")

        permutation_amt = len(ingredients) ** 6
        print(f"Total permutation amount: {permutation_amt}")

        device_ingreds = cuda.to_device(np.array([i.to_np_array(*ids) for i in ingredients], dtype=np.intc))

        recipes = cupy.empty((permutation_amt, device_ingreds.shape[1]), dtype=cupy.short)
        viable = cupy.empty(permutation_amt, dtype=cupy.bool_)

        kernel_times = cuda.device_array(3, dtype=np.uint64)

        blockspergrid = math.ceil(permutation_amt / THREADSPERBLOCK)

        t = time.time()
        _kernel[blockspergrid, THREADSPERBLOCK](device_ingreds, recipes, viable, kernel_times)
        cuda.synchronize()
        scoring_time = time.time() - t

        t = time.time()
        nonzero_indx = cupy.nonzero(viable)[0]
        nonzero_res = cupy.take(recipes, nonzero_indx, axis=0)
        print("Found", len(nonzero_indx), "viable base recipes.")
        res_len = len(nonzero_indx)

        zero_time = time.time() - t
        t = time.time()

        mods_array = cuda.device_array((len(nonzero_indx), 7), dtype=cupy.short)
        _mods_kernel[blockspergrid, THREADSPERBLOCK](nonzero_indx, nonzero_res, mods_array)
        mods_array = mods_array.copy_to_host()
        nonzero_res = cupy.asnumpy(nonzero_res)

        mods_time = time.time() - t

        t = time.time()
        res = {}
        for i in range(len(nonzero_indx)):
            mods = tuple(sorted(mods_array[i][j] for j in range(1, mods_array[i][0])))
            if mods in res:
                res[mods].append(i)
            else:
                res[mods] = [i]

        dict_time = time.time() - t
        t = time.time()

        for mods, option in res.items():
            new_options = []
            for recipe_indx1 in option:
                passes = True
                for recipe_indx2 in option:
                    if recipe_indx1 == recipe_indx2:
                        continue
                    if is_worse(nonzero_res[recipe_indx1], nonzero_res[recipe_indx2], skill):
                        passes = False
                        break
                if passes:
                    new_options.append(recipe_indx1)
            res[mods] = new_options

        unique_time = time.time() - t
        print(f"Filtered out {res_len - sum(len(v) for v in res.values())} worse recipes with same modifiers.")
        res_len = sum(len(v) for v in res.values())
        t = time.time()

        for mods, options in res.items():
            for sub_combo in bruteForce.generate_all_subpermutations(*mods, ordered=True):
                new_options = []
                for recipe_indx1 in res.get(sub_combo, []):
                    passes = True
                    for recipe_indx2 in options:
                        if is_worse(nonzero_res[recipe_indx1], nonzero_res[recipe_indx2], skill):
                            passes = False
                            break
                    if passes:
                        new_options.append(recipe_indx1)
                if sub_combo in res:
                    res[sub_combo] = new_options

        res = {k: res[k] for k in res if len(res[k]) > 0}
        print(f"Filtered out {res_len - sum(len(v) for v in res.values())} worse recipes with a subset of modifiers.")
        subset_time = time.time() - t
        t = time.time()

        res = sorted(((k, v) for k, v in res.items()), key=lambda x: sum(x[0]), reverse=True)
        res = {k: [nonzero_indx[i].item() for i in v] for k, v in res}
        res = [(k, recipe.Recipe(*[ingredients[p] for p in get_permutation_py(_ingr_count, i)]))
               for k, v in res.items() for i in v]

        # _to_csv(res)

        print(f"Finished. Total unique recipes: {len(res)}.")

        print(f"Scoring time: {scoring_time:.2f}s")
        print(f"Zero time: {zero_time:.2f}s")
        print(f"Mods time: {mods_time:.2f}s")
        print(f"Dict time: {dict_time:.2f}s")
        print(f"Unique time: {unique_time:.2f}s")
        print(f"Subset time: {subset_time:.2f}s")

        kernel_times = kernel_times.copy_to_host()
        print(f"Kernel times: {kernel_times}")

        return res


def _to_csv(combos: dict[tuple[int, ...], list]):
    with open("combos2.csv", "w", encoding='utf8') as f:
        f.write("Combo,,,,,,Charges,Duration,Durability,Str,Dex,Int,Def,Agi,mods,...,,,,,id0_max,id0_min,...\n")
        for k, v in combos.items():
            for res in v:
                res[2] += 735
                f.write(
                    f"{','.join(_pad_r(tuple(map(str, k)), 6, ''))},"
                    f"{','.join(map(str, list(res)))}\n"
                )

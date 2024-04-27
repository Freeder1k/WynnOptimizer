import math
import time
from threading import Lock

import cupy
import numba
import numpy as np
from numba import cuda

from core.optimizer import bruteForce
from crafting import ingredient, optimizer
from crafting.old.base_recipe import _pad_r

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
# idk.max,                      # k * 2 + 14
# idk.min,                      # k * 2 + 15
# ...


BATCH_SIZE = 2 ** 24
THREADSPERBLOCK = 128
_running = Lock()

_id_count = 0
_ingr_count = 0


@cuda.jit(device=True, fastmath=True)
def _calc_recipe(ingredients, r, mods, res_recipe):
    for i in range(6):
        ingr = ingredients[r[i]]

        res_recipe[0] += ingr[0]
        res_recipe[1] += ingr[1]
        res_recipe[2] += ingr[2] // 1000
        res_recipe[3] += int(ingr[3] * mods[i])
        res_recipe[4] += int(ingr[4] * mods[i])
        res_recipe[5] += int(ingr[5] * mods[i])
        res_recipe[6] += int(ingr[6] * mods[i])
        res_recipe[7] += int(ingr[7] * mods[i])
        for k in range(_id_count):
            j = 2 * k + 14
            if mods[i] > 0:
                res_recipe[j] += int(ingr[j] * mods[i])
                res_recipe[j + 1] += int(ingr[j + 1] * mods[i])
            elif mods[i] < 0:
                res_recipe[j] += int(ingr[j + 1] * mods[i])
                res_recipe[j + 1] += int(ingr[j] * mods[i])


@cuda.jit(fastmath=True)
def _kernel(ingredients, recipes, viable, times):
    pos = cuda.grid(1)
    if pos < len(recipes):
        t1 = optimizer.cuda_clock64()

        r_arr = cuda.local.array(shape=6, dtype=numba.intc)
        optimizer.get_permutation_cuda(len(ingredients), pos, r_arr)

        t2 = optimizer.cuda_clock64()
        numba.cuda.atomic.add(times, 0, t2 - t1)
        t1 = optimizer.cuda_clock64()

        mod_arr = cuda.local.array(shape=6, dtype=numba.float32)
        optimizer.calc_mods(ingredients, r_arr, mod_arr)

        t2 = optimizer.cuda_clock64()
        numba.cuda.atomic.add(times, 1, t2 - t1)

        abs_mod = 0
        for i in range(6):
            if r_arr[i] == 0:
                abs_mod += abs(mod_arr[i])

        if abs_mod < 3.:
            viable[pos] = False
            return
        else:
            viable[pos] = True
            recipes[pos][8] = round(mod_arr[0] * 100)
            recipes[pos][9] = round(mod_arr[1] * 100)
            recipes[pos][10] = round(mod_arr[2] * 100)
            recipes[pos][11] = round(mod_arr[3] * 100)
            recipes[pos][12] = round(mod_arr[4] * 100)
            recipes[pos][13] = round(mod_arr[5] * 100)

        t1 = optimizer.cuda_clock64()

        _calc_recipe(ingredients, r_arr, mod_arr, recipes[pos])

        t2 = optimizer.cuda_clock64()
        numba.cuda.atomic.add(times, 2, t2 - t1)


item_profs = [
    'armouring',
    'tailoring',
    'weaponsmithing',
    'woodworking',
    'jeweling',
]

consu_profs = [
    'cooking',
    'alchemism',
    'scribing',
]


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
        optimizer.get_permutation_cuda(_ingr_count, p_num, r_arr)
        j = 1
        for k in range(6):
            if r_arr[k] == 0:
                mods[pos][j] = nonzero_res[pos][k + 8]
                j += 1

        mods[pos][0] = j


async def get_base_recipes_gpu(profession: str):
    """
    No more than 15 ingredients should be used.
    """
    with _running:
        ingredients = [ingr for ingr in (await ingredient.get_all_ingredients()).values() if
                       ingr.modifiers.abs_total() > 0]
        ingredients = [ingr for ingr in ingredients if profession in ingr.requirements.skills]
        ingredients = [ingredient.NO_INGREDIENT] + ingredients

        ids = []

        global _id_count, _ingr_count
        _id_count = len(ids)
        _ingr_count = len(ingredients)

        print(f"Calculating base recipes with {len(ingredients)} ingredients...")

        permutation_amt = len(ingredients) ** 6
        print(f"Total permutation amount: {permutation_amt}")

        ingredients_array = np.array([i.to_np_array(*ids) for i in ingredients], dtype=np.intc)
        device_ingreds = cuda.to_device(ingredients_array)

        recipes = cupy.empty((permutation_amt, ingredients_array.shape[1]), dtype=cupy.short)
        viable = cupy.empty(permutation_amt, dtype=cupy.bool_)

        kernel_times = np.zeros(3, dtype=np.uint64)
        kernel_times = cuda.to_device(kernel_times)

        blockspergrid = math.ceil(permutation_amt / THREADSPERBLOCK)

        t = time.time()
        _kernel[blockspergrid, THREADSPERBLOCK](device_ingreds, recipes, viable, kernel_times)
        cuda.synchronize()
        scoring_time = time.time() - t

        t = time.time()
        nonzero_indx = cupy.nonzero(viable)[0]
        nonzero_res = cupy.take(recipes, nonzero_indx, axis=0)
        print(len(nonzero_indx))

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
                good = True
                for i_other in res[mods]:
                    if is_worse(nonzero_res[i], nonzero_res[i_other], profession):
                        good = False
                        break
                if good:
                    res[mods].append(i)
            else:
                res[mods] = [i]

        print(sum(len(v) for v in res.values()))
        unique_time = time.time() - t
        t = time.time()

        for mods, options in res.items():
            for sub_combo in bruteForce.generate_all_subpermutations(*mods, ordered=True):
                new_options = []
                for recipe_indx1 in res.get(sub_combo, []):
                    passes = True
                    for recipe_indx2 in options:
                        if is_worse(nonzero_res[recipe_indx1], nonzero_res[recipe_indx2], profession):
                            passes = False
                            break
                    if passes:
                        new_options.append(recipe_indx1)
                if sub_combo in res:
                    res[sub_combo] = new_options

        res = {k: res[k] for k in res if len(res[k]) > 0}
        print(sum(len(v) for v in res.values()))
        subset_time = time.time() - t
        t = time.time()

        res = sorted(((k, v) for k, v in res.items()), key=lambda x: sum(x[0]), reverse=True)
        res = {k: [nonzero_res[i] for i in v] for k, v in res}

        _to_csv(res)

        print("Finished.")

        print(f"Scoring time: {scoring_time:.2f}s")
        print(f"Zero time: {zero_time:.2f}s")
        print(f"Mods time: {mods_time:.2f}s")
        print(f"Unique time: {unique_time:.2f}s")
        print(f"Subset time: {subset_time:.2f}s")

        kernel_times = kernel_times.copy_to_host()
        print(f"Kernel times: {kernel_times}")

        return


def _to_csv(combos: dict[tuple[int, ...], list]):
    with open("combos2.csv", "w", encoding='utf8') as f:
        f.write("Combo,,,,,,Charges,Duration,Durability,Str,Dex,Int,Def,Agi,mods,,,,,,id0_max,id0_min,...\n")
        for k, v in combos.items():
            for res in v:
                res[2] += 735
                f.write(
                    f"{','.join(_pad_r(tuple(map(str, k)), 6, ''))},"
                    f"{','.join(map(str, list(res)))}\n"
                )

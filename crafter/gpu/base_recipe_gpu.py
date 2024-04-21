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
def calc_recipe_score(recipe):
    effectiveness_vec = cuda.local.array(shape=6, dtype=numba.intc)
    for i in range(6):
        effectiveness_vec[i] = 100
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

    for i in range(6):
        apply_modifier(effectiveness_vec, recipe[i], i)

    for i in range(6):
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


@cuda.jit(device=True)
def get_recipe_cuda(ingredients, pos):
    base = ingredients.shape[0]
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


@cuda.jit
def scoring_kernel(ingredients, scores, offset, perm_amt, score_min):
    pos = cuda.grid(1)
    if pos < scores.shape[0]:
        if pos + offset >= perm_amt:
            scores[pos] = 0
            return
        recipe = get_recipe_cuda(ingredients, pos + offset)
        r_score = calc_recipe_score(recipe)
        if r_score >= score_min:
            scores[pos] = r_score
        else:
            scores[pos] = 0


def get_best_recipes_gpu(ingredients: list[ingredient.Ingredient]) -> list[recipe.Recipe]:
    permutation_amt = len(ingredients) ** 6
    batch_size = min(2 ** 27, permutation_amt)

    print(f"Total permutation amount: {permutation_amt}")
    ingredients_array = np.array([i.to_np_array("rawHealth", "", "", "", "") for i in ingredients], dtype=np.intc)
    device_ingreds = cuda.to_device(ingredients_array)
    scores = cupy.empty(batch_size, dtype=np.uint)

    threadsperblock = 512
    blockspergrid = math.ceil(permutation_amt / threadsperblock)

    total_best = []
    loop_amount = math.ceil(permutation_amt / batch_size)

    for offset in range(0, permutation_amt, batch_size):
        score_min = 0 if len(total_best) < 20 else total_best[-1][0]
        print(
            f"\rCalculating scores for batch {offset // batch_size + 1}/{loop_amount} (minimum score set to: {score_min})...        ",
            end="")
        scoring_kernel[blockspergrid, threadsperblock](device_ingreds, scores, offset, permutation_amt, score_min)

        nonzero = cupy.nonzero(scores)[0]
        nonzero_scores = scores.take(nonzero)

        best_idx = cupy.argsort(nonzero_scores)[-20:]

        best = [(nonzero_scores[i].item(), nonzero[i].item() + offset) for i in best_idx]

        total_best = sorted(total_best + best, key=lambda x: x[0], reverse=True)[:20]

    print()
    print("Finished.")

    return [recipe.Recipe(*get_recipe(ingredients, i)) for s, i in total_best]


if __name__ == "__main__":
    # host()
    t = time.time()
    # print(get_best_recipes_gpu([ingredient.NO_INGREDIENT] * 10))

    print("time: ", time.time() - t)
    # print([x for x in itertools.product((1,2,3), repeat=3)])

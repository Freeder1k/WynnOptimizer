import asyncio
import math
import time

from numba import cuda

import core.managers.httpSessionManager
import crafter.base_recipe
import crafter.crafter
import crafter.gpu.base_recipe_gpu
import crafter.ingredient
import crafter.recipe

jeweling_base = [
    "Lunar Charm",
    "Borange Fluff",
    "Bob's Tear",
    "Doom Stone",
    "Obelisk Core",
    "Old Treasure֎",
    "Eye of The Beast",
    "Major's Badge",
    "Stolen Pearls",
]

armouring_base = [
    "Unicorn Horn",
    "Borange Fluff",
    "Bob's Tear",
    "Decaying Heart",
    "Obelisk Core",
    "Disturbed Dye",
    "Transformativity",
    "Festering Face",
    "Major's Badge",
    'Alginate Dressing',
    "Familiar Essence",
    "Antique Metal",
    "Elephelk Trunk"
]


def constraints(item: crafter.ingredient.Ingredient):
    free_sp = 22
    return (
            item.durability > -735000 + 150000
            and item.requirements.strength <= 4 + free_sp
            and item.requirements.dexterity <= 30 + free_sp
            and item.requirements.intelligence <= 120 + free_sp
            and item.requirements.defence <= 4 + free_sp
            and item.requirements.agility <= 60 + free_sp
            and item.requirements.strength + item.requirements.dexterity + item.requirements.intelligence + item.requirements.defence + item.requirements.agility <= 4 + 30 + 120 + 4 + 60 + free_sp
            and item.identifications['rawAgility'].max + item.identifications['rawDefence'].max >= 10
    )


def constraints2(item: crafter.ingredient.Ingredient):
    return (
            item.durability > -735000 + 10000
            and item.requirements.intelligence <= 130
    )


def score2(item: crafter.ingredient.Ingredient):
    return item.identifications['rawHealth'].max * 100000 + item.durability // 10 + item.requirements.intelligence


def eff_defagi(item: crafter.ingredient.Ingredient):
    return ((item.identifications['rawDefence'].max + item.identifications['rawAgility'].max)
            - (max(0, item.requirements.strength - 4) + max(0, item.requirements.dexterity - 30)))


def score(item: crafter.ingredient.Ingredient):
    return int(100 * item.identifications["waterDamage"].max
               + 125 * eff_defagi(item)
               + durascore(item.durability))


def score_cuda(charges, duration, durability, req_str, req_dex, req_int, req_def, req_agi,
               id1_min, id1_max, id2_min, id2_max, id3_min, id3_max, id4_min, id4_max, id5_min, id5_max):
    return int(100 * id1_max
               + 125 * (id2_max + id3_max - max(0, req_str - 4) - max(0, req_dex - 30))
               + min((durability + 735000) // 100000, 200))


def constraints_cuda(charges, duration, durability, req_str, req_dex, req_int, req_def, req_agi,
                     id1_min, id1_max, id2_min, id2_max, id3_min, id3_max, id4_min, id4_max, id5_min, id5_max):
    free_sp = 22
    return (
            durability > -735000 + 150000
            and req_str <= 4 + free_sp
            and req_dex <= 30 + free_sp
            and req_int <= 120 + free_sp
            and req_def <= 4 + free_sp
            and req_agi <= 60 + free_sp
            and req_str + req_dex + req_int + req_def + req_agi <= 4 + 30 + 120 + 4 + 60 + free_sp
            and id1_max + id2_max + id3_max >= 10
    )


@cuda.jit(device=True, fastmath=True)
def durascore_cuda(dura: int):
    normed = ((dura + 735000) // 1000) / 100
    normed_score = fast_sigmoid((normed - 1.3)/0.3)
    return int(normed_score * 1000)


@cuda.jit(device=True, fastmath=True)
def fast_sigmoid(x: float):
    return (1 / (1 + abs(x))) + 1



async def craft():
    eff_ings = [await crafter.ingredient.get_ingredient(name) for name in armouring_base]
    water_ings = [ingr for ingr in (await crafter.ingredient.get_all_ingredients()).values() if abs(ingr.identifications["waterDamage"].max) >= 5]
    def_ings = [ingr for ingr in (await crafter.ingredient.get_all_ingredients()).values() if ingr.identifications["rawDefence"].max >= 4 or ingr.identifications["rawAgility"].min <= -3]
    agi_ings = [ingr for ingr in (await crafter.ingredient.get_all_ingredients()).values() if abs(ingr.identifications["rawAgility"].max) >= 2]
    ingredients = {i.name for i in eff_ings + water_ings + def_ings + agi_ings}
    ingredients = [await crafter.ingredient.get_ingredient(name) for name in [
    ] + list(ingredients)]
    ingredients = [ingr for ingr in ingredients if "armouring" in ingr.requirements.skills]
    print(len(ingredients))
    t = time.time()
    print(f"Calculating optimal recipe with {len(ingredients)} ingredients...")
    res = crafter.gpu.base_recipe_gpu.get_best_recipes_gpu(ingredients + eff_ings, score_cuda, constraints_cuda,
                                                           ["waterDamage", "rawDefence", "rawAgility"])
    print(f"Time taken: {time.time() - t:.2f}s")
    print('\n'.join(map(print_recipe, res)))


async def main():
    print(f" ∧,,∧\n"
          "( `•ω•) 。•。︵\n"
          "/　 　ο—ヽ二二ラ))\n"
          "し———J\n")
    try:
        await core.managers.httpSessionManager.HTTPSessionManager().start()

        await craft()
    finally:
        await core.managers.httpSessionManager.HTTPSessionManager().close()


def print_recipe(r: crafter.recipe.Recipe) -> str:
    item = r.build()
    return (f"https://hppeng-wynn.github.io/crafter/#1{r.b64_hash()}9g91 "
            f"{item.identifications['waterDamage'].max} wd "
            f"{eff_defagi(item)} def+agi "
            f"{(item.durability + 735000) // 1000} dura   "
            f"{r}")


if __name__ == '__main__':
    asyncio.run(main())

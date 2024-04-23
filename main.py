import asyncio
import time

from numba import cuda

import core.managers.httpSessionManager
import crafter.base_recipe
import crafter.crafter
import crafter.base_recipe_gpu
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
               + 56 * id2_max
               + 35 * id3_max
               #+ 5 * min((durability + 735000) // 1000, 250)
               )


def constraints_cuda(charges, duration, durability, req_str, req_dex, req_int, req_def, req_agi,
                     id1_min, id1_max, id2_min, id2_max, id3_min, id3_max, id4_min, id4_max, id5_min, id5_max):
    free_sp = 0
    return (
            durability > -735000 + 50000 and id1_max > 0 and id4_max >= 0 and id5_max >= 0
            and req_str <= 100
            and req_dex <= 120
            and req_int <= 65
            and req_def <= 0
            and req_agi <= 0
            #and max(req_str, 4) + max(req_dex, 30) + max(req_int, 120) + max(req_def, 4) + max(req_agi, 60) <= 4 + 30 + 120 + 4 + 60 + free_sp
    )


@cuda.jit(device=True, fastmath=True)
def durascore_cuda(dura: int):
    normed = ((dura + 735000) // 1000) / 100
    normed_score = fast_sigmoid((normed - 1.3) / 0.3)
    return int(normed_score * 1000)


@cuda.jit(device=True, fastmath=True)
def fast_sigmoid(x: float):
    return (1 / (1 + abs(x))) + 1


async def craft():
    eff_ings = [await crafter.ingredient.get_ingredient(name) for name in jeweling_base]
    ings1 = [ingr for ingr in (await crafter.ingredient.get_all_ingredients()).values() if
                  abs(ingr.identifications["spellDamage"].max) > 0]
    ings2 = [ingr for ingr in (await crafter.ingredient.get_all_ingredients()).values() if
                abs(ingr.identifications["thunderDamage"].max) > 0]
    ings3 = [ingr for ingr in (await crafter.ingredient.get_all_ingredients()).values() if
                abs(ingr.identifications["earthDamage"].max) > 0]
    ingredients = {i.name for i in eff_ings + ings1 + ings2 + ings3}
    ingredients = [await crafter.ingredient.get_ingredient(name) for name in [
    ] + list(ingredients)]
    ingredients = [ingr for ingr in ingredients if "jeweling" in ingr.requirements.skills]

    t = time.time()
    print(f"Calculating optimal recipe with {len(ingredients)} ingredients...")
    res = crafter.base_recipe_gpu.get_best_recipes_gpu(ingredients, score_cuda, constraints_cuda,
                                                       ["spellDamage", "thunderDamage", "earthDamage", "manaRegen", "rawIntelligence"], 2000)
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
    return (f"https://hppeng-wynn.github.io/crafter/#1{r.b64_hash()}9m91 "
            f"{item.identifications['spellDamage'].max} sd "
            f"{item.identifications['thunderDamage'].max} td "
            f"{item.identifications['earthDamage'].max} ed "
            #f"{eff_defagi(item)} def+agi "
            f"{(item.durability + 735000) // 1000} dura   "
            #f"{r}"
            )


if __name__ == '__main__':
    asyncio.run(main())

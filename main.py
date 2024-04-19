import asyncio
import math
import time

import core.managers.httpSessionManager
import crafter.crafter
import crafter.effectiveness_combos
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
    #"Stolen Pearls",
]

armouring_base = [
    "Unicorn Horn",
    "Borange Fluff",
    "Bob's Tear",
    "Decaying Heart",
    # "Obelisk Core",
    # "Transformativity",
    # "Festering Face",
    # "Major's Badge",
    # "Familiar Essence",
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
            and "waterDamage" in item.identifications
            and "rawDefence" in item.identifications
            and "rawAgility" in item.identifications
            and item.identifications['rawAgility'].max + item.identifications['rawDefence'].max >= 10
    )


def eff_defagi(item: crafter.ingredient.Ingredient):
    return ((item.identifications['rawDefence'].max + item.identifications['rawAgility'].max)
            - (max(0, item.requirements.strength - 4) + max(0, item.requirements.dexterity - 30)))


def score(item: crafter.ingredient.Ingredient):
    return int(100 * item.identifications["waterDamage"].max
               + 125 * eff_defagi(item)
               + durascore(item.durability))


def durascore(dura: int):
    normed = ((dura + 735000) // 1000) / 100
    normed_score = math.tanh((normed - 1.3) / .7) + 1
    return int(normed_score * 1000)


async def opt_craft():
    ingredients = [await crafter.ingredient.get_ingredient(name) for name in [
        # "Ocea Steel",
        "Deep Ice Core",
        "River Clay",
        "Wintery Aspect",
        "Fiberglass Frame",
        "Voidtossed Memory",
        "Coastal Shell",
        "Soft Silk",
        "Fragmentation"
    ] + armouring_base]

    t = time.time()
    print("Optimizing...")
    r = crafter.crafter.optimize(constraints, score, ingredients, 20, 5)
    print('\n'.join(map(print_recipe, r)))
    print(f"Time taken: {time.time() - t:.2f}s")


async def eff_combos():
    ingredients = [await crafter.ingredient.get_ingredient(name) for name in jeweling_base]
    t = time.time()
    print("Calculating combos...")
    res = crafter.effectiveness_combos.get_effectiveness_combos(ingredients, 5)
    #print(len(res))
    #combos = sorted(res.keys(), key=lambda x: sum(x))
    #print('\n'.join(map(str, combos)))
    print(f"Time taken: {time.time() - t:.2f}s")


async def main():
    print(f" ∧,,∧\n"
          "( `•ω•) 。•。︵\n"
          "/　 　ο—ヽ二二ラ))\n"
          "し———J\n")
    try:
        await core.managers.httpSessionManager.HTTPSessionManager().start()

        await eff_combos()
    finally:
        await core.managers.httpSessionManager.HTTPSessionManager().close()


def print_recipe(r: crafter.recipe.Recipe) -> str:
    item = r.build()
    return (f"https://hppeng-wynn.github.io/crafter/#1{r.b64_hash()}9g91 "
            f"{item.identifications['waterDamage'].max}% wd "
            f"{eff_defagi(item)} def+agi "
            f"{(item.durability + 735000) // 1000} dura   "
            f"{r}")


if __name__ == '__main__':
    asyncio.run(main())

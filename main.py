import asyncio
import time

import core.managers.httpSessionManager
import crafter.crafter
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
    # "Obelisk Core",
    "Transformativity",
    # "Festering Face",
    # "Major's Badge",
    # "Familiar Essence",
    "Antique Metal"
]


def constraints(item: crafter.ingredient.Ingredient):
    return (
            item.durability > -625000
            and item.requirements.strength <= 30
            and item.requirements.dexterity <= 30
            and item.requirements.intelligence <= 120
            and item.requirements.defence <= 50
            and item.requirements.agility <= 50
            and "rawDefence" in item.identifications
            and "rawAgility" in item.identifications
            and item.identifications['rawAgility'].max + item.identifications['rawDefence'].max >= 15
    )

async def main():
    print(f" ∧,,∧\n"
          "( `•ω•) 。•。︵\n"
          "/　 　ο—ヽ二二ラ))\n"
          "し———J\n")
    try:
        await core.managers.httpSessionManager.HTTPSessionManager().start()

        ingredients = [await crafter.ingredient.get_ingredient(name) for name in [
            "Ocea Steel",
            "Deep Ice Core",
            "River Clay",
            "Wintery Aspect",
            "Fiberglass Frame",
            "Voidtossed Memory"
        ] + armouring_base]

        t = time.time()
        print("Optimizing...")
        print("Best recipe:", await crafter.crafter.optimize("waterDamage", constraints, ingredients))
        print(f"Time taken: {time.time() - t:.2f}s")

    finally:
        await core.managers.httpSessionManager.HTTPSessionManager().close()


if __name__ == '__main__':
    asyncio.run(main())

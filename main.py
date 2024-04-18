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
    # "Transformativity",
    # "Festering Face",
    # "Major's Badge",
    # "Familiar Essence",
    "Antique Metal"
]


def constraints(item: crafter.ingredient.Ingredient):
    return (
            item.durability > -735000 + 180000
            and item.requirements.strength <= 60
            and item.requirements.dexterity <= 65
            and item.requirements.intelligence <= 120
            and item.requirements.defence <= 60
            and item.requirements.agility <= 60
            and item.requirements.defence + item.requirements.agility + item.requirements.strength + item.requirements.dexterity <= 25 + 30 + 25 + 25 + 33
            and "waterDamage" in item.identifications
            and "rawDefence" in item.identifications
            and "rawAgility" in item.identifications
            and item.identifications['rawAgility'].max + item.identifications['rawDefence'].max >= 10
    )


def score(item: crafter.ingredient.Ingredient):
    return int(100 * item.identifications["waterDamage"].max
               + 10 * (item.identifications['rawDefence'].max + item.identifications['rawAgility'].max)
               + item.durability // 1000)


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
            # "River Clay",
            "Wintery Aspect",
            "Fiberglass Frame",
            "Voidtossed Memory"
        ] + armouring_base]

        t = time.time()
        print("Optimizing...")
        r = await crafter.crafter.optimize(constraints, score, ingredients, 20, 7)
        print('\n'.join(map(str, r)))
        print(f"Time taken: {time.time() - t:.2f}s")

    finally:
        await core.managers.httpSessionManager.HTTPSessionManager().close()


if __name__ == '__main__':
    asyncio.run(main())

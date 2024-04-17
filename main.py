import asyncio
import time

import core.managers.httpSessionManager
import crafter.crafter
import crafter.recipe
import crafter.ingredient


async def main():
    print(f" ∧,,∧\n"
          "( `•ω•) 。•。︵\n"
          "/　 　ο—ヽ二二ラ))\n"
          "し———J\n")
    try:
        await core.managers.httpSessionManager.HTTPSessionManager().start()

        ingredients = [await crafter.ingredient.get_ingredient(name) for name in [
            "Lunar Charm",
            "Borange Fluff",
            "Bob's Tear",
            "Doom Stone",
            "Obelisk Core",
            "Old Treasure֎",
            "Eye of The Beast",
            "Major's Badge",
            "Naval Stone",
            "Archaic Medallion",
            "Stolen Pearls",
        ]]

        t = time.time()
        print("Optimizing...")
        print("Best recipe:", await crafter.crafter.optimize("spellDamage", -725000, ingredients))
        print(f"Time taken: {time.time() - t:.2f}s")

    finally:
        await core.managers.httpSessionManager.HTTPSessionManager().close()


if __name__ == '__main__':
    asyncio.run(main())

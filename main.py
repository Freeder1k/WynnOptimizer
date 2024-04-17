import asyncio

import core.managers.httpSessionManager
import crafter.crafter
import crafter.recipe


async def main():
    print(f" ∧,,∧\n"
          "( `•ω•) 。•。︵\n"
          "/　 　ο—ヽ二二ラ))\n"
          "し———J\n")
    try:
        await core.managers.httpSessionManager.HTTPSessionManager().start()

        test = await crafter.recipe.Recipe.from_names("Lunar Charm", "Lunar Charm",
                                                      "Naval Stone", "Naval Stone",
                                                      "Naval Stone", "Naval Stone")

        print(test.build())

    finally:
        await core.managers.httpSessionManager.HTTPSessionManager().close()


if __name__ == '__main__':
    asyncio.run(main())

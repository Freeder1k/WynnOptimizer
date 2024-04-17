import asyncio
import json

import crafter.crafter
import core.managers.httpSessionManager

async def main():
    print(f" ∧,,∧\n"
          "( `•ω•) 。•。︵\n"
          "/　 　ο—ヽ二二ラ))\n"
          "し———J\n")
    try:
        await core.managers.httpSessionManager.HTTPSessionManager().start()
        print(await crafter.crafter.get_ingredients())
    finally:
        await core.managers.httpSessionManager.HTTPSessionManager().close()


if __name__ == '__main__':
    asyncio.run(main())

import asyncio
import time

import core.managers.httpSessionManager
import crafter.base_recipe
import crafter.base_recipe_gpu
import crafter.config.example.spell_ring
import crafter.crafter
import crafter.ingredient
import crafter.recipe


async def craft():
    t = time.time()
    config = await crafter.config.example.spell_ring.SpellRingConfig.load()
    res = crafter.base_recipe_gpu.get_best_recipes_gpu(config)
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
            # f"{eff_defagi(item)} def+agi "
            f"{(item.durability + 735000) // 1000} dura   "
            # f"{r}"
            )


if __name__ == '__main__':
    asyncio.run(main())

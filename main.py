import asyncio
import time

import core.managers.httpSessionManager
import crafting.config.example.spell_ring2
import crafting.ingredient
import crafting.optimizer
import crafting.recipe
import crafting.config.example.base_recipe
import crafting.base_recipes
import crafting.config.example.hp_ring


async def craft():
    t = time.time()
    config = await crafting.config.example.hp_ring.SpellRingConfig.load()
    res = crafting.optimizer.get_best_recipes_gpu(config)
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


def print_recipe(r: crafting.recipe.Recipe) -> str:
    item = r.build()
    return (f"https://hppeng-wynn.github.io/crafter/#1{r.b64_hash()}9m91 "
            f"{item.identifications['spellDamage'].max} sd "
            f"{item.identifications['thunderDamage'].max} td "
            f"{item.identifications['airDamage'].max} ad "
            # f"{eff_defagi(item)} def+agi "
            f"{(item.durability + 735000) // 1000} dura   "
            # f"{r}"
            )


if __name__ == '__main__':
    asyncio.run(main())

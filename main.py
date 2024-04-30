import time

import craft.base_recipes
import craft.config.example.base_recipe
import craft.config.example.spell_ring
import craft.ingredient
import craft.optimizerBruteForce
import craft.recipe


def craft_fun():
    t = time.time()
    config = craft.config.example.spell_ring.SpellRingConfig.load()
    res = craft.optimizer.get_best_recipes_gpu(config)
    print(f"Time taken: {time.time() - t:.2f}s")
    print('\n'.join(map(print_recipe, res)))


def main():
    print(f" ∧,,∧\n"
          "( `•ω•) 。•。︵\n"
          "/　 　ο—ヽ二二ラ))\n"
          "し———J\n")
    craft_fun()


def print_recipe(r: craft.recipe.Recipe) -> str:
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
    main()

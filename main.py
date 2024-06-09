import craft.base_recipes
import craft.config.example.base_recipe
import craft.config.example.spell_ring
import craft.fastHybridOptimizer
import craft.ingredient
import craft.optimizerBruteForce
import craft.recipe
from craft.config.base import HybridOptimizerConfig


def score(ingr: craft.ingredient.Ingredient) -> float:
    return (
            100 * ingr.identifications['spellDamage'].max
            + 30 * ingr.identifications['manaRegen'].max
            + 12 * ingr.identifications['rawSpellDamage'].max
            + 8 * ingr.identifications['earthDamage'].max
            + 4 * ingr.identifications['thunderDamage'].max
            + 4 * ingr.identifications['waterDamage'].max
            + 17 * ingr.identifications['fireDamage'].max
            + 64 * ingr.identifications['airDamage'].max
            + ingr.durability / 100000)


def main():
    print(f" ∧,,∧\n"
          "( `•ω•) 。•。︵\n"
          "/　 　ο—ヽ二二ラ))\n"
          "し———J\n")

    cfg = HybridOptimizerConfig(
        ingredients=list(i for i in craft.ingredient.get_all_ingredients().values()
                         if i.modifiers.abs_total() == 0 and 'tailoring' in i.requirements.skills),
        score_function=score,
        crafting_skill='tailoring',
        relevant_ids=[craft.ingredient.IdentificationType.MANA_REGEN,
                      craft.ingredient.IdentificationType.SPELL_DAMAGE]
    )

    cfg.set_min_durability(90)
    cfg.set_max_str_req(25)
    cfg.set_max_dex_req(23)
    cfg.set_max_int_req(77)
    cfg.set_max_def_req(0)
    cfg.set_max_agi_req(110)
    cfg.set_identification_min(craft.ingredient.IdentificationType.MANA_REGEN, 13)
    cfg.set_identification_min(craft.ingredient.IdentificationType.RAW_INTELLIGENCE, 0)
    cfg.set_identification_min(craft.ingredient.IdentificationType.RAW_STRENGTH, 0)

    res = craft.fastHybridOptimizer.optimize(cfg)
    print_recipe(res)


def print_recipe(r: craft.recipe.Recipe) -> str:
    item = r.build()
    print(f"https://hppeng-wynn.github.io/crafter/#1{r.b64_hash()}9i91 "
            f"{item.identifications['spellDamage'].max} sd "
            f"{item.identifications['rawSpellDamage'].max} raw sd "
            f"{item.identifications['airDamage'].max} ad "
            f"{item.identifications['fireDamage'].max} fd "
            # f"{eff_defagi(item)} def+agi "
            f"{(item.durability + 735000) // 1000} dura   "
            # f"{r}"
            )


if __name__ == '__main__':
    main()

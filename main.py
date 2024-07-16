import craft.old.base_recipes
import craft.old.config.example.spell_ring
import craft.old.fastHybridOptimizer
import craft.old.ingredient
import craft.old.optimizerBruteForce
import craft.old.recipe
from craft.old.config import HybridOptimizerConfig


def score(ingr: craft.old.ingredient.Ingredient) -> float:
    return (
            100 * ingr.identifications['spellDamage'].max
            + 56 * ingr.identifications['thunderDamage'].max
            + 35 * ingr.identifications['airDamage'].max
            + ingr.durability / 100000)


def main():
    print(f" ∧,,∧\n"
          "( `•ω•) 。•。︵\n"
          "/　 　ο—ヽ二二ラ))\n"
          "し———J\n")

    cfg = HybridOptimizerConfig(
        ingredients=list(i for i in craft.old.ingredient.get_all_ingredients().values()
                         if i.modifiers.abs_total() == 0 and craft.old.ingredient.Skill('jeweling') in i.requirements.skills),
        score_function=score,
        crafting_skill=craft.old.ingredient.Skill('jeweling'),
        relevant_ids=[]
    )

    cfg.set_min_durability(30)
    cfg.set_max_str_req(100)
    cfg.set_max_dex_req(120)
    cfg.set_max_int_req(65)
    cfg.set_max_def_req(0)
    cfg.set_max_agi_req(0)
    cfg.set_identification_min(craft.old.ingredient.IdentificationType.MANA_REGEN, 0)
    cfg.set_identification_min(craft.old.ingredient.IdentificationType.RAW_INTELLIGENCE, 0)

    res = craft.old.fastHybridOptimizer.optimize(cfg)
    print_recipe(res)


def print_recipe(r: craft.old.recipe.Recipe):
    item = r.build("a")
    print(f"https://hppeng-wynn.github.io/crafter/#1{item.name}9m91 "
            f"{item.identifications['spellDamage'].max} sd "
            f"{item.identifications['thunderDamage'].max} td "
            f"{item.identifications['airDamage'].max} ad "
            # f"{eff_defagi(item)} def+agi "
            f"{(item.durability + 735000) // 1000} dura   "
            # f"{r}"
            )


if __name__ == '__main__':
    main()

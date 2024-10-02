import craft.optimizer_cp
import wynndata.ingredient
from wynndata.ingredient import Profession


def main():
    # Crafter configuration
    profession = Profession.ALCHEMISM
    ingredients = list(i for i in wynndata.ingredient.get_all_ingredients().values()
                       if profession in i.skills
                       and (i.durability > 0
                            or i.duration > 0
                            or i.modifiers.abs_total() != 0
                            # or i.requirements.abs_sp_total != 0
                            or i.identifications.rawHealth.abs_max != 0
                            ))

    solver = craft.optimizer_cp.CPRecipeOptimizer(ingredients=ingredients, profession=profession.value)
    recipe = solver.recipe

    solver.set_objective((0
                          + recipe.identifications.rawHealth.abs_max * 1000
                          + recipe.durability))

    solver.add(recipe.durability >= 30)
    # solver.add(recipe.requirements.strength <= 0)
    # solver.add(recipe.requirements.dexterity <= 0)
    # solver.add(recipe.requirements.intelligence <= 0)
    # solver.add(recipe.requirements.defence <= 0)
    # solver.add(recipe.requirements.agility <= 0)

    print(f"Finding optimal recipe with {len(ingredients)} unique ingredients...")
    print(solver.find_best())


if __name__ == '__main__':
    main()

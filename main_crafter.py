import craft.optimizer_cp
import wynndata.ingredient
from wynndata.ingredient import Profession


def main():
    # Crafter configuration
    profession = Profession.COOKING
    ingredients = list(i for i in wynndata.ingredient.get_all_ingredients().values()
                       if profession in i.skills
                       and (i.durability > 0
                            or i.duration > 0
                            or i.modifiers.abs_total() != 0
                            # or i.requirements.abs_sp_total != 0
                            or i.identifications.gatherXpBonus.abs_max != 0
                            or i.identifications.gatherSpeed.abs_max != 0
                            # or i.name == "Ivy Sprout"
                            or i.charges != 0
                            )
                       # and i.requirements.level <= 103
                    )


    solver = craft.optimizer_cp.CPRecipeOptimizer(ingredients=ingredients, profession=profession.value)
    recipe = solver.recipe

    solver.set_objective((0
                          + recipe.identifications.gatherXpBonus.abs_max * 10000
                          + recipe.duration
                          + recipe.charges * 1000))

    solver.add(recipe.duration >= 1000)
    solver.add(recipe.charges >= 6)
    solver.add(recipe.identifications.gatherSpeed.abs_max >= 0)
    # solver.add(recipe.requirements.intelligence <= 0)
    # solver.add(recipe.requirements.defence <= 0)
    # solver.add(recipe.requirements.agility <= 0)

    print(f"Finding optimal recipe with {len(ingredients)} unique ingredients...")
    print(solver.find_best())


if __name__ == '__main__':
    main()

import craft.optimizer_cp
import wynndata.ingredient
from wynndata.ingredient import Profession


def main():
    # Crafter configuration
    profession = Profession.ARMOURING
    ingredients = list(i for i in wynndata.ingredient.get_all_ingredients().values()
                       if profession in i.skills
                       and (i.durability > 0
                            #or i.duration > 0
                            or i.modifiers.abs_total() != 0
                            or i.requirements.abs_sp_total != 0
                            or i.identifications.rawHealth.abs_max != 0
                            or i.identifications.rawDefence.abs_max != 0
                            or i.identifications.rawAgility.abs_max != 0
                            or i.identifications.rawStrength.abs_max != 0
                            or i.identifications.rawDexterity.abs_max != 0
                            or i.identifications.waterDamage.abs_max != 0
                            or i.identifications.spellDamage.abs_max != 0
                            ))

    solver = craft.optimizer_cp.CPRecipeOptimizer(ingredients=ingredients, profession=profession.value)
    recipe = solver.recipe

    solver.set_objective((0
                          + recipe.identifications.rawHealth.abs_max * 100
                          + recipe.identifications.rawDefence.abs_max * 15000
                            + recipe.identifications.rawAgility.abs_max * 15000
                            + recipe.identifications.rawStrength.abs_max * 8000
                            + recipe.identifications.rawDexterity.abs_max * 8000
                            + recipe.identifications.waterDamage.abs_max * 10000
                            + recipe.identifications.spellDamage.abs_max * 7000
                          + recipe.durability))

    solver.add(recipe.identifications.manaRegen.abs_max >= -5)

    solver.add(recipe.durability >= 180)
    solver.add(recipe.requirements.strength <= 24)
    solver.add(recipe.requirements.dexterity <= 30)
    solver.add(recipe.requirements.intelligence <= 120)
    solver.add(recipe.requirements.defence <= 40)
    solver.add(recipe.requirements.agility <= 40)

    print(f"Finding optimal recipe with {len(ingredients)} unique ingredients...")
    print(solver.find_best())


if __name__ == '__main__':
    main()

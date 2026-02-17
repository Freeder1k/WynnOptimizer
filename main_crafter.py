import time

import craft.optimizer_cp
import wynndata.ingredient
from cp_utils import calc
from wynndata.ingredient import Profession


def main():
    # Crafter configuration (Example: acolyte healing helmet)
    profession = Profession.ARMOURING

    # Choose ingredients to use in the recipe.
    ingredients = list(i for i in wynndata.ingredient.get_all_ingredients().values()
                       if profession in i.skills
                       and (False
                            or i.durability > 0
                            or i.modifiers.abs_total() != 0
                            or i.identifications.waterDamage.abs_max != 0
                            or i.identifications.healingEfficiency.abs_max != 0
                            or i.identifications.rawHealth.abs_max != 0
                            )
                       and i.name not in ['Unicorn Horn']
                       )

    # Initialize solver
    solver = craft.optimizer_cp.CPRecipeOptimizer(ingredients=ingredients, profession=profession.value)
    recipe = solver.recipe

    # helper function to calculate acolyte healing
    healing = calc.healing(
        recipe.identifications,
        solver.model,
        base_health=50000 + 3518,
        base_healing_efficiency=200,
        base_water_dmg=250,
        fluid_healing=True,
        radiance_mult=30
    )

    # Set the objective
    solver.set_objective(
        healing     # Note: this value is already scaled up a lot
        + recipe.identifications.manaRegen.abs_max * 10000
        + recipe.durability
    )

    # Set some constraints (note: the more you add, the longer the solver will take to find the optimal recipe)
    solver.add(recipe.identifications.manaRegen.abs_max >= 0)

    solver.add(recipe.durability >= 10)

    # Set the maximum skill point requirements
    solver.add(recipe.requirements.intelligence <= 100)
    solver.add(recipe.requirements.defence <= 110)

    # Run the solver
    print(f"Finding optimal recipe with {len(ingredients)} unique ingredients...")
    t1 = time.time()
    print(solver.find_best(num_workers=0))
    print(f"Time taken: {time.time() - t1:.2f}s")

if __name__ == '__main__':
    main()

import craft.optimizerCP
import wynndata.ingredient


def main():
    ingredients = list(i for i in wynndata.ingredient.get_all_ingredients().values()
                       if wynndata.ingredient.Profession('armouring') in i.skills
                       and (i.durability > 0
                            # or i.identifications.healingEfficiency.abs_max != 0
                            # or i.identifications.manaRegen.abs_max != 0
                            # or i.identifications.rawHealth.abs_max != 0
                            # or i.identifications.waterDamage.abs_max != 0
                            # or i.identifications.thunderDamage.abs_max != 0
                            # or i.identifications.spellDamage.abs_max != 0
                            # or i.identifications.lootBonus.abs_max != 0
                            # or i.identifications.lootQuality.abs_max != 0
                            or i.requirements.sp_total != 0
                            or i.identifications.rawSpellDamage.abs_max != 0
                            or i.modifiers.abs_total() != 0))
    # ingredients = [i for i in ingredients if i.name != "Elephelk Trunk"]
    print(len(ingredients))
    solver = craft.optimizerCP.CPRecipeOptimizer(
        ingredients=ingredients,
    )

    recipe = solver.recipe

    # water_dmg_var = solver.model.new_int_var(0, 5000, "water_dmg")
    # health_var = solver.model.new_int_var(20000, 40000, "health")
    # healing_eff_var = solver.model.new_int_var(0, 500, "healing_eff")
    #
    # solver.model.add(water_dmg_var == 3 * recipe.identifications.waterDamage.abs_max + 1000 + 3 * 32)
    # solver.model.add(health_var == recipe.identifications.rawHealth.abs_max + 28090)
    # solver.model.add(healing_eff_var == recipe.identifications.healingEfficiency.abs_max + 100 + 160)
    #
    # water_x_hp = solver.model.new_int_var(0, 160000000, "water_x_hp")
    # solver.model.add_multiplication_equality(water_x_hp, water_dmg_var, health_var)
    #
    # healing = solver.model.new_int_var(0, 80000000000, "healing")
    # solver.model.add_multiplication_equality(healing, water_x_hp, healing_eff_var)
    #
    solver.set_objective(((0
                           + recipe.identifications.rawSpellDamage.abs_max
                           ) * 100
                          + recipe.durability))

    solver.add(recipe.durability >= 100)
    solver.add(recipe.requirements.strength <= 10)
    solver.add(recipe.requirements.dexterity <= 70)
    solver.add(recipe.requirements.intelligence <= 80)
    solver.add(recipe.requirements.defence <= 100)
    solver.add(recipe.requirements.agility <= 10)

    print(solver.find_best())


if __name__ == '__main__':
    main()

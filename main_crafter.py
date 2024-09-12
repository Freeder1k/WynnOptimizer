import craft.optimizer_cp
import wynndata.ingredient


def main():
    ingredients = list(i for i in wynndata.ingredient.get_all_ingredients().values()
                       if wynndata.ingredient.Profession('tailoring') in i.skills
                       and (i.durability > 0
                            # or i.identifications.healingEfficiency.abs_max != 0
                            or i.identifications.manaSteal.abs_max != 0
                            # or i.identifications.rawHealth.abs_max != 0
                            # or i.identifications.waterDamage.abs_max != 0
                            # or i.identifications.thunderDamage.abs_max != 0
                            # or i.identifications.spellDamage.abs_max != 0
                            or i.identifications.walkSpeed.abs_max != 0
                            # or i.identifications.lootBonus.abs_max != 0
                            # or i.identifications.lootQuality.abs_max != 0
                            or i.identifications.manaRegen.abs_max != 0
                            # or i.requirements.sp_total != 0
                            # or i.identifications.rawSpellDamage.abs_max != 0
                            or i.identifications.rawMainAttackDamage.abs_max != 0
                            or i.identifications.rawDamage.abs_max != 0
                            or i.identifications.rawEarthMainAttackDamage.abs_max != 0
                            or i.identifications.rawEarthDamage.abs_max != 0
                            or i.identifications.rawElementalDamage.abs_max != 0
                            or i.identifications.rawElementalMainAttackDamage.abs_max != 0
                            or i.identifications.mainAttackDamage.abs_max != 0
                            or i.identifications.damage.abs_max != 0
                            or i.identifications.earthMainAttackDamage.abs_max != 0
                            or i.identifications.earthDamage.abs_max != 0
                            or i.identifications.elementalDamage.abs_max != 0
                            or i.identifications.elementalMainAttackDamage.abs_max != 0
                            or i.modifiers.abs_total() != 0))
    ingredients = [i for i in ingredients if i.name != "Void Particulates"]
    print(len(ingredients))
    solver = craft.optimizer_cp.CPRecipeOptimizer(
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
    solver.set_objective((recipe.identifications.rawMainAttackDamage.abs_max * 40000
                          + recipe.identifications.rawDamage.abs_max * 40000
                          + recipe.identifications.rawEarthMainAttackDamage.abs_max * 40000
                          + recipe.identifications.rawEarthDamage.abs_max * 40000
                          + recipe.identifications.rawElementalDamage.abs_max * 40000
                          + recipe.identifications.rawElementalMainAttackDamage.abs_max * 40000
                          + recipe.identifications.mainAttackDamage.abs_max * 604900
                          + recipe.identifications.damage.abs_max * 604900
                          + recipe.identifications.earthDamage.abs_max * 604900
                          + recipe.identifications.elementalDamage.abs_max * 604900
                          + recipe.identifications.earthMainAttackDamage.abs_max * 604900
                          + recipe.identifications.elementalMainAttackDamage.abs_max * 604900
                          # + recipe.identifications.manaRegen.abs_max * 300000
                          # + recipe.identifications.manaSteal.abs_max * 300000
                          # + recipe.identifications.walkSpeed.abs_max * 300000
                          + recipe.durability))

    solver.add(recipe.durability >= 108)
    solver.add(recipe.identifications.manaRegen.abs_max >= 0)
    solver.add(recipe.identifications.walkSpeed.abs_max >= 0)
    solver.add(recipe.requirements.strength <= 100)
    solver.add(recipe.requirements.dexterity <= 65)
    solver.add(recipe.requirements.intelligence <= 0)
    solver.add(recipe.requirements.defence <= 65)
    solver.add(recipe.requirements.agility <= 0)

    print(solver.find_best())


if __name__ == '__main__':
    main()

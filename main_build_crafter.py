import craft.build_optimizer_cp
import wynndata.ingredient


def main():
    ingredients = list(i for i in wynndata.ingredient.get_all_ingredients().values()
                       if (i.durability > 0
                            # or i.identifications.healingEfficiency.abs_max != 0
                            # or i.identifications.manaSteal.abs_max != 0
                            # or i.identifications.rawHealth.abs_max != 0
                            # or i.identifications.waterDamage.abs_max != 0
                            # or i.identifications.thunderDamage.abs_max != 0
                            # or i.identifications.spellDamage.abs_max != 0
                            # or i.identifications.walkSpeed.abs_max != 0
                            # or i.identifications.lootBonus.abs_max != 0
                            # or i.identifications.lootQuality.abs_max != 0
                            # or i.identifications.manaRegen.abs_max != 0
                            # or i.requirements.sp_total != 0
                            # or i.identifications.rawSpellDamage.abs_max != 0
                            # or i.identifications.rawMainAttackDamage.abs_max != 0
                            # or i.identifications.rawDamage.abs_max != 0
                            # or i.identifications.rawEarthMainAttackDamage.abs_max != 0
                            # or i.identifications.rawEarthDamage.abs_max != 0
                            # or i.identifications.rawElementalDamage.abs_max != 0
                            # or i.identifications.rawElementalMainAttackDamage.abs_max != 0
                            # or i.identifications.rawElementalSpellDamage.abs_max != 0
                            # or i.identifications.mainAttackDamage.abs_max != 0
                            # or i.identifications.damage.abs_max != 0
                            # or i.identifications.earthMainAttackDamage.abs_max != 0
                            # or i.identifications.waterSpellDamage.abs_max != 0
                            # or i.identifications.thunderSpellDamage.abs_max != 0
                            # or i.identifications.earthDamage.abs_max != 0
                            # or i.identifications.elementalDamage.abs_max != 0
                            # or i.identifications.elementalMainAttackDamage.abs_max != 0
                            # or i.identifications.elementalSpellDamage.abs_max != 0
                           # or i.identifications.rawDexterity.abs_max != 0
                           or i.identifications.gatherSpeed.abs_max != 0
                           or i.identifications.gatherXpBonus.abs_max != 0
                            or i.modifiers.abs_total() != 0)
                            and i.requirements.level <= 103
                       )
    ingredients_lists = []
    ingredients = [i for i in ingredients if i.name != "Squid Beak"]
    # add a filter?
    # armouring, tailoring, jeweling, weaponsmithing, woodworking, cooking, alchemism, scribing
    professions = ['cooking', 'alchemism', 'scribing']
    # professions = ['tailoring']
    for prof in professions:
        ingredients_lists.append(list(i for i in ingredients if wynndata.ingredient.Profession(prof) in i.skills))
    print([f"{p}: {len(i)}" for p, i in zip(professions, ingredients_lists)])
    solver = craft.build_optimizer_cp.CPBuildRecipeOptimizer(
        ingredients_lists=ingredients_lists,
        professions = professions
    )

    recipes = solver.recipes

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
    # noinspection PyTypeChecker
    solver.set_objective(sum(r.identifications.gatherSpeed.abs_max * 100000
                             + r.identifications.gatherXpBonus.abs_max * 1000
                             + r.durability
                             for r in recipes))
    # solver.set_objective(sum(r.identifications.rawDamage.abs_max * 54999
    #                          + r.identifications.rawWaterSpellDamage.abs_max * 40109
    #                          + r.identifications.rawWaterDamage.abs_max * 40109
    #                          + r.identifications.rawThunderSpellDamage.abs_max * 14890
    #                          + r.identifications.rawThunderDamage.abs_max * 14890
    #                          + r.identifications.rawElementalDamage.abs_max * 54999
    #                          + r.identifications.rawElementalSpellDamage.abs_max * 54999
    #                          + r.identifications.rawSpellDamage.abs_max * 54999
    #                          + r.identifications.spellDamage.abs_max * 411718
    #                          + r.identifications.damage.abs_max * 411718
    #                          + r.identifications.waterDamage.abs_max * 300250
    #                          + r.identifications.thunderDamage.abs_max * 111468
    #                          + r.identifications.elementalDamage.abs_max * 411718
    #                          + r.identifications.waterSpellDamage.abs_max * 300250
    #                          + r.identifications.thunderSpellDamage.abs_max * 111468
    #                          + r.identifications.elementalSpellDamage.abs_max * 411718
    #                          + r.durability
    #                          for r in recipes))

    # solver.add(sum(r.identifications.manaRegen.abs_max for r in recipes) >= 0)
    # solver.add(sum(r.identifications.rawHealth.abs_max for r in recipes) >= 0)
    for recipe in recipes:
        solver.add(recipe.duration >= 150)
        # solver.add(recipe.requirements.strength <= 60)
        # solver.add(recipe.requirements.dexterity <= 60)
        # solver.add(recipe.requirements.intelligence <= 129)
        # solver.add(recipe.requirements.defence <= 0)
        # solver.add(recipe.requirements.agility <= 0)
        # solver.add(recipe.identifications.rawStrength.abs_max >= 0)
        # solver.add(recipe.identifications.rawDexterity.abs_max >= 0)

    print(solver.find_best())


if __name__ == '__main__':
    main()

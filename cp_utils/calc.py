from ortools.sat.python.cp_model import CpModel, IntVar

from craft.cp_recipe import CPRecipe


def healing(
        recipe: CPRecipe,
        model: CpModel,
        base_water_dmg=0,
        base_health=0,
        base_healing_efficiency=0,
        fluid_healing=True,
        radiance_mult=0
) -> IntVar:
    """
    Create a linear expression for the shaman healing value represented by the given cp-identifications.
    Base stats can be set to adjust for equipment/consumables.
    This adds 5 new integer variables, 3 new linear constraints and 2 new multiplication constraints to the model.
    The result is an IntVar representing the healing value times 400000.
    This does not work for negative stat values.
    :param recipe: The recipe containing the identifications to use for the calculation.
    :param model: CpModel object to add the constraints to
    :param base_water_dmg: Base water damage to use for the calculation (after radiance application)
    :param base_health: Base health to use for the calculation (after radiance application)
    :param base_healing_efficiency: Base healing efficiency to use for the calculation (after radiance application)
    :param fluid_healing: Whether to use fluid healing or not
    :param radiance_mult: Multiplier to use for the radiance effect (example: 30 for 30% radiance) (not added onto base stats)
    """
    identifications = recipe.identifications
    radiance_mult = (radiance_mult // 10) + 10

    # Upper bound estimations for the variables
    if fluid_healing:
        wd_max = min(300, base_water_dmg) + 100
        wd_min = base_water_dmg - 100
    hp_max = 10000 * radiance_mult + base_health
    hp_min = base_health - 10000
    he_max = 500 * radiance_mult + 100 + base_healing_efficiency
    he_min = base_healing_efficiency - 500

    # mult all by 2 since .avg = .min + .max
    if fluid_healing:
        wd_min *= 2
        wd_max *= 2
    hp_min *= 2
    hp_max *= 2
    he_min *= 2
    he_max *= 2


    if fluid_healing:
        water_dmg_var = model.new_int_var(wd_min, wd_max, "water_dmg")
    health_var = model.new_int_var(hp_min, hp_max, "health")
    healing_eff_var = model.new_int_var(he_min, he_max, "healing_eff")

    if fluid_healing:
        model.add_min_equality(
            water_dmg_var,
            (3 * radiance_mult * identifications.waterDamage.avg + (1000 + 3 * base_water_dmg) * 2,
             1750 * 2)  # caps at 75% (+100% base)
        )
    model.add(health_var == radiance_mult * identifications.rawHealth.avg + base_health * 2)
    model.add(healing_eff_var == radiance_mult * identifications.healingEfficiency.avg + (100 + base_healing_efficiency) * 2)

    if fluid_healing:
        wd_x_hp_ub = wd_max * hp_max
        wd_x_hp_var = model.new_int_var(0, wd_x_hp_ub, "water_x_hp")
        model.add_multiplication_equality(wd_x_hp_var, water_dmg_var, health_var)
    else:
        wd_x_hp_ub = hp_max
        wd_x_hp_var = health_var

    healing_ub = wd_x_hp_ub * he_max
    healing_var = model.new_int_var(0, healing_ub, "healing")
    model.add_multiplication_equality(healing_var, wd_x_hp_var, healing_eff_var)

    return healing_var

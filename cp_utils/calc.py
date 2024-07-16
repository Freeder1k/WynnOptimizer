from ortools.sat.python.cp_model import CpModel, IntVar

from cp_utils.cp_identifications import CPIdentifications


def healing(identifications: CPIdentifications, model: CpModel, base_water_dmg=0, base_health=0,
            base_healing_efficiency=0) -> IntVar:
    """
    Create a linear expression for the shaman healing value represented by the given cp-identifications.
    Base stats can be set to adjust for equipment/consumables.
    This adds 5 new integer variables, 3 new linear constraints and 2 new multiplication constraints to the model.
    The result is an IntVar representing the healing value times 400000.
    This does not work for negative stat values.
    """
    wd_ub = 3 * 1000 + 1000 + 3 * base_water_dmg
    hp_ub = 100000 + base_health
    he_ub = 500 + 100 + base_healing_efficiency

    water_dmg_var = model.new_int_var(0, wd_ub, "water_dmg")
    health_var = model.new_int_var(0, hp_ub, "health")
    healing_eff_var = model.new_int_var(0, he_ub, "healing_eff")

    model.add(water_dmg_var == 3 * identifications.waterDamage.abs_max + 1000 + 3 * base_water_dmg)
    model.add(health_var == identifications.rawHealth.abs_max + base_health)
    model.add(healing_eff_var == identifications.healingEfficiency.abs_max + 100 + base_healing_efficiency)

    wd_x_hp_ub = wd_ub * hp_ub
    wd_x_hp_var = model.new_int_var(0, wd_x_hp_ub, "water_x_hp")
    model.add_multiplication_equality(wd_x_hp_var, water_dmg_var, health_var)

    healing_ub = wd_x_hp_ub * he_ub
    healing_var = model.new_int_var(0, healing_ub, "healing")
    model.add_multiplication_equality(healing_var, wd_x_hp_var, healing_eff_var)

    return healing_var

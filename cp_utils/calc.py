from ortools.sat.python.cp_model import CpModel, IntVar

from cp_utils.cp_identifications import CPIdentifications


def healing(identifications: CPIdentifications, model: CpModel, base_health=0, base_healing_efficiency=0,
            base_water_dmg=0, fluid_healing=True, radiance_mult=0) -> IntVar:
    """
    Create a linear expression for the shaman healing value represented by the given cp-identifications.
    Formula: (HP/4) * (1 + HE/100) * (1 + 0.3 * (WD/100))
    Base stats can be set to adjust for equipment/consumables. Radiance is not calculated onto these.
    :param identifications: CPIdentifications object to use for the calculation
    :param model: CpModel object to add the constraints to
    :param base_health: Base health to use for the calculation (after radiance application)
    :param base_healing_efficiency: Base healing efficiency to use for the calculation (after radiance application)
    :param base_water_dmg: Base water damage to use for the calculation (after radiance application)
    :param fluid_healing: Whether to use fluid healing or not
    :param radiance_mult: Multiplier to use for the radiance effect (example: 30 for 30% radiance) (not added onto base stats)
    """
    radiance_mult = (radiance_mult // 10) + 10

    # Define bounds, 10 and 2 are scaling for radiance and .avg
    hp_ub = 200000 * 25 * 10 * 2
    hp_lb = -hp_ub
    he_ub = 500 * 10 * 2
    he_lb = -he_ub
    wd_ub = 1750 * 10
    wd_lb = -wd_ub
    heal_ub = wd_ub * hp_ub * he_ub
    heal_lb = -heal_ub

    health_var = model.new_int_var(hp_lb, hp_ub, "healing_calc:health")
    model.add(
        health_var == (radiance_mult * identifications.rawHealth.abs_max
                      + base_health * 10) * 25
    )

    healing_eff_var = model.new_int_var(he_lb, he_ub, "healing_calc:healing_eff")
    model.add(
        healing_eff_var == 100 * 10
                           + identifications.healingEfficiency.abs_max * radiance_mult
                           + base_healing_efficiency * 10
    )

    water_dmg_var = model.new_int_var(wd_lb, wd_ub, "healing_calc:water_dmg")
    if fluid_healing:
        model.add_min_equality(
            water_dmg_var,
            (
                10 * 100 * 10
                + 3 * radiance_mult * identifications.waterDamage.abs_max
                + 3 * base_water_dmg * 10,
                1750 * 10   # caps at 75% (+100% base)
             )
        )
    else:
        model.add(water_dmg_var == 1)

    heal_var = model.new_int_var(heal_lb, heal_ub, "healing_calc:healing")
    model.add_multiplication_equality(heal_var, [health_var, healing_eff_var, water_dmg_var])

    return heal_var

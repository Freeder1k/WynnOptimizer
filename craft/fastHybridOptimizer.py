import time
from multiprocessing import Pool

import craft.base_recipes
import craft.ingredient
import craft.optimizerLP
import craft.recipe
from craft.config.base import HybridOptimizerConfig


def _runLPOptimizer(mods, base_r, cfg):
    mods = tuple(int(m) for m in mods)
    base = base_r.build("a")
    optimizer = craft.optimizerLP.LPRecipeOptimizer(cfg.ingredients, cfg.score_function, mods)
    if cfg.min_charges is not None:
        optimizer.set_min_charges(cfg.min_charges - base.charges)
    if cfg.min_duration is not None:
        optimizer.set_min_duration(cfg.min_duration - base.duration)
    if cfg.min_durability is not None:
        optimizer.set_min_durability(cfg.min_durability - (base.durability // 1000))
    if cfg.max_str_req is not None:
        optimizer.set_max_str_req(cfg.max_str_req - base.requirements.strength)
    if cfg.max_dex_req is not None:
        optimizer.set_max_dex_req(cfg.max_dex_req - base.requirements.dexterity)
    if cfg.max_int_req is not None:
        optimizer.set_max_int_req(cfg.max_int_req - base.requirements.intelligence)
    if cfg.max_def_req is not None:
        optimizer.set_max_def_req(cfg.max_def_req - base.requirements.defence)
    if cfg.max_agi_req is not None:
        optimizer.set_max_agi_req(cfg.max_agi_req - base.requirements.agility)

    for val, sp_types in cfg.max_sp_sum_req:
        optimizer.add_max_sp_sum_req(val, **sp_types)
    for id_type, value in cfg.max_id_reqs.items():
        optimizer.set_identification_max(id_type, value - base.identifications[id_type].pos_max)
    for id_type, value in cfg.min_id_reqs.items():
        optimizer.set_identification_min(id_type, value - base.identifications[id_type].pos_max)

    res_score, res_ingrs = optimizer.find_best()
    if res_score <= 0:
        return 0, []

    ingrs = []
    j = 0
    for ingr in base_r.ingredients:
        if ingr == craft.ingredient.NO_INGREDIENT:
            ingrs.append(res_ingrs[j])
            j += 1
        else:
            ingrs.append(ingr)

    return res_score, ingrs


def optimize(cfg: HybridOptimizerConfig, pool_size=4):
    t = time.time()
    # TODO some base recipes could be getting skipped
    bases = craft.base_recipes.get_base_recipes_gpu(cfg.crafting_skill, cfg.relevant_ids)

    print(f"Found {len(bases)} base recipes. Finding optimal recipes...")

    with Pool(pool_size) as p:
        results = p.starmap(_runLPOptimizer, [(mods, base_r, cfg) for mods, base_r in bases])
        max_score, max_recipe = max(results, key=lambda x: x[0])

    print(f"Total time taken: {time.time() - t:.2f}s")

    if max_score <= 0:
        print("No viable recipes found.")
        return None

    max_recipe = craft.recipe.Recipe(*max_recipe)

    print(f"Best score: {max_score}")

    return max_recipe

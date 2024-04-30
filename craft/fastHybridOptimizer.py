import time
from multiprocessing import Pool

import craft.base_recipes
import craft.ingredient
import craft.optimizerLP
import craft.recipe
import main
from craft.config.base import LinearOptimizerConfigBase


def _runLPOptimizer(mods, base_r, cfg):
    mods = tuple(int(m) for m in mods)
    min_dura = cfg.min_durability + sum([-ingr.durability // 1000 for ingr in base_r.ingredients])
    optimizer = craft.optimizerLP.LPRecipeOptimizer(cfg.ingredients, cfg.score, mods)
    optimizer.set_min_durability(min_dura)
    optimizer.set_max_str_req(0)
    optimizer.set_max_dex_req(0)
    optimizer.set_max_total_sp_req(200)

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


def optimize(cfg: LinearOptimizerConfigBase):
    t = time.time()
    bases = craft.base_recipes.get_base_recipes_gpu(cfg.profession, cfg.relevant_ids)

    with Pool(7) as p:
        results = p.starmap(_runLPOptimizer, [(mods, base_r, cfg) for mods, base_r in bases])
        max_score, max_recipe = max(results, key=lambda x: x[0])
    max_recipe = craft.recipe.Recipe(*max_recipe)

    print()
    print(f"Best score: {max_score}")
    print(main.print_recipe(max_recipe))

    print(f"Time taken: {time.time() - t:.2f}s")

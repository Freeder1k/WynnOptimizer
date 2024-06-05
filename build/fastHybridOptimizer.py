import time
from multiprocessing import Pool

import build.item
import build.optimizerLP
import build.build
from build.config.base import HybridOptimizerConfig
import utils.skillpoints as sp


def _runLPOptimizer(cfg):

    optimizer = build.optimizerLP.LPBuildOptimizer(cfg.items, cfg.score_function, cfg.weapon)
    if cfg.max_str_req is not None:
        optimizer.set_max_str_req(cfg.max_str_req)
    if cfg.max_dex_req is not None:
        optimizer.set_max_dex_req(cfg.max_dex_req)
    if cfg.max_int_req is not None:
        optimizer.set_max_int_req(cfg.max_int_req)
    if cfg.max_def_req is not None:
        optimizer.set_max_def_req(cfg.max_def_req)
    if cfg.max_agi_req is not None:
        optimizer.set_max_agi_req(cfg.max_agi_req)

    for val, sp_types in cfg.max_sp_sum_req:
        optimizer.add_max_sp_sum_req(val, **sp_types)
    for id_type, value in cfg.max_id_reqs.items():
        optimizer.set_identification_max(id_type, value)
    for id_type, value in cfg.min_id_reqs.items():
        optimizer.set_identification_min(id_type, value)

    #result = optimizer.find_bestn2(cfg.N)
    #result = optimizer.find_bestn(cfg.N)
    result = optimizer.find_best_validn(cfg.N)

    return result

def optimize(cfg: HybridOptimizerConfig, pool_size=4):
    t = time.time()

    print(f"Finding top {cfg.N} optimal builds...")

    results = _runLPOptimizer(cfg)

    print(f"Total time taken: {time.time() - t:.2f}s")

    if results[0][0] <= 0:
        print("No viable builds found.")
        return None

    print(f"Number of builds found: {len(results)}")

    print(f"Processing found builds")

    valid_builds = []

    for entry in results:
        b = build.build.Build(cfg.weapon, *entry[1])
        asp = sp.skillpoints(b)
        if sum(asp) < 205:
            valid_builds.append((entry[0], entry[1], cfg.score_function(b.build())))

    valid_builds = sorted(valid_builds, key=lambda x: x[2], reverse=True)

    print(f"Number of valid builds found: {len(valid_builds)}")

    with open('array.txt', 'w') as f:
        for entry in valid_builds:
            f.write(f"{entry}\n")

    max_build = valid_builds[0][1]
    return build.build.Build(cfg.weapon, *max_build)

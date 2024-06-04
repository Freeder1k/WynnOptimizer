import time
from multiprocessing import Pool

import build.item
import build.optimizerLP
import build.build
from build.config.base import HybridOptimizerConfig


def _runLPOptimizer(cfg):

    optimizer = build.optimizerLP.LPBuildOptimizer(cfg.items, cfg.score_function)
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

    result = optimizer.find_bestN2(cfg.N)
    #result = optimizer.find_bestN(cfg.N)

    return result

def optimize(cfg: HybridOptimizerConfig, pool_size=4):
    t = time.time()

    print(f"Finding optimal builds...")

    results = _runLPOptimizer(cfg)
    max_score, max_build = results[0]

    print(f"Total time taken: {time.time() - t:.2f}s")

    if max_score <= 0:
        print("No viable builds found.")
        return None

    max_build = build.build.Build(*max_build)
    print(f"Number of builds found: {len(results)}")
    with open('array.txt', 'w') as f:
        for entry in results:
            f.write(f"{entry}\n")
    print(f"Best score: {max_score}")

    return max_build

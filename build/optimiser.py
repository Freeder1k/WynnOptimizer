import time

import build.item
import build.cpmodelsolver
import build.build
import utils.skillpoints as sp
import ast

masterybonus = [20, 10, 15, 15 ,15]
damageTypes = ["damage", "earthDamage", "thunderDamage",  "waterDamage", "fireDamage", "airDamage"]

def _runCPModelSolver(cfg):
    with open('tempoutput.txt', 'w') as f:
        f.write("")
    with open('isrunning', 'w') as f:
        f.write("True")
    try:
        solver = build.cpmodelsolver.CPModelSolver(cfg.items, cfg.score_function, cfg.weapon)

        for key, value in cfg.max_ids.items():
            solver.add_upper_bound(value + cfg.weapon.identifications[key].max, lambda itm: itm.identifications[key].max)
        for key, value in cfg.min_ids.items():
            solver.add_lower_bound(value - cfg.weapon.identifications[key].max, lambda itm: itm.identifications[key].max)
        for key, value in cfg.max_reqs.items():
            solver.add_max_assignable_sp(value, key)
        for key, value in cfg.max_sp.items():
            solver.add_max_sp(value, key)
        for key, value in cfg.min_sp.items():
            solver.add_min_sp(value, key)

        hive_master = ["Abyss-Imbued Leggings","Boreal-Patterned Crown","Anima-Infused Cuirass","Chaos-Woven Greaves","Elysium-Engraved Aegis","Eden-Blessed Guards","Gaea-Hewn Boots","Hephaestus-Forged Sabatons","Obsidian-Framed Helmet","Twilight-Gilded Cloak","Contrast","Prowess","Intensity"]
        solver.mutual_exclude(hive_master)

        solver.find_best()
        best_score = process_results(cfg, 2)[0][2]

        solver.add_min_score(int(best_score) - 200)
        solver.find_allbest()
    except:
        with open('.isrunning', 'w') as f:
            f.write("False")
        raise

    with open('.isrunning', 'w') as f:
        f.write("False")


def process_results(cfg, sort: int):
    results = []
    with open('tempoutput.txt', 'r') as f:
        lines = f.readlines()
    for line in lines:
        results.append(ast.literal_eval(line))

    for i, entry in enumerate(results):
        items = []
        for n in entry:
            items.append(build.item.get_item(n))
        b = build.build.Build(cfg.weapon, *items)

        builditem = sp.add_sp(b.build(), *b.calc_sp())
        for typ,mas,bon in zip(damageTypes, cfg.mastery, masterybonus):
            builditem.identifications[typ] += bon*mas

        buildscore = cfg.score_function(builditem)
        objectivevalue = sum(cfg.score_function(it) for it in b.items)
        results[i] = (b, buildscore, objectivevalue)

    results = sorted(results, key=lambda x: x[sort], reverse=True)
    return results


def optimise(cfg):
    t = time.time()

    try:
        with open('.isrunning', 'r') as f:
            running = f.readlines()[0]
    except FileNotFoundError:
        running = 'False'
    if running == 'False':
        print(f"Finding optimal builds...")
        _runCPModelSolver(cfg)
    else:
        print(f"Program is currently running, Calculating preliminary results. (Delete file:'isrunning' if this is not the case)")

    results = process_results(cfg, 1)

    print(f"Total time taken: {time.time() - t:.2f}s")

    if len(results) == 0:
        print("No viable builds found.")
    else:
        print(f"Best build: {results[0][0]}, score: {results[0][1]}")
        print(results[0][0].generate_link(cfg.skilltree))
    return results

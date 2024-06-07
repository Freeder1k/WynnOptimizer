import time

import build.item
import build.cpmodelsolver
import build.build
import utils.skillpoints as sp
import ast

def _runCPmodelSolver(cfg):
    with open('tempoutput.txt', 'w') as f:
        f.write("")
    solver = build.cpmodelsolver.CPModelSolver(cfg.items, cfg.score_function, cfg.weapon)

    hive_master = ["Abyss-Imbued Leggings","Boreal-Patterned Crown","Anima-Infused Cuirass","Chaos-Woven Greaves","Elysium-Engraved Aegis","Eden-Blessed Guards","Gaea-Hewn Boots","Hephaestus-Forged Sabatons","Obsidian-Framed Helmet","Twilight-Gilded Cloak","Contrast","Prowess","Intensity"]
    solver.mutual_exclude(hive_master)

    solver.find_allbest()


def optimize(cfg):
    t = time.time()

    print(f"Finding optimal builds...")

    _runCPmodelSolver(cfg)

    results = []
    with open('tempoutput.txt', 'r') as f:
        lines = f.readlines()
    for line in lines:
        results.append(ast.literal_eval(line)[0])

    for i, entry in enumerate(results):
        items = []
        for n in entry:
            items.append(build.item.get_item(n))
        b = build.build.Build(cfg.weapon, *items)

        builditem = sp.add_sp(b.build(), *b.calc_sp())
        buildscore = cfg.score_function(builditem)
        objectivevalue = sum(cfg.score_function(it) for it in b.items)
        results[i] = (b, buildscore, objectivevalue)

    results = sorted(results, key=lambda x: x[1], reverse=True)


    print(f"Total time taken: {time.time() - t:.2f}s")

    if len(results) == 0:
        print("No viable builds found.")
    else:
        print("Best build:")
        print(results[0][0], results[0][1])
    return results

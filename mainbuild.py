import build.fastHybridOptimizer
import build.item
import build.build
from build.config.dmg import DmgConfig
import build.ortoolssolver
import utils.skillpoints as sp
import ast

import faulthandler
faulthandler.enable()

def main():
    print(f" ∧,,∧\n"
          "( `•ω•) 。•。︵\n"
          "/　 　ο—ヽ二二ラ))\n"
          "し———J\n")

    with open('tempoutput.txt', 'w') as f:
        f.write("")
    cfg = DmgConfig()
    solver = build.ortoolssolver.CPModelSolver(cfg.items, cfg.score_function, cfg.weapon)
    results = solver.find_allbest()

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
        buildscore = cfg.score_function(builditem)
        objectivevalue = sum(cfg.score_function(it) for it in b.items)
        results[i] = (b, buildscore, objectivevalue)

    results = sorted(results, key=lambda x: x[1], reverse=True)



    with open('array.txt', 'w') as f:
        for entry in results:
            f.write(f"{entry[0].items}, {entry[1:]}\n")
            #f.write(f"{entry.items}\n")


    '''cfg = DmgConfig()
    res = build.fastHybridOptimizer.optimize(cfg)
    if res is not None:
        print_build(res)'''


def print_build(b: build.build.Build):
    print(b.items)


if __name__ == '__main__':
    main()

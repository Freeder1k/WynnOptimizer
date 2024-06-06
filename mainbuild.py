import build.fastHybridOptimizer
import build.item
import build.build
from build.config.dmg import DmgConfig
import build.ortoolssolver
import utils.skillpoints as sp
import faulthandler
faulthandler.enable()

def main():
    print(f" ∧,,∧\n"
          "( `•ω•) 。•。︵\n"
          "/　 　ο—ヽ二二ラ))\n"
          "し———J\n")

    cfg = DmgConfig()
    solver = build.ortoolssolver.CPModelSolver(cfg.items, cfg.score_function, cfg.weapon)
    results = solver.find_allbest()

    for i, entry in enumerate(results):
        b = entry[0]
        builditem = sp.add_sp(b.build(), *b.calc_sp())
        buildscore = cfg.score_function(builditem)
        objectivevalue = sum(cfg.score_function(it) for it in b.items)
        results[i] = (b, buildscore, objectivevalue, entry[1])

    results = sorted(results, key=lambda x: x[2], reverse=True)



    with open('array.txt', 'w') as f:
        for entry in results:
            f.write(f"{entry[0].items} {entry[1]} {entry[2]} {entry[3]}\n")
            #f.write(f"{entry.items}\n")


    '''cfg = DmgConfig()
    res = build.fastHybridOptimizer.optimize(cfg)
    if res is not None:
        print_build(res)'''


def print_build(b: build.build.Build):
    print(b.items)


if __name__ == '__main__':
    main()

import build.fastHybridOptimizer
import build.item
import build.build
from build.config.dmg import DmgConfig
import build.ortoolssolver
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

    with open('array.txt', 'w') as f:
        for entry in results:
            f.write(f"{entry.items}\n")


    '''cfg = DmgConfig()
    res = build.fastHybridOptimizer.optimize(cfg)
    if res is not None:
        print_build(res)'''


def print_build(b: build.build.Build):
    print(b.items)


if __name__ == '__main__':
    main()

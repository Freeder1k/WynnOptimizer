import build.fastHybridOptimizer
import build.item
import build.build
from build.config.dmg import DmgConfig
import utils.skillpoints as sp
import build.findBuilds as solver

import faulthandler
faulthandler.enable()

def main():
    print(f" ∧,,∧\n"
          "( `•ω•) 。•。︵\n"
          "/　 　ο—ヽ二二ラ))\n"
          "し———J\n")

    cfg = DmgConfig()
    results = solver.optimize(cfg)

    with open('array.txt', 'w') as f:
        for entry in results:
            f.write(f"{entry}\n")


if __name__ == '__main__':
    main()

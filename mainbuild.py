import build.fastHybridOptimizer
import build.item
import build.build
from build.config.dmg import DmgConfig


def main():
    print(f" ∧,,∧\n"
          "( `•ω•) 。•。︵\n"
          "/　 　ο—ヽ二二ラ))\n"
          "し———J\n")

    cfg = DmgConfig()
    res = build.fastHybridOptimizer.optimize(cfg)
    print_build(res)


def print_build(b: build.build.Build):
    print(b.items)


if __name__ == '__main__':
    main()

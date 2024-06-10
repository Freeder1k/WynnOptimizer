from build.config.dmg import DmgConfig
import build.optimiser as optimiser
import os
import faulthandler
faulthandler.enable()

def main():
    print(f" ∧,,∧\n"
          "( `•ω•) 。•。︵\n"
          "/　 　ο—ヽ二二ラ))\n"
          "し———J\n")

    cfg = DmgConfig()
    results = optimiser.optimise(cfg)

    os.makedirs('output', exist_ok=True)
    with open("output/"+cfg.weapon.name+str(len(results)), 'w') as f:
        for entry in results:
            f.write(f"{entry}\n")


if __name__ == '__main__':
    main()

import build.optimiser as optimiser
import os
import faulthandler
faulthandler.enable()

def main():
    print(f" ∧,,∧\n"
          "( `•ω•) 。•。︵\n"
          "/　 　ο—ヽ二二ラ))\n"
          "し———J\n")

    from build.config.grimreg import DmgConfig
    cfg = DmgConfig()
    results = optimiser.optimise(cfg)


    with open('.isrunning', 'r') as f:
        running = f.readlines()[0]
    if running == 'True':
        filename = 'results.txt'
    else:
        filename = cfg.weapon.name+str(len(results))+'.txt'


    os.makedirs('output', exist_ok=True)
    with open("output/"+filename, 'w') as f:
        for entry in results:
            f.write(f"{entry}\n")


if __name__ == '__main__':
    main()

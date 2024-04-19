import signal
from multiprocessing import Pool

from core.optimizer import bruteForce
from . import ingredient, recipe


def get_effectiveness_combos(
        ingredients: list[ingredient.Ingredient],
        pool_size: int = 4) -> dict[tuple[int, ...], recipe.Recipe]:
    ingredients.append(ingredient.NO_INGREDIENT)

    with Pool(pool_size, initializer=initializer) as p:
        try:
            results = p.starmap(_get_combos, [(i, ingredients) for i in ingredients])
        except KeyboardInterrupt:
            p.terminate()
            raise KeyboardInterrupt

    res = {}
    for r in results:
        for k, v in r.items():
            if k not in res or v.build().durability > res[k].build().durability:
                res[k] = v

    combos = sorted(res.keys(), key=lambda x: len(x), reverse=True)

    print(len(res))
    for c1 in combos:
        if c1 not in res:
            continue
        for sub_c in bruteForce.generate_all_subpermutations(*c1, ordered=True):
            if sub_c in res and res[sub_c].build().durability <= res[c1].build().durability:
                del res[sub_c]

    if () in res:
        del res[()]

    print(len(res))

    combos = sorted([(c, r.build().durability) for c, r in res.items()], key=lambda x: x[1], reverse=True)

    combos2 = [combos[0]]

    # This should only run if no global effects ingredients with undesirable ids are used
    for c1, dura1 in combos[1:]:
        passes = True
        for c2, dura2 in combos2:
            if dura1 > dura2:
                continue
            if len(c1) > len(c2):
                continue

            n1 = negatives(c1)
            n2 = negatives(c2)
            p1 = positives(c1)
            p2 = positives(c2)
            if len(n1) > len(n2) or len(p1) > len(p2):
                continue

            n2 = n2[:len(n1)]
            p2 = p2[len(p2) - len(p1):]

            if (all(n1[i] >= n2[i] for i in range(len(n1)))
                    and all(p1[i] <= p2[i] for i in range(len(p1)))):
                passes = False
                break
        if passes:
            combos2.append((c1, dura1))

    combos = sorted([c[0] for c in combos2], key=lambda x: sum(x), reverse=True)
    print(len(combos))

    # print('\n'.join(map(str, combos)))
    to_csv({c: res[c] for c in combos})

    return res


def negatives(t: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(x for x in t if x < 0)


def positives(t: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(x for x in t if x >= 0)


def pad_r(t: tuple, n: int, val) -> tuple:
    return t + (val,) * (n - len(t))


def to_csv(combos: dict[tuple[int, ...], recipe.Recipe]):
    with open("combos.csv", "w", encoding='utf8') as f:
        f.write("Combo,,,,,,Durability,I1,I2,I3,I4,I5,I6\n")
        for k, v in combos.items():
            f.write(
                f"{','.join(pad_r(tuple(map(str, k)), 6, ''))},{(v.build().durability + 735000) // 1000},{','.join(map(str, v.ingredients))}\n")


def initializer():
    signal.signal(signal.SIGINT, lambda: None)


def _get_combos(
        first_ing,
        ingredients
) -> dict[tuple[int, ...], recipe.Recipe]:
    combos = {}

    for combination in bruteForce.generate_all_permutations(5, *ingredients, repeat=True):
        r = recipe.Recipe(first_ing, *combination)

        mods = r.calculate_modifiers()

        effs = []

        for i in range(6):
            if r.ingredients[i].name != "No Ingredient":
                continue

            effs.append(mods[i])

        effs = tuple(sorted(effs))

        if effs not in combos or r.build().durability > combos[effs].build().durability:
            combos[effs] = r

    return combos

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

    combos = sorted(res.keys(), key=lambda x: sum(x))

    return res


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

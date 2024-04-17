from multiprocessing import Pool

from core.optimizer import bruteForce
from . import ingredient, recipe


async def optimize(stat: str, min_dura: int, ingredients: list[ingredient.Ingredient]):
    with Pool(6) as p:
        results = p.starmap(_get_best_recipe, [(stat, min_dura, i, ingredients) for i in ingredients])

    best_r = results[0]
    for r in results:
        if r.build().identifications[stat].max > best_r.build().identifications[stat].max:
            best_r = r

    return best_r


def _get_best_recipe(stat: str, min_dura: int, first_ing, ingredients):
    best = ingredient.Ingredient("base", 0, 0, 0, {'stat': ingredient.Identification(0)}, ingredient.Modifier(),
                                 ingredient.Requirements(set()))
    best_r = None
    best.identifications[stat] = ingredient.Identification(0)

    for combination in bruteForce.generate_all_combinations(5, *ingredients):
        r = recipe.Recipe(first_ing, *combination)
        item = r.build()

        if not stat in item.identifications or item.durability < min_dura:
            continue

        if item.identifications[stat].max > best.identifications[stat].max:
            best = item
            best_r = r

    return best_r

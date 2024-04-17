from multiprocessing import Pool
from typing import Callable

from core.optimizer import bruteForce
from . import ingredient, recipe
from .ingredient import Ingredient


async def optimize(stat: str, constraints: Callable[[ingredient.Ingredient], bool], ingredients: list[ingredient.Ingredient]):
    with Pool(3) as p:
        results = p.starmap(_get_best_recipe, [(stat, constraints, i, ingredients) for i in ingredients])

    best_r = results[0]
    for r in results:
        if r.build().identifications[stat].max > best_r.build().identifications[stat].max:
            best_r = r

    return best_r


def _get_best_recipe(stat: str, constraints: Callable[[ingredient.Ingredient], bool], first_ing, ingredients):
    best = ingredient.Ingredient("base", 0, 0, 0, {'stat': ingredient.Identification(0)}, ingredient.Modifier(),
                                 ingredient.Requirements(set()))
    best_r = None
    best.identifications[stat] = ingredient.Identification(0)

    for combination in bruteForce.generate_all_combinations(5, *ingredients):
        r = recipe.Recipe(first_ing, *combination)
        item = r.build()

        if not constraints(item):
            continue

        if stat in item.identifications and item.identifications[stat].max > best.identifications[stat].max:
            best = item
            best_r = r

    return best_r

import bisect
from heapq import merge
from multiprocessing import Pool
from typing import Callable

from core.optimizer import bruteForce
from . import ingredient, recipe


async def optimize(
        constraint_func: Callable[[ingredient.Ingredient], bool],
        scoring_func: Callable[[ingredient.Ingredient], int],
        ingredients: list[ingredient.Ingredient],
        n: int = 10,
        pool_size: int = 4):
    """
    Optimizes the recipe for the given ingredients.
    :param constraint_func: The function to filter the recipes. True = keep.
    :param scoring_func: A scoring function to judge the recipes. Higher = better.
    :param ingredients: A list of ingredients test in the recipe.
    :param n: The number of recipes to return.
    :param pool_size: The number of processes to use.
    :return: List of up to n recipes sorted from best to worst.
    """
    with Pool(pool_size) as p:
        results = p.starmap(_get_best_recipes,
                            [(constraint_func, scoring_func, i, ingredients, n) for i in ingredients])

    return merge(*results, key=lambda x: -scoring_func(x.build()))[:n]


def _get_best_recipes(
        constraints: Callable[[ingredient.Ingredient], bool],
        scoring_func: Callable[[ingredient.Ingredient], bool],
        first_ing,
        ingredients,
        n: int):
    best_r = []

    for combination in bruteForce.generate_all_combinations(5, *ingredients):
        r = recipe.Recipe(first_ing, *combination)

        if not constraints(r.build()):
            continue

        bisect.insort(best_r, r, key=lambda x: -scoring_func(x.build()))
        best_r = best_r[:n]

    return best_r

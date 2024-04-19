import signal
from multiprocessing import Pool
from typing import Callable

from core.optimizer import bruteForce
from core.uniqueHeap import UniqueHeap
from . import ingredient, recipe


def optimize(
        constraint_func: Callable[[ingredient.Ingredient], bool],
        scoring_func: Callable[[ingredient.Ingredient], int],
        ingredients: list[ingredient.Ingredient],
        n: int = 10,
        pool_size: int = 4) -> list[recipe.Recipe]:
    """
    Optimizes the recipe for the given ingredients.
    :param constraint_func: The function to filter the recipes. True = keep.
    :param scoring_func: A scoring function to judge the recipes. Higher = better.
    :param ingredients: A list of ingredients test in the recipe.
    :param n: The number of recipes to return.
    :param pool_size: The number of processes to use.
    :return: List of up to n recipes sorted from best to worst.
    """
    with Pool(pool_size, initializer=initializer) as p:
        try:
            results = p.starmap(_get_best_recipes,
                                [(constraint_func, scoring_func, i, ingredients, n) for i in ingredients])
        except KeyboardInterrupt:
            p.terminate()
            raise KeyboardInterrupt

    heap = UniqueHeap(sum(results, []), key=lambda x: scoring_func(x.build()), max_size=n)
    return [item for _, item in heap.elements][::-1]


def initializer():
    signal.signal(signal.SIGINT, lambda: None)


def _get_best_recipes(
        constraints: Callable[[ingredient.Ingredient], bool],
        scoring_func: Callable[[ingredient.Ingredient], bool],
        first_ing,
        ingredients,
        n: int) -> list[recipe.Recipe]:
    best_r = UniqueHeap(key=lambda x: scoring_func(x.build()), max_size=n)

    for combination in bruteForce.generate_all_permutations(5, *ingredients, repeat=True):
        r = recipe.Recipe(first_ing, *combination)

        if not constraints(r.build()):
            continue

        best_r.put(r)

    return [item for _, item in best_r.elements][::-1]


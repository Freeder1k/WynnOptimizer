import signal
import traceback
from multiprocessing import Pool
from typing import Callable

from core.optimizer import bruteForce
from core.uniqueHeap import UniqueHeap
from . import ingredient, recipe


def optimize(
        constraint_func: Callable[[ingredient.Ingredient], bool],
        scoring_func: Callable[[ingredient.Ingredient], int],
        ingredients: list[ingredient.Ingredient],
        combos: dict[tuple[int, ...], recipe.Recipe] = None,
        n: int = 10,
        pool_size: int = 4) -> list[recipe.Recipe]:
    """
    Optimizes the recipe for the given ingredients.
    :param constraint_func: The function to filter the recipes. True = keep.
    :param scoring_func: A scoring function to judge the recipes. Higher = better.
    :param ingredients: A list of ingredients test in the recipe.
    :param combos: A dictionary of effectiveness combos.
    :param n: The number of recipes to return.
    :param pool_size: The number of processes to use.
    :return: List of up to n recipes sorted from best to worst.
    """
    if combos is None:
        combos = {(100,) * 6: recipe.Recipe(*((ingredient.NO_INGREDIENT,) * 6))}

    with Pool(pool_size, initializer=initializer) as p:
        try:
            results = p.starmap(_get_best_recipes,
                                [(constraint_func, scoring_func, i, ingredients, combos, n) for i in ingredients])
        except KeyboardInterrupt:
            p.terminate()
            raise KeyboardInterrupt

    heap = UniqueHeap(sum(results, []), key=lambda x: scoring_func(x.build()), max_size=n)
    return [item for _, item in heap.elements][::-1]


def initializer():
    signal.signal(signal.SIGINT, lambda: None)


def _replace_no_ing(r: recipe.Recipe, *ings):
    res = []
    ing_it = iter(ings)
    for i in range(6):
        if r.ingredients[i] == ingredient.NO_INGREDIENT:
            res.append(next(ing_it))
        else:
            res.append(r.ingredients[i])
    return res


def _get_best_recipes(
        constraints: Callable[[ingredient.Ingredient], bool],
        scoring_func: Callable[[ingredient.Ingredient], bool],
        first_ing,
        ingredients,
        combos,
        n: int) -> list[recipe.Recipe]:
    try:
        best_r = UniqueHeap(key=lambda x: scoring_func(x.build()), max_size=n)

        for combo, base_r in combos.items():
            if len(combo) <= 1:
                r = recipe.Recipe(*_replace_no_ing(base_r, first_ing))
                if not constraints(r.build()):
                    continue
                best_r.put(r)
            else:
                for ings in bruteForce.generate_all_permutations(len(combo) - 1, *ingredients, repeat=True):
                    r = recipe.Recipe(*_replace_no_ing(base_r, first_ing, *ings))
                    if not constraints(r.build()):
                        continue
                    best_r.put(r)

        return [item for _, item in best_r.elements][::-1]
    except Exception as e:
        print(e)
        print(traceback.format_exc())
        return []

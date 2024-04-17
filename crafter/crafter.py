from core.optimizer import bruteForce
from . import ingredient, recipe


async def optimize(stat: str, min_dura: int, ingredients: list[ingredient.Ingredient]):
    best = ingredient.NO_INGREDIENT
    best_r = None
    best.identifications[stat] = ingredient.Identification(0)  # uhh yeah... ig it works

    for combination in bruteForce.generate_all_combinations(6, *ingredients):
        r = recipe.Recipe(*combination)
        item = r.build()

        if item.identifications[stat].max > best.identifications[stat].max and item.durability >= min_dura:
            best = item
            best_r = r

    return best_r

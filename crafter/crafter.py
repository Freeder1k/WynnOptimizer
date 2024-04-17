from async_lru import alru_cache

from core.wynnAPI import item
from .ingredient import Ingredient


@alru_cache(ttl=3600)
async def get_ingredients():
    items = await item.database()

    return {k: Ingredient.from_api_json(k, v) for k, v in items.items()
            if 'itemOnlyIDs' in v or 'consumableOnlyIDs' in v}


def clean_data(ingredient: dict):
    ingredient.pop('skin', None)
    ingredient.pop('material', None)
    ingredient.pop('tier', None)
    ingredient.pop('internalName', None)
    ingredient.pop('droppedBy', None)
    return ingredient


async def get_ingredient(name: str):
    ingredients = await get_ingredients()
    return ingredients.get(name, None)

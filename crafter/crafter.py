from core.wynnAPI import item


async def get_ingredients():
    items = await item.database()

    return {k: clean_data(v) for k, v in items.items() if 'itemOnlyIDs' in v or 'consumableOnlyIDs' in v}


def clean_data(ingredient: dict):
    ingredient.pop('skin', None)
    ingredient.pop('material', None)
    ingredient.pop('tier', None)
    ingredient.pop('internalName', None)
    ingredient.pop('droppedBy', None)
    return ingredient



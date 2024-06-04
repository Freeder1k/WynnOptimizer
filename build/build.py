# import craft.ingredient
# from utils.integer import Base64
from .item import Item, NO_ITEM, IdentificationList


class Build:
    def __init__(self, i1: Item, i2: Item, i3: Item, i4: Item, i5: Item, i6: Item, i7: Item, i8: Item):
        """
        Wynncraft build class.
        """
        self.items = (i1, i2, i3, i4, i5, i6, i7, i8)
        self._item = None

    def build(self) -> Item:
        """
        Build from the items.
        :return: A new Item object representing the build.
        """
        if self._item is not None:
            return self._item

        name = "build"  # TODO: Come up with naming scheme

        # calculate the build stats
        result = NO_ITEM
        for i in range(8):
            result = result + (self.items[i])

        self._item = Item(name, "build", result.identifications, result.requirements)

        return self._item


    # Havent done this yet
    '''
    def b64_hash(self):
        return "".join([Base64.fromInt(craft.ingredient.get_ing_id(i.name)).rjust(2, "0") for i in self.ingredients])

    @classmethod
    def from_ingredient_strings(cls, i1: str, i2: str, i3: str, i4: str, i5: str, i6: str):
        return cls(*(craft.ingredient.get_ingredient(ing) for ing in (i1, i2, i3, i4, i5, i6)))

    def __str__(self):
        return f"Recipe({', '.join(str(i) for i in self.ingredients)})"

    def __repr__(self):
        return self.__str__()'''

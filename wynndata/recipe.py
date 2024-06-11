from . import ingredient
from .ingredient import Ingredient, Modifier, NO_INGREDIENT
from .item import Crafted, Base


class ModifierMatrix:
    def __init__(self):
        self.matrix = [
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 100, 100, 0],
            [0, 100, 100, 0],
            [0, 100, 100, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0]
        ]

    def flatten(self):
        return [self.matrix[i][j] for i in range(2, 5) for j in range(1, 3)]

    def apply_modifier(self, modifier: Modifier, flat_pos: int):
        x, y = flat_pos % 2 + 1, flat_pos // 2 % 3 + 2

        for i in range(2, 5):
            for j in range(1, 3):
                self.matrix[i][j] += modifier.notTouching

        self.matrix[y][x - 1] += modifier.left + modifier.touching - modifier.notTouching

        self.matrix[y][x + 1] += modifier.right + modifier.touching - modifier.notTouching

        self.matrix[y - 1][x] += modifier.above + modifier.touching - modifier.notTouching
        self.matrix[y - 2][x] += modifier.above

        self.matrix[y + 1][x] += modifier.under + modifier.touching - modifier.notTouching
        self.matrix[y + 2][x] += modifier.under

        self.matrix[y][x] -= modifier.notTouching


class Recipe:
    def __init__(self, i1: Ingredient, i2: Ingredient, i3: Ingredient, i4: Ingredient, i5: Ingredient, i6: Ingredient):
        """
        Wynncraft crafted item recipe class.
        Format:
        i1 i2
        i3 i4
        i5 i6
        """
        self.ingredients = (i1, i2, i3, i4, i5, i6)
        self._item = None

    def calculate_modifiers(self):
        """
        Calculate the modifier matrix of the recipe.
        """
        m = ModifierMatrix()

        for i in range(6):
            m.apply_modifier(self.ingredients[i].modifiers, i)

        return m.flatten()

    def build(self) -> Ingredient:
        """
        Build the item from the recipe.
        :return: A new Ingredient object representing the crafted item.
        """
        if self._item is not None:
            return self._item

        # calculate the recipe stats
        modifier_vector = self.calculate_modifiers()
        result = NO_INGREDIENT
        for i in range(6):
            result = result + (self.ingredients[i] * (modifier_vector[i] / 100))

        self._item = result

        return self._item

    @property
    def id(self):
        return sum(self.ingredients[i].id << (i * 12) for i in range(6))

    @classmethod
    def from_ingredient_strings(cls, i1: str, i2: str, i3: str, i4: str, i5: str, i6: str):
        return cls(*(ingredient.get_ingredient(ing) for ing in (i1, i2, i3, i4, i5, i6)))

    def __str__(self):
        return f"Recipe({', '.join(str(i) for i in self.ingredients)})"

    def __repr__(self):
        return self.__str__()

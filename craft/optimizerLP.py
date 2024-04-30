from typing import Callable, TypeVar

import numpy as np

from core.optimizer.linearProgramming import BinaryLinearProgramm
from craft import ingredient
from craft.ingredient import IdentificationType
from utils.decorators import single_use

T = TypeVar('T')


class LPRecipeOptimizer(BinaryLinearProgramm):
    def __init__(self, ingredients: list[ingredient.Ingredient],
                 score_function: Callable[[ingredient.Ingredient], float],
                 modifiers: tuple[int] = (100, 100, 100, 100, 100, 100)):
        """
        Create a linear programming optimizer for a recipe.
        :param ingredients: A list of ingredients to use in the recipe.
        :param score_function: A function that returns the score of an individual ingredient.
        :param modifiers: The modifier values of the recipe.
        """
        self._ingredients = ingredients
        self._modifiers = modifiers
        self._ingr_count = len(ingredients)
        self._mod_count = len(modifiers)
        self._ingrs_weighted = [ingr * m for m in modifiers for ingr in ingredients]
        self._score = score_function

        A_eq = np.zeros((self._mod_count, self._ingr_count * self._mod_count), dtype=int)
        for i in range(self._mod_count):
            A_eq[i][i * self._ingr_count: (i + 1) * self._ingr_count] = 1
        super().__init__(
            c=[-self._score(ingr) for ingr in self._ingrs_weighted],
            A_ub=[],
            b_ub=[],
            A_eq=A_eq,
            b_eq=[1] * self._mod_count
        )

    def find_best(self):
        """
        Find the recipe where the sum of the scores of the ingredients in that recipe is maximized and the constraints
        are satisfied.
        :return: The score of the best recipe and the ingredients in that recipe.
        """
        res = super().solve()
        if not res.success:
            return 0, []
        res_score = -res.fun
        res_ingrs = [self._ingredients[i % self._ingr_count] for i, x in enumerate(res.x) if x >= 0.999]
        return res_score, res_ingrs

    def add_max_constraint(self, value: T, ingr_lambda: Callable[[ingredient.Ingredient], T]):
        """
        Add a constraint that sum(ingr_lambda(i)) ≤ value for the weighted ingredients in the recipe.
        """
        if value is not None:
            self.A_ub.append([ingr_lambda(ingr) for ingr in self._ingrs_weighted])
            self.b_ub.append(value)

    def add_min_constraint(self, value: T, ingr_lambda: Callable[[ingredient.Ingredient], T]):
        """
        Add a constraint that sum(ingr_lambda(i)) ≥ value for the weighted ingredients in the recipe.
        """
        self.add_max_constraint(-value, lambda i: -ingr_lambda(i))

    @single_use
    def set_min_charges(self, value: int):
        self.add_min_constraint(value - 3, lambda i: i.charges)

    @single_use
    def set_min_duration(self, value: int):
        self.add_min_constraint(value - 1344, lambda i: i.duration)

    @single_use
    def set_min_durability(self, value: int):
        self.add_min_constraint(value - 735, lambda i: i.durability // 1000)

    @single_use
    def set_max_durability(self, value: int):
        self.add_max_constraint(value - 735, lambda i: i.durability // 1000)

    @single_use
    def set_max_str_req(self, value: int):
        self.add_max_constraint(value, lambda i: i.requirements.strength)

    @single_use
    def set_max_dex_req(self, value: int):
        self.add_max_constraint(value, lambda i: i.requirements.dexterity)

    @single_use
    def set_max_int_req(self, value: int):
        self.add_max_constraint(value, lambda i: i.requirements.intelligence)

    @single_use
    def set_max_def_req(self, value: int):
        self.add_max_constraint(value, lambda i: i.requirements.defence)

    @single_use
    def set_max_agi_req(self, value: int):
        self.add_max_constraint(value, lambda i: i.requirements.agility)

    @single_use
    def set_max_total_sp_req(self, value: int):
        self.add_max_constraint(value, lambda i: i.requirements.total_sp)

    @single_use
    def set_identification_max(self, identification: IdentificationType, value: int):
        self.add_max_constraint(value, lambda i: i.identifications[identification].max)

    @single_use
    def set_identification_min(self, identification: IdentificationType, value: int):
        self.add_min_constraint(value, lambda i: i.identifications[identification].max)

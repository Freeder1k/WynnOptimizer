from typing import Callable, TypeVar

from ortools.sat.python import cp_model
from ortools.sat.python.cp_model import LinearExpr, BoundedLinearExpression

from craft.CPRecipe import CPRecipe, LinearExprGenerator
from wynndata import ingredient

T = TypeVar('T')
SLOTS = (0, 1, 2, 3, 4, 5)


class CPRecipeOptimizer:
    def __init__(self, ingredients: list[ingredient.Ingredient],
                 score_function: Callable[[CPRecipe], LinearExpr]):
        """
        Create a linear programming optimizer for a recipe.
        :param ingredients: A list of ingredients to use in the recipe.
        :param score_function: A function that returns the score of an individual ingredient.
        :param modifiers: The modifier values of the recipe.
        """
        self.recipe = CPRecipe(_RecipeLinExprGenerator(self))
        self.model = cp_model.CpModel()

        self.ingredients = ingredients
        self.ingr_count = len(ingredients)
        self._values_count = 0

        # Define ingredient variables for each slot
        self._ingredient_variables = [[self.model.new_bool_var(f"{ingr.name}_{i}") for ingr in ingredients]
                                      for i in SLOTS]
        for i in SLOTS:
            self.model.add_exactly_one(self._ingredient_variables[i])

        # Define modifier variables
        self._mods = self._calc_mods()
        self._mod_variables = [[self.model.new_int_var(-1000, 1000, f"{ingr.name}_mod_{i}") for ingr in ingredients]
                               for i in SLOTS]
        for i in SLOTS:
            for j in range(self.ingr_count):
                self.model.add(self._mod_variables[i][j] == self._mods[i]).only_enforce_if(self._ingredient_variables[i][j])
                self.model.add(self._mod_variables[i][j] == 0).only_enforce_if(self._ingredient_variables[i][j].negated())

        # Define objective
        self._objective = score_function(self.recipe)

        self.model.maximize(self._objective)

        # requirements
        # self.model.add(sum(self.effective_values(lambda i: i.requirements.intelligence)) <= 60 * 100)
        # self.model.add(sum(self.effective_values(lambda i: i.identifications.rawIntelligence.max)) >= 0)
        # self.model.add(sum(self.effective_values(lambda i: i.identifications.rawHealth.max)) >= 0)
        # self.model.add(sum(self.effective_values(lambda i: i.identifications.manaRegen.max)) >= 10 * 100)
        # self.model.add(sum(self.effective_values(lambda i: i.requirements.strength)) <= 10 * 100)
        # self.model.add(sum(self.effective_values(lambda i: i.requirements.dexterity)) <= 90 * 100)
        # self.model.add(sum(self.effective_values(lambda i: i.requirements.intelligence)) <= 120 * 100)
        # self.model.add(sum(self.effective_values(lambda i: i.requirements.defence)) <= 0 * 100)
        # self.model.add(sum(self.effective_values(lambda i: i.requirements.agility)) <= 0 * 100)
        # self.model.add(sum(self.effective_values(lambda i: i.requirements.intelligence)) <= 60)
        # self.model.add(sum(sum(self.ingredients[j].durability * self._ingredient_variables[i][j]
        #                        for j in range(self.ingr_count))
        #                    for i in range(6)) > (-735 + 20) * 1000)
        # self.model.add(sum(sum(self.ingredients[j].duration * self.ingredient_variables[i][j]
        #                        for j in range(self.ingr_count))
        #                    for i in range(6)) > -3800)

    def raw_values(self, value_func: Callable[[ingredient.Ingredient], int]):
        """
        Return lin exprs corresponding to the value of each slot (unmodified).
        """
        return [sum(value_func(self.ingredients[j]) * self._ingredient_variables[i][j] for j in range(self.ingr_count))
                for i in SLOTS]

    def effective_values(self, value_func: Callable[[ingredient.Ingredient], int], name: str = None):
        """
        Return variables corresponding to the value of each slot (rounded down by 100).
        """
        return [sum(value_func(self.ingredients[j]) * self._mod_variables[i][j] for j in range(self.ingr_count))
                for i in SLOTS]
        # if name is None:
        #     name = self._values_count
        #     self._values_count += 1
        #
        # vars = [self.model.new_int_var_from_domain(cp_model.Domain.all_values(), f"val_{i}_{name}")
        #         for i in SLOTS]
        # mod_vars = [self.model.new_int_var_from_domain(cp_model.Domain.all_values(), f"val_{i}_{name}_mod")
        #             for i in SLOTS]
        #
        # base_vals = [sum(value_func(self.ingredients[j]) * self._mod_variables[i][j] for j in range(self.ingr_count))
        #         for i in SLOTS]
        #
        # for i in SLOTS:
        #     self.model.add_modulo_equality(mod_vars[i], base_vals[i], 100)
        #     self.model.add(vars[i] == base_vals[i] - mod_vars[i])
        #
        # return vars

    def _calc_mods(self):
        mod_left = [sum(self.ingredients[j].modifiers.left * self._ingredient_variables[i][j]
                        for j in range(self.ingr_count) if self.ingredients[j].modifiers.left != 0)
                    for i in range(6)]
        mod_right = [sum(self.ingredients[j].modifiers.right * self._ingredient_variables[i][j]
                         for j in range(self.ingr_count) if self.ingredients[j].modifiers.right != 0)
                     for i in range(6)]
        mod_above = [sum(self.ingredients[j].modifiers.above * self._ingredient_variables[i][j]
                         for j in range(self.ingr_count) if self.ingredients[j].modifiers.above != 0)
                     for i in range(6)]
        mod_under = [sum(self.ingredients[j].modifiers.under * self._ingredient_variables[i][j]
                         for j in range(self.ingr_count) if self.ingredients[j].modifiers.under != 0)
                     for i in range(6)]
        mod_touch = [sum(self.ingredients[j].modifiers.touching * self._ingredient_variables[i][j]
                         for j in range(self.ingr_count) if self.ingredients[j].modifiers.touching != 0)
                     for i in range(6)]
        mod_not_touch = [sum(self.ingredients[j].modifiers.notTouching * self._ingredient_variables[i][j]
                             for j in range(self.ingr_count) if self.ingredients[j].modifiers.notTouching != 0)
                         for i in range(6)]

        mod_arr = []
        mod_arr.append(100
                       + mod_left[1] + mod_touch[1]
                       + mod_above[2] + mod_touch[2]
                       + mod_not_touch[3]
                       + mod_above[4] + mod_not_touch[4]
                       + mod_not_touch[5])
        mod_arr.append(100
                       + mod_right[0] + mod_touch[0]
                       + mod_not_touch[2]
                       + mod_above[3] + mod_touch[3]
                       + mod_not_touch[4]
                       + mod_above[5] + mod_not_touch[5])
        mod_arr.append(100
                       + mod_under[0] + mod_touch[0]
                       + mod_not_touch[1]
                       + mod_left[3] + mod_touch[3]
                       + mod_above[4] + mod_touch[4]
                       + mod_not_touch[5])
        mod_arr.append(100
                       + mod_not_touch[0]
                       + mod_under[1] + mod_touch[1]
                       + mod_right[2] + mod_touch[2]
                       + mod_not_touch[4]
                       + mod_above[5] + mod_touch[5])
        mod_arr.append(100
                       + mod_under[0] + mod_not_touch[0]
                       + mod_not_touch[1]
                       + mod_under[2] + mod_touch[2]
                       + mod_not_touch[3]
                       + mod_left[5] + mod_touch[5])
        mod_arr.append(100
                       + mod_not_touch[0]
                       + mod_under[1] + mod_not_touch[1]
                       + mod_not_touch[2]
                       + mod_under[3] + mod_touch[3]
                       + mod_right[4] + mod_touch[4])

        return mod_arr

    def find_best(self):
        """
        Find the recipe where the sum of the scores of the ingredients in that recipe is maximized and the constraints
        are satisfied.
        :return: The score of the best recipe and the ingredients in that recipe.
        """
        solver = cp_model.CpSolver()
        printer = SolutionPrinter(self)
        status = solver.solve(self.model, printer)

        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            return solver.ObjectiveValue(), [self.ingredients[j] for i in range(6) for j in range(self.ingr_count) if
                                             solver.Value(self._ingredient_variables[i][j])]
        else:
            return 0, []

    def add(self, constraint: BoundedLinearExpression):
        self.model.add(constraint)


class SolutionPrinter(cp_model.CpSolverSolutionCallback):
    """Print intermediate solutions."""

    def __init__(self, optimizer: CPRecipeOptimizer):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.optimizer = optimizer
        self.count = 0

    def on_solution_callback(self) -> None:
        self.count += 1
        ingredients = [self.optimizer.ingredients[j] for i in range(6) for j in range(self.optimizer.ingr_count) if
                       self.Value(self.optimizer._ingredient_variables[i][j])]
        print(
            f"Solution {self.count}, time = {self.WallTime()} s, objective = {self.ObjectiveValue()}, ingredients = {ingredients}")


class _RecipeLinExprGenerator(LinearExprGenerator):
    def __init__(self, model):
        self.model = model

    def generate(self, value_func: Callable[[ingredient.Ingredient], int], raw: bool = False) -> LinearExpr:
        if not raw:
            return sum(self.model.effective_values(value_func))
        else:
            return sum(self.model.raw_values(value_func))

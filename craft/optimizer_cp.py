from typing import Callable, TypeVar

from ortools.sat.python import cp_model
from ortools.sat.python.cp_model import LinearExpr, BoundedLinearExpression

from cp_utils.linear_expr_factory import LinearExprFactory
from craft.cp_recipe import CPRecipe
from utils.integer import Base64
from wynndata import ingredient
from wynndata.recipe import Recipe

T = TypeVar('T')
SLOTS = (0, 1, 2, 3, 4, 5)


class CPRecipeOptimizer:
    def __init__(self, ingredients: list[ingredient.Ingredient], profession: str):
        """
        Create a linear programming optimizer for a recipe.
        :param ingredients: A list of ingredients to use in the recipe.
        :param score_function: A function that returns the score of an individual ingredient.
        :param modifiers: The modifier values of the recipe.
        """
        self.recipe = CPRecipe(_BaseLinExprFactory(self), _IdentificationsLinExprFactory(self),
                               _RequirementsLinExprFactory(self), profession)
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
                self.model.add(self._mod_variables[i][j] == self._mods[i]).only_enforce_if(
                    self._ingredient_variables[i][j])
                self.model.add(self._mod_variables[i][j] == 0).only_enforce_if(
                    self._ingredient_variables[i][j].negated())

        self._objective = None

    def raw_values(self, value_func: Callable[[ingredient.Ingredient], int]):
        """
        Return lin exprs corresponding to the value of each slot (unmodified).
        """
        return [sum(value_func(self.ingredients[j]) * self._ingredient_variables[i][j] for j in range(self.ingr_count))
                for i in SLOTS]

    def effective_values(self, value_func: Callable[[ingredient.Ingredient], int], name: str = None,
                         round_up: bool = False):
        """
        Add and return variables corresponding to the modified value of each slot.
        Each call to this function adds 12 new variables, 24 new linear constraints and 6 new division constraints.
        """
        if name is None:
            name = self._values_count
            self._values_count += 1

        if all(value_func(ingr) == 0 for ingr in self.ingredients):
            slot_vars = [self.model.new_constant(0) for _ in SLOTS]
            return slot_vars

        values = [value_func(ingr) for ingr in self.ingredients]
        max_val = abs(max(values, key=abs))

        base_vals = [sum(values[j] * self._mod_variables[i][j] for j in range(self.ingr_count)) for i in SLOTS]
        base_vars = [self.model.new_int_var(-max_val * 1000, max_val * 1000, f"val_{i}_{name}_base") for i in SLOTS]

        slot_vars = [self.model.new_int_var(-max_val * 10, max_val * 10, f"val_{i}_{name}") for i in SLOTS]

        for i in SLOTS:
            is_neg_var = self.model.new_bool_var(f"val_{i}_{name}_is_neg")
            self.model.add(base_vars[i] < 0).only_enforce_if(is_neg_var)
            self.model.add(base_vars[i] >= 0).only_enforce_if(is_neg_var.Not())

            # round up/down
            if round_up:
                self.model.add(base_vars[i] == base_vals[i]).only_enforce_if(is_neg_var)
                self.model.add(base_vars[i] == base_vals[i] + 99).only_enforce_if(is_neg_var.Not())
            else:
                self.model.add(base_vars[i] == base_vals[i]).only_enforce_if(is_neg_var.Not())
                self.model.add(base_vars[i] == base_vals[i] - 99).only_enforce_if(is_neg_var)

            self.model.AddDivisionEquality(slot_vars[i], base_vars[i], 100)

        return slot_vars

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
        mod_not_touch = [sum(self.ingredients[j].modifiers.not_touching * self._ingredient_variables[i][j]
                             for j in range(self.ingr_count) if self.ingredients[j].modifiers.not_touching != 0)
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

    def set_objective(self, objective: LinearExpr):
        """
        Set the objective of the model.
        """
        self._objective = objective

    def find_best(self):
        """
        Find the recipe where the sum of the scores of the ingredients in that recipe is maximized and the constraints
        are satisfied.
        :return: The score of the best recipe and the ingredients in that recipe.
        """
        if self._objective is None:
            raise ValueError("Objective not set")

        self.model.maximize(self._objective)
        solver = cp_model.CpSolver()
        solver.parameters.num_workers = 6
        printer = SolutionPrinter(self)
        status = solver.solve(self.model, printer)

        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            return solver.ObjectiveValue(), [self.ingredients[j] for i in range(6) for j in range(self.ingr_count) if
                                             solver.Value(self._ingredient_variables[i][j])]
        else:
            print(self.model.validate())
            print(f"Status = {solver.StatusName(status)}")
            return 0, []

    def add(self, constraint: BoundedLinearExpression):
        """
        Add a constraint to the model.
        """
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

        recipe = Recipe(*ingredients)
        print(f"https://hppeng-wynn.github.io/crafter/#1{Base64.fromInt(recipe.id, order=12)}9i91")


class _IdentificationsLinExprFactory(LinearExprFactory):
    def __init__(self, model):
        self.model = model

    def generate(self, value_func: Callable[[ingredient.Ingredient], int], lb=None, ub=None, name=None) -> LinearExpr:
        return sum(self.model.effective_values(value_func, name=name))


class _RequirementsLinExprFactory(LinearExprFactory):
    def __init__(self, model):
        self.model = model

    def generate(self, value_func: Callable[[ingredient.Ingredient], int], lb=None, ub=None, name=None) -> LinearExpr:
        return sum(self.model.effective_values(value_func, name=name, round_up=True))


class _BaseLinExprFactory(LinearExprFactory):
    def __init__(self, model):
        self.model = model

    def generate(self, value_func: Callable[[ingredient.Ingredient], int], lb=None, ub=None, name=None) -> LinearExpr:
        return sum(self.model.raw_values(value_func))

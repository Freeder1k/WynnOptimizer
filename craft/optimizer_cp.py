from typing import Callable, TypeVar

from ortools.sat.python import cp_model
from ortools.sat.python.cp_model import LinearExpr, BoundedLinearExpression

from cp_utils.linear_expr_factory import LinearExprFactory
from craft.cp_recipe import CPRecipe
from utils import gridUtils
from utils.integer import Base64
from wynndata import ingredient
from wynndata.recipe import Recipe

T = TypeVar('T')
SLOTS = (0, 1, 2, 3, 4, 5)


class CPRecipeOptimizer:
    def __init__(self, ingredients: list[ingredient.Ingredient], profession: str):
        """
        Create a constraint programming optimizer for a recipe.
        :param ingredients: A list of ingredients to use in the recipe.
        :param profession: The profession of the recipe.
        """
        self.recipe = CPRecipe(_BaseLinExprFactory(self), _IdentificationsLinExprFactory(self),
                               _RequirementsLinExprFactory(self), profession)
        self.model = cp_model.CpModel()

        self.ingredients = ingredients
        self.ingr_count = len(ingredients)

        # Ingredient in each slot is represented by its index.
        self._ingredient_vars = [self.model.new_int_var(0, self.ingr_count - 1, f"slot_{i}_ingredient") for i in SLOTS]

        # Define modifier variables
        self._mod_vars = self._define_mods()

        self._objective = None
        self._solver = None

    def base_values(self, value_func: Callable[[ingredient.Ingredient], int], name: str = None):
        """
        Return variables corresponding to the base value of each slot (unmodified).
        """
        all_base_values = [value_func(ingr) for ingr in self.ingredients]
        max_val = abs(max(all_base_values, key=abs))
        base_vars = [self.model.new_int_var(-max_val, max_val, f"slot_{i}_{name}_base") for i in SLOTS]

        for i in SLOTS:
            self.model.add_element(self._ingredient_vars[i], all_base_values, base_vars[i])

        return base_vars

    def effective_values(self, value_func: Callable[[ingredient.Ingredient], int], name: str = None,
                         round_up: bool = False):
        """
        Add and return variables corresponding to the modified value of each slot.
        """
        max_val = max([abs(value_func(ingr)) for ingr in self.ingredients])

        if max_val == 0:
            value_vars = [self.model.new_constant(0) for _ in SLOTS]
            return value_vars

        base_vars = self.base_values(value_func, name=name)
        value_vars = [self.model.new_int_var(-max_val * 10, max_val * 10, f"slot_{i}_{name}_value") for i in SLOTS]

        for i in SLOTS:
            v_modified = self.model.NewIntVar(-max_val * 1000, max_val * 1000, f"slot_{i}_{name}_modified")
            self.model.add_multiplication_equality(v_modified, [base_vars[i], self._mod_vars[i]])  # x = base * modifier

            # Wynncraft rounds up/down to +/-infinity instead of 0.
            is_neg = self.model.new_bool_var(f"slot_{i}_{name}_is_neg")
            v_offset = self.model.new_int_var(-max_val * 1000, max_val * 1000, f"slot_{i}_{name}_modified_offset")
            self.model.add(v_modified < 0).only_enforce_if(is_neg)
            self.model.add(v_modified >= 0).only_enforce_if(is_neg.Not())
            if round_up:
                offset = is_neg.Not() * 99
            else:
                offset = is_neg * -99
            self.model.add(v_offset == v_modified + offset)  # y = x + offset

            self.model.add_division_equality(value_vars[i], v_offset, 100)  # y = x // 100

        return value_vars

    def _define_mods(self):
        lb, ub = -1000, 1000
        mods = []
        for i in SLOTS:
            mod = 100
            for j in SLOTS:
                if j == i:
                    continue
                if gridUtils.is_left(i, j):
                    v = self.model.new_int_var(lb, ub, f"mod_{i}_{j}_left")
                    self.model.add_element(self._ingredient_vars[j], [ingr.modifiers.left for ingr in self.ingredients],
                                           v)
                    mod += v
                if gridUtils.is_right(i, j):
                    v = self.model.new_int_var(lb, ub, f"mod_{i}_{j}_right")
                    self.model.add_element(self._ingredient_vars[j],
                                           [ingr.modifiers.right for ingr in self.ingredients], v)
                    mod += v
                if gridUtils.is_above(i, j):
                    v = self.model.new_int_var(lb, ub, f"mod_{i}_{j}_above")
                    self.model.add_element(self._ingredient_vars[j],
                                           [ingr.modifiers.above for ingr in self.ingredients], v)
                    mod += v
                if gridUtils.is_under(i, j):
                    v = self.model.new_int_var(lb, ub, f"mod_{i}_{j}_under")
                    self.model.add_element(self._ingredient_vars[j],
                                           [ingr.modifiers.under for ingr in self.ingredients], v)
                    mod += v
                if gridUtils.is_touching(i, j):
                    v = self.model.new_int_var(lb, ub, f"mod_{i}_{j}_touching")
                    self.model.add_element(self._ingredient_vars[j],
                                           [ingr.modifiers.touching for ingr in self.ingredients], v)
                    mod += v
                if gridUtils.is_not_touching(i, j):
                    v = self.model.new_int_var(lb, ub, f"mod_{i}_{j}_not_touching")
                    self.model.add_element(self._ingredient_vars[j],
                                           [ingr.modifiers.not_touching for ingr in self.ingredients], v)
                    mod += v

            mod_var = self.model.new_int_var(lb, ub, f"slot_{i}_mod")
            self.model.add(mod_var == mod)
            mods.append(mod_var)

        return mods

    def set_objective(self, objective: LinearExpr):
        """
        Set the objective of the model.
        """
        self._objective = objective

    def find_best(self, num_workers=1):
        """
        Find the recipe where the sum of the scores of the ingredients in that recipe is maximized and the constraints
        are satisfied.
        :return: The score of the best recipe and the ingredients in that recipe.
        """
        if self._objective is None:
            raise ValueError("Objective not set")

        self.model.maximize(self._objective)
        solver = cp_model.CpSolver()
        self._solver = solver
        solver.parameters.num_workers = num_workers
        printer = SolutionPrinter(self)
        status = solver.solve(self.model, printer)

        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            return solver.ObjectiveValue(), [self.ingredients[solver.Value(self._ingredient_vars[i])] for i in range(6)]
        else:
            print(self.model.validate())
            print(f"Status = {solver.StatusName(status)}")
            return 0, []

    def add(self, constraint: BoundedLinearExpression):
        """
        Add a constraint to the model.
        """
        self.model.add(constraint)

    def get(self, var: LinearExpr):
        """
        Get the value of a variable in the current solution.
        """
        if self._solver is None:
            raise ValueError("Solver not initialized")
        return self._solver.Value(var)


class SolutionPrinter(cp_model.CpSolverSolutionCallback):
    """Print intermediate solutions."""

    def __init__(self, optimizer: CPRecipeOptimizer):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.optimizer = optimizer
        self.count = 0

    def on_solution_callback(self) -> None:
        self.count += 1
        ingredients = [self.optimizer.ingredients[self.Value(self.optimizer._ingredient_vars[i])] for i in SLOTS]
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
        return sum(self.model.base_values(value_func, name=name))

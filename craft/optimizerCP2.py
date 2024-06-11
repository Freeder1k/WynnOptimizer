from typing import Callable, TypeVar

from ortools.sat.python import cp_model
from ortools.sat.python.cp_model import LinearExpr, BoundedLinearExpression

from craft.CPIngredient import CPIngredient
from wynndata.recipe import Recipe
from wynndata import ingredient

T = TypeVar('T')


class CPRecipeOptimizer:
    def __init__(self, ingredients: list[ingredient.Ingredient],
                 score_function: Callable[[ingredient.Ingredient], int],
                 bases: list[tuple[tuple, Recipe]]):
        """
        Create a linear programming optimizer for a recipe.
        :param ingredients: A list of ingredients to use in the recipe.
        :param score_function: A function that returns the score of an individual ingredient.
        :param modifiers: The modifier values of the recipe.
        """
        self.model = cp_model.CpModel()

        # Define variables for the number of occurrences of each modifier
        self.mod_values = list(set(mod for mods, _ in bases for mod in mods))
        self.mod_amt = len(self.mod_values)

        self.mod_count_variables = [self.model.new_int_var(0, 6, f"mod_{mod}") for mod in self.mod_values]
        # allowed_assignments = []
        # for mods, _ in bases:
        #     allowed_assignments.append(tuple(mods.count(mod) for mod in self.mod_values))
        # self.model.add_allowed_assignments(self.mod_count_variables, allowed_assignments)

        # Define variables for the ingredients
        self.ingredients = ingredients
        self.ingr_count = len(ingredients)

        self.ingredient_variables = [[self.model.new_int_var(0, 6, f"{ingr.name}x{mod}") for ingr in ingredients]
                                     for mod in self.mod_values]

        # Bind the ingredient variables to the modifier count variables
        for i in range(self.mod_amt):
            self.model.add(self.mod_count_variables[i] == sum(self.ingredient_variables[i]))

        # Define base recipes
        self.base_variables = [self.model.new_bool_var(f"base_{i}") for i in range(len(bases))]
        self.model.add_exactly_one(self.base_variables)

        # mod_count_exprs = [sum(self.ingredient_variables[i]) for i in range(self.mod_amt)]
        for i in range(len(bases)):
            assignment = [bases[i][0].count(mod) for mod in self.mod_values]
            self.model.add_allowed_assignments(self.mod_count_variables, [assignment]).only_enforce_if(
                self.base_variables[i])


        # Ingredients with modifiers precalculated
        self.ingrs_mod = [[ingr * (mod / 100) for ingr in ingredients] for mod in self.mod_values]
        self.base_items = [base[1].build() for base in bases]

        # Set the objective
        self.item = CPIngredient(self)

        self.objective = (sum(score_function(self.ingrs_mod[i][j]) * self.ingredient_variables[i][j]
                             for i in range(self.mod_amt)
                             for j in range(self.ingr_count)
                              if score_function(self.ingrs_mod[i][j]) != 0)
                          + sum(score_function(self.base_items[i]) * self.base_variables[i]
                                for i in range(len(bases))
                                if score_function(self.base_items[i]) != 0)
                          )
        self.model.maximize(self.objective)


    def add(self, constraint: BoundedLinearExpression):
        self.model.add(constraint)

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
                                             solver.Value(self.ingredient_variables[i][j])]
        else:
            return 0, []


class SolutionPrinter(cp_model.CpSolverSolutionCallback):
    """Print intermediate solutions."""

    def __init__(self, optimizer: CPRecipeOptimizer):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.optimizer = optimizer
        self.count = 0

    def on_solution_callback(self) -> None:
        self.count += 1
        ingredients = [self.optimizer.ingredients[j] for i in range(6) for j in range(self.optimizer.ingr_count) if
                       self.Value(self.optimizer.ingredient_variables[i][j])]
        print(
            f"Solution {self.count}, time = {self.WallTime()} s, objective = {self.ObjectiveValue()}, ingredients = {ingredients}")

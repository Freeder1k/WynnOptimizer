from typing import Callable, TypeVar

from ortools.sat.python import cp_model

from wynndata import ingredient

T = TypeVar('T')


class CPRecipeOptimizer:
    def __init__(self, ingredients: list[ingredient.Ingredient],
                 score_function: Callable[[ingredient.Ingredient], int]):
        """
        Create a linear programming optimizer for a recipe.
        :param ingredients: A list of ingredients to use in the recipe.
        :param score_function: A function that returns the score of an individual ingredient.
        :param modifiers: The modifier values of the recipe.
        """
        self.model = cp_model.CpModel()

        self.ingredients = ingredients
        self.ingr_count = len(ingredients)

        # self.recipe_variables = [self.model.new_int_var(0, self.ingr_count, f"ingr_{i}") for i in range(6)]

        self.ingredient_variables = [[self.model.new_bool_var(f"{ingr.name}_{i}") for ingr in ingredients] for i in
                                     range(6)]
        for i in range(6):
            self.model.add_exactly_one(self.ingredient_variables[i])

        self.mods = self.calc_mods()
        self.mod_variables = [[self.model.new_int_var(-1000, 1000, f"{ingr.name}_mod_{i}") for ingr in ingredients] for
                              i in
                              range(6)]
        for i in range(6):
            for j in range(self.ingr_count):
                self.model.add(self.mod_variables[i][j] == self.mods[i]).only_enforce_if(
                    self.ingredient_variables[i][j])
                self.model.add(self.mod_variables[i][j] == 0).only_enforce_if(self.ingredient_variables[i][j].negated())

        self._objective = self.effective_values(score_function)

        self.model.maximize(sum(self._objective))

        # requirements
        # self.model.add(sum(self.effective_values(lambda i: i.requirements.intelligence)) <= 60 * 100)
        # self.model.add(sum(self.effective_values(lambda i: i.identifications.rawIntelligence.max)) >= 0)
        # self.model.add(sum(self.effective_values(lambda i: i.identifications.rawHealth.max)) >= 0)
        # self.model.add(sum(self.effective_values(lambda i: i.identifications.manaRegen.max)) >= 0)
        self.model.add(sum(self.effective_values(lambda i: i.requirements.strength)) <= 77 * 100)
        self.model.add(sum(self.effective_values(lambda i: i.requirements.defence)) <= 126 * 100)
        # self.model.add(sum(self.effective_values(lambda i: i.requirements.intelligence)) <= 10 * 100)
        # self.model.add(sum(self.effective_values(lambda i: i.requirements.intelligence)) <= 60)
        self.model.add(sum(sum(self.ingredients[j].durability * self.ingredient_variables[i][j]
                               for j in range(self.ingr_count))
                           for i in range(6)) > (-735 + 90) * 1000)
        # self.model.add(sum(sum(self.ingredients[j].duration * self.ingredient_variables[i][j]
        #                        for j in range(self.ingr_count))
        #                    for i in range(6)) > -3800)

    def effective_values(self, value_func: Callable[[ingredient.Ingredient], int]):
        return [sum(value_func(self.ingredients[j]) * self.mod_variables[i][j]
                    for j in range(self.ingr_count))
                for i in range(6)]

    def calc_mods(self):
        mod_left = [sum(self.ingredients[j].modifiers.left * self.ingredient_variables[i][j]
                        for j in range(self.ingr_count) if self.ingredients[j].modifiers.left != 0)
                    for i in range(6)]
        mod_right = [sum(self.ingredients[j].modifiers.right * self.ingredient_variables[i][j]
                         for j in range(self.ingr_count) if self.ingredients[j].modifiers.right != 0)
                     for i in range(6)]
        mod_above = [sum(self.ingredients[j].modifiers.above * self.ingredient_variables[i][j]
                         for j in range(self.ingr_count) if self.ingredients[j].modifiers.above != 0)
                     for i in range(6)]
        mod_under = [sum(self.ingredients[j].modifiers.under * self.ingredient_variables[i][j]
                         for j in range(self.ingr_count) if self.ingredients[j].modifiers.under != 0)
                     for i in range(6)]
        mod_touch = [sum(self.ingredients[j].modifiers.touching * self.ingredient_variables[i][j]
                         for j in range(self.ingr_count) if self.ingredients[j].modifiers.touching != 0)
                     for i in range(6)]
        mod_not_touch = [sum(self.ingredients[j].modifiers.notTouching * self.ingredient_variables[i][j]
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
                                             solver.Value(self.ingredient_variables[i][j])]
        else:
            return 0, []
    #
    # def add_max_constraint(self, value: T, ingr_lambda: Callable[[ingredient.Ingredient], T]):
    #     """
    #     Add a constraint that sum(ingr_lambda(i)) ≤ value for the weighted ingredients in the recipe.
    #     """
    #     if value is not None:
    #         self.A_ub.append([ingr_lambda(ingr) for ingr in self._ingrs_weighted])
    #         self.b_ub.append(value)
    #
    # def add_min_constraint(self, value: T, ingr_lambda: Callable[[ingredient.Ingredient], T]):
    #     """
    #     Add a constraint that sum(ingr_lambda(i)) ≥ value for the weighted ingredients in the recipe.
    #     """
    #     self.add_max_constraint(-value, lambda i: -ingr_lambda(i))
    #
    # @single_use
    # def set_min_charges(self, value: int):
    #     self.add_min_constraint(value - 3, lambda i: i.charges)
    #
    # @single_use
    # def set_min_duration(self, value: int):
    #     self.add_min_constraint(value - 1344, lambda i: i.duration)
    #
    # @single_use
    # def set_min_durability(self, value: int):
    #     self.add_min_constraint(value - 735, lambda i: i.durability // 1000)
    #
    # @single_use
    # def set_max_str_req(self, value: int):
    #     self.add_max_constraint(value, lambda i: i.requirements.strength)
    #
    # @single_use
    # def set_max_dex_req(self, value: int):
    #     self.add_max_constraint(value, lambda i: i.requirements.dexterity)
    #
    # @single_use
    # def set_max_int_req(self, value: int):
    #     self.add_max_constraint(value, lambda i: i.requirements.intelligence)
    #
    # @single_use
    # def set_max_def_req(self, value: int):
    #     self.add_max_constraint(value, lambda i: i.requirements.defence)
    #
    # @single_use
    # def set_max_agi_req(self, value: int):
    #     self.add_max_constraint(value, lambda i: i.requirements.agility)
    #
    # def add_max_sp_sum_req(self, value: int, strength=False, dexterity=False, intelligence=False, defence=False,
    #                        agility=False):
    #     def sp_sum(ingr: ingredient.Ingredient):
    #         val = 0
    #         if strength:
    #             val += ingr.requirements.strength
    #         if dexterity:
    #             val += ingr.requirements.dexterity
    #         if intelligence:
    #             val += ingr.requirements.intelligence
    #         if defence:
    #             val += ingr.requirements.defence
    #         if agility:
    #             val += ingr.requirements.agility
    #         return val
    #
    #     self.add_max_constraint(value, lambda i: sp_sum(i))

    # def set_identification_max(self, identification: IdentificationType, value: int):
    #     self.add_max_constraint(value, lambda i: i.identifications[identification].max)
    #
    # def set_identification_min(self, identification: IdentificationType, value: int):
    #     self.add_min_constraint(value, lambda i: i.identifications[identification].max)


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

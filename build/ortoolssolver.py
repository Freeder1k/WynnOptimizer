"""Solves a simple assignment problem."""
from ortools.sat.python import cp_model
from typing import Callable, TypeVar
import sys

import numpy as np

#from core.optimizer.linearProgramming import BinaryLinearProgramm
from build import item
#from build.item import IdentificationType, NO_ITEM
#from utils.decorators import single_use
from build import build

np.set_printoptions(threshold=sys.maxsize)
T = TypeVar('T')
types = ['helmet', 'chestplate', 'leggings', 'boots', 'ring', 'bracelet', 'necklace']
spinner = ['|', '/', '-', '\\']


class CPModelSolver():
    def __init__(self, items: list[item.Item],
                 score_function: Callable[[item.Item], float],
                 weapon: item.Item):
        """
        Create a linear programming optimizer for a Build.
        :param items: A list of ingredients to use in the Build.
        :param score_function: A function that returns the score of an individual ingredient.
        :weapon: The weapon used in the build.
        """
        self._items = []
        self._objective = []
        self._weapon = weapon
        self._preitems = []  # TODO: add these
        item_count = []

        self.model = cp_model.CpModel()
        self.x = {}

        for t in types:
            t_items = [it for it in items if t in it.type]
            if len(t_items) == 0:
                continue
            if t != 'ring':
                if len(t_items) == 1:
                    self._preitems = self._preitems + t_items
                else:
                    self._items.append(t_items)
                    for i in t_items:
                        self.x[t, i.name] = self.model.new_bool_var(f"x[{t},{i.name}]")
                        self._objective.append(round(score_function(i)) * self.x[t, i.name])
                    self.model.add_exactly_one(self.x[t, i.name] for i in t_items)
                    item_count.append(len(t_items))
            else:  # build has 2 rings
                if len(t_items) <= 2:
                    self._preitems = self._preitems + t_items
                else:
                    self._items.append(t_items)
                    for i in t_items:
                        self.x[t, i.name] = self.model.new_int_var(0,2,f"x[{t},{i.name}]")
                        self._objective.append(round(score_function(i)) * self.x[t, i.name])
                    self.model.add(sum([self.x[t, i.name] for i in t_items]) == 2)
                    item_count.append(len(t_items))
        print(item_count)

        self.model.add(sum(self._objective) > 7500)

    def find_best(self):
        """
        Find the build where the sum of the scores of the items in that build is maximized and the constraints
        are satisfied.
        :return: The score of the best build and the items in that build.
        """
        self.model.maximize(sum(self._objective))
        solver = cp_model.CpSolver()
        status = solver.solve(self.model)

        # Print solution.
        res_items = []
        res_score = 0
        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            res_score = solver.objective_value
            for t_items in self._items:
                for i in t_items:
                    val = solver.value(self.x[i.type, i.name])
                    if val == 1:
                        res_items.append(i)
                    if val == 2:
                        res_items.append(i)
                        res_items.append(i)

        return res_score, res_items

    def find_allbest(self):
        """
        Find the build where the sum of the scores of the items in that build is maximized and the constraints
        are satisfied.
        :return: The score of the best build and the items in that build.
        """
        solver = cp_model.CpSolver()
        solution_printer = VarArraySolutionPrinter(self.x, self._items, self._weapon)
        solver.parameters.enumerate_all_solutions = True
        status = solver.solve(self.model, solution_printer)


        print(f"Status = {solver.status_name(status)}")
        print(f"Number of solutions found: {solution_printer.solution_count}")

        return solution_printer.results


class VarArraySolutionPrinter(cp_model.CpSolverSolutionCallback):
    """Print intermediate solutions."""

    def __init__(self, x, items, weapon):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self._x = x
        self._items = items
        self.solution_count = 0
        self.results = []
        self._weapon = weapon

    def on_solution_callback(self) -> None:
        self.solution_count += 1
        res_items = []
        for t_items in self._items:
            for i in t_items:
                val = self.value(self._x[i.type, i.name])
                if val == 1:
                    res_items.append(i)
                if val == 2:
                    res_items.append(i)
                    res_items.append(i)

        b = build.Build(self._weapon, *res_items)
        reqsp, bonsp = b.calc_sp()
        if sum(reqsp) < 400:
            self.results.append(b)

        sys.stdout.write(f"\r{spinner[(self.solution_count//3)%4]}  Solving {len(self.results)}/{self.solution_count} valid builds!")
        sys.stdout.flush()

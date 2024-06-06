"""Solves a simple assignment problem."""
from ortools.sat.python import cp_model
from typing import Callable, TypeVar
import sys

import numpy as np

from core.optimizer.linearProgramming import IntegerLinearProgramm
from build import item
from build.item import IdentificationType, NO_ITEM
from utils.decorators import single_use
from build import build

np.set_printoptions(threshold=sys.maxsize)
T = TypeVar('T')
types = ['helmet', 'chestplate', 'leggings', 'boots', 'ring', 'bracelet', 'necklace']


class CPModelSolver:
    def __init__(self, items: list[item.Item],
                 score_function: Callable[[item.Item], float],
                 weapon: item.Item):
        """
        Create a linear programming optimizer for a Build.
        :param items: A list of items to use in the Build.
        :param score_function: A function that returns the score of an individual item.
        :param weapon: The weapon used in the build.
        """
        self._items = []
        self._objective = []
        self._weapon = weapon
        self._preitems = []  # TODO: add these
        item_count = []

        self.model = cp_model.CpModel()
        self.x = {}     # TODO this doesn't have to be a dictionary

        for item_type in types:
            t_items = [itm for itm in items if item_type in itm.type]
            if len(t_items) <= 1:
                self._preitems = self._preitems + t_items
                item_count.append(0)
                continue

            self._items.append(t_items)
            item_count.append(len(t_items))

            if item_type != 'ring':
                for itm in t_items:
                    self.x[item_type, itm.name] = self.model.new_bool_var(f"x[{item_type},{itm.name}]")
                    self._objective.append(score_function(itm) * self.x[item_type, itm.name])
                self.model.add_exactly_one(self.x[item_type, i.name] for i in t_items)
            else:  # build has 2 rings
                for itm in t_items:
                    self.x[item_type, itm.name] = self.model.new_int_var(0,2,f"x[{item_type},{itm.name}]")
                    self._objective.append(score_function(itm) * self.x[item_type, itm.name])
                self.model.add(sum([self.x[item_type, i.name] for i in t_items]) == 2)

        print(item_count)

        self.model.maximize(sum(self._objective))

    def find_best(self):
        """
        Find the build where the sum of the scores of the items in that build is maximized and the constraints
        are satisfied.
        :return: The score of the best build and the items in that build.
        """
        solver = cp_model.CpSolver()
        status = solver.solve(self.model)

        # Print solution.
        res_items = []
        res_score = 0
        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            res_score = solver.objective_value
            for t_items in self._items:
                for itm in t_items:
                    val = solver.value(self.x[itm.type, itm.name])
                    if val == 1:
                        res_items.append(itm)
                    if val == 2:
                        res_items.append(itm)
                        res_items.append(itm)

        return res_score, res_items

    def find_bestn(self, n: int):
        """
        Find the build where the sum of the scores of the items in that build is maximized and the constraints
        are satisfied.
        :return: The score of the best build and the items in that build.
        """
        solver = cp_model.CpSolver()
        solution_printer = VarArraySolutionPrinter(self.x, self._items)
        solver.parameters.enumerate_all_solutions = True
        status = solver.solve(self.model, solution_printer)
        # TODO find the best n solutions

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


class VarArraySolutionPrinter(cp_model.CpSolverSolutionCallback):
    """Print intermediate solutions."""

    def __init__(self, x, items):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self._x = x
        self._items = items
        self.__solution_count = 0

    def on_solution_callback(self) -> None:
        if self.__solution_count > 100:
            return
        self.__solution_count += 1
        print("solution")
        res_items = []
        for t_items in self._items:
            for i in t_items:
                val = self.value(self._x[i.type, i.name])
                if val == 1:
                    res_items.append(i)
                if val == 2:
                    res_items.append(i)
                    res_items.append(i)
        print(res_items)

    @property
    def solution_count(self) -> int:
        return self.__solution_count

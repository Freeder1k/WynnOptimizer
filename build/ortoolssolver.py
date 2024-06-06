"""Solves a simple assignment problem."""
import sys
from typing import Callable, TypeVar

import numpy as np
from ortools.sat.python import cp_model

from build import item
from build import build

np.set_printoptions(threshold=sys.maxsize)
T = TypeVar('T')
types = ['helmet', 'chestplate', 'leggings', 'boots', 'ring', 'bracelet', 'necklace']
spinner = ['|', '/', '-', '\\']


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
        self._weapon = weapon
        self._preitems = []  # TODO: add these
        item_count = []

        self.model = cp_model.CpModel()

        self._items = []
        self.item_variables = []

        for item_type in types:
            t_items = [itm for itm in items if item_type in itm.type]
            if len(t_items) <= 1:
                self._preitems = self._preitems + t_items
                item_count.append(0)
                continue

            self._items += t_items
            item_count.append(len(t_items))

            if item_type == 'ring':  # build has 2 rings
                t_vars = [self.model.new_int_var(0, 2, f"x[{item_type},{itm.name}]") for itm in t_items]
                self.model.add(sum(t_vars) == 2)
            else:
                t_vars = [self.model.new_bool_var(f"x[{item_type},{itm.name}]") for itm in t_items]
                self.model.add_exactly_one(t_vars)

            self.item_variables += t_vars

        self._objective = [score_function(itm) * x for itm, x in zip(self._items, self.item_variables)]
        self.model.maximize(sum(self._objective))

        # Satisfy skill point constraints
        sp_vars = [self.model.new_int_var(0, 100, f"sp_{name}") for name in ['str', 'dex', 'int', 'def', 'agi']]
        self.model.add(sum(sp_vars) <= 200)

        self._sp_bonuses = [[]*5]
        for itm, x in zip(self._items, self.item_variables):
            for sp_bonus, bonus_sp in zip(self._sp_bonuses, [itm.identifications.rawStrength, itm.identifications.rawDexterity,
                                                              itm.identifications.rawIntelligence, itm.identifications.rawDefence,
                                                              itm.identifications.rawAgility]):
                if bonus_sp.raw != 0:
                    sp_bonus.append(x * bonus_sp.raw)
        for itm, x in zip(self._items, self.item_variables):
            for sp_var, req_sp, sp_bonus in zip(sp_vars, [itm.requirements.strength, itm.requirements.dexterity,
                                            itm.requirements.intelligence, itm.requirements.defence,
                                            itm.requirements.agility]), self._sp_bonuses:
                if req_sp != 0:
                    self.model.add(sp_var >= req_sp - sum(sp_bonus)).only_enforce_if(x)

        print(item_count)

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
            for itm, x in zip(self._items, self.item_variables):
                if solver.value(x) == 1:
                    res_items.append(itm)
                elif solver.value(x) == 2:
                    res_items.append(itm)
                    res_items.append(itm)

        return res_score, res_items

    def find_allbest(self):
        """
        Find the build where the sum of the scores of the items in that build is maximized and the constraints
        are satisfied.
        :return: The score of the best build and the items in that build.
        """
        solver = cp_model.CpSolver()
        solution_printer = VarArraySolutionPrinter(self.item_variables, self._items, self._weapon)
        solver.parameters.enumerate_all_solutions = True

        try:
            status = solver.solve(self.model, solution_printer)
            print()
        except KeyboardInterrupt:
            print()
            print(f"Solver interrupted")


        print(f"Status = {solver.status_name(status)}")
        print(f"Number of solutions found: {solution_printer.solution_count}")

        return solution_printer.results


class VarArraySolutionPrinter(cp_model.CpSolverSolutionCallback):
    """Print intermediate solutions."""

    def __init__(self, variables, items, weapon):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self._variables = variables
        self._items = items
        self.solution_count = 0
        self.results = []
        self._weapon = weapon

    def on_solution_callback(self) -> None:
        self.solution_count += 1
        res_items = []
        for itm, x in zip(self._items, self._variables):
            if self.value(x) == 1:
                res_items.append(itm)
            if self.value(x) == 2:
                res_items.append(itm)
                res_items.append(itm)
        b = build.Build(self._weapon, *res_items)
        reqsp, bonsp = b.calc_sp()
        if sum(reqsp) < 400:
            self.results.append(b)

        sys.stdout.write(f"\r{spinner[(self.solution_count//3)%4]}  Solving {len(self.results)}/{self.solution_count} valid builds!")
        sys.stdout.flush()

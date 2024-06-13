"""Solves a simple assignment problem."""
import sys
from typing import Callable, TypeVar
from build.item import SkillpointsTuple
import numpy as np
from ortools.sat.python import cp_model
from build import item, build

np.set_printoptions(threshold=sys.maxsize)
T = TypeVar('T')
types = ['helmet', 'chestplate', 'leggings', 'boots', 'ring', 'ring2', 'bracelet', 'necklace']
spinner = ['|', '/', '-', '\\']


class CPModelSolver:
    def __init__(self, items: list[item.Item],
                 score_function: Callable[[item.Item], int],
                 weapon: item.Item):
        """
        Create a linear programming optimizer for a Build.
        :param items: A list of items to use in the Build.
        :param score_function: A function that returns the score of an individual item.
        :param weapon: The weapon used in the build.
        """
        self._weapon = weapon
        item_count = []

        self.model = cp_model.CpModel()

        self._items: list[item.Item] = []
        self.item_variables = []
        t_var_dict = {}

        # Manual skillpoint assignment variables
        self.sp_assignment_vars = SkillpointsTuple(
            *(self.model.new_int_var(0, 102, f"sp_{name}") for name in ['str', 'dex', 'int', 'def', 'agi']))
        self.model.add(sum(self.sp_assignment_vars) <= 204)

        sp_reqs = SkillpointsTuple([], [], [], [], [])

        for item_type in types:
            t_items = [itm for itm in items if item_type == itm.type]
            self._items += t_items
            item_count.append(len(t_items))

            # Add exactly one item of each type
            t_vars = [self.model.new_bool_var(f"x[{item_type},{itm.name}]") for itm in t_items]
            self.model.add_exactly_one(t_vars)
            self.item_variables += t_vars
            t_var_dict[item_type] = t_vars

            # Skillpoint requirements
            t_sp_reqs = SkillpointsTuple([], [], [], [], [])
            for itm, x in zip(t_items, t_vars):
                for t_sp_req, itm_sp_bonus, itm_sp_req in zip(t_sp_reqs, itm.identifications.skillpoints, itm.requirements.skillpoints):
                    if itm_sp_req != 0:
                        t_sp_req.append((itm_sp_bonus + itm_sp_req + 1000) * x)

            for sp_assign, t_sp_req, sp_req in zip(self.sp_assignment_vars, t_sp_reqs, sp_reqs):
                sp_req.append(sum(t_sp_req) - 1000)

        # Prevent same build with swapped rings
        r1_ind = [i*x for i, x in enumerate(t_var_dict['ring'])]
        r2_ind = [i*x for i, x in enumerate(t_var_dict['ring2'])]
        self.model.add(sum(r1_ind) <= sum(r2_ind))

        # Skillpoint bonuses
        sp_bonuses = SkillpointsTuple([], [], [], [], [])
        for itm, x in zip(self._items, self.item_variables):
            if not isinstance(itm, item.Crafted):
                for sp_bonus, itm_sp_bonus in zip(sp_bonuses, itm.identifications.skillpoints):
                    if itm_sp_bonus != 0:
                        sp_bonus.append(itm_sp_bonus * x)

        # Skillpoint requirement constraints
        for sp_assign, w_sp_req, sp_bonus, sp_req in zip(self.sp_assignment_vars, weapon.requirements.skillpoints, sp_bonuses, sp_reqs):
            if w_sp_req != 0:
                sp_req.append(w_sp_req)
            sp_req.append(sum(sp_bonus))
            self.model.add_max_equality(sp_assign + sum(sp_bonus), sp_req)

        # Set the objective function
        self._objective = [int(score_function(itm)) * x for itm, x in zip(self._items, self.item_variables)]

        print(item_count)

    def add_upper_bound(self, value: T, item_lambda: Callable[[item.Item], T]):
        """
        Add a constraint that sum(ingr_lambda(i)) ≤ value for the weighted ingredients in the recipe.
        """
        if value is not None:
            a = []
            for itm, x in zip(self._items, self.item_variables):
                a.append(item_lambda(itm)*x)
            self.model.add(value >= sum(a))

    def add_lower_bound(self, value: T, item_lambda: Callable[[item.Item], T]):
        """
        Add a constraint that sum(ingr_lambda(i)) ≥ value for the weighted ingredients in the recipe.
        """
        if value is not None:
            a = []
            for itm, x in zip(self._items, self.item_variables):
                a.append(item_lambda(itm)*x)
            self.model.add(value <= sum(a))

    def add_max_assignable_sp(self, value: int, skillpoint: str):
        """
        Add a constraint that the build can't have more sp of element assigned than a given value.
        :param value: The max value that can be assigned.
        :param skillpoint: The skillpoint that is to be constrained.
        """
        a = ['str','dex','int','def','agi']
        if value is not None and skillpoint in a:
            self.model.add(value >= self.sp_assignment_vars[a.index(skillpoint)])

    def add_max_sp(self, value: int, skillpoint: str):
        """
        Add a constraint that the build can't have more sp of element than a given value.
        In certain cases this might exclude include non-viable builds.
        :param value: The max value for given skillpoint.
        :param skillpoint: The skillpoint that is to be constrained.
        """
        s = ['str','dex','int','def','agi']
        if value is not None and skillpoint in s:
            a = [self._weapon.identifications.skillpoints[s.index(skillpoint)]]
            for itm, x in zip(self._items, self.item_variables):
                a.append(itm.identifications.skillpoints[s.index(skillpoint)] * x)
            self.model.add(value >= sum(a) + self.sp_assignment_vars[s.index(skillpoint)])

    def add_min_sp(self, value: int, skillpoint: str):  # TODO: Better method for this
        """
        Add a constraint that the build can't have less sp of element than a given value.
        In certain cases this might exclude viable builds.
        :param value: The min value for given skillpoint.
        :param skillpoint: The skillpoint that is to be constrained.
        """
        s = ['str','dex','int','def','agi']
        if value is not None and skillpoint in s:
            a = [self._weapon.identifications.skillpoints[s.index(skillpoint)]]
            for itm, x in zip(self._items, self.item_variables):
                a.append(itm.identifications.skillpoints[s.index(skillpoint)] * x)
            self.model.add(value <= sum(a) + self.sp_assignment_vars[s.index(skillpoint)])

    def add_min_score(self, value: int):
        self.model.add(sum(self._objective) >= value)

    def add_min_score_sp(self, value: int, factor):
        itembonusses = [(itm.identifications.skillpoints[0] + itm.identifications.skillpoints[1]) * x for itm, x in zip(self._items, self.item_variables)]
        itembonusses += [self._weapon.identifications.skillpoints[0] + self._weapon.identifications.skillpoints[1]]
        assignsp = self.sp_assignment_vars[0] + self.sp_assignment_vars[1]
        self.model.add(factor*(assignsp + sum(itembonusses)) + sum(self._objective) >= value)

    def mutual_exclude(self, set_items: list[item.Item]):
        """
        Prevent builds from having more than 1 item from the set.
        :param set_items: list of items in a set.
        """
        if len(set_items) > 1:
            a = []
            for itm, x in zip(self._items, self.item_variables):
                if itm.name in set_items:
                    a.append(x)
            self.model.add(sum(a) <= 1)

    def _find(self, silent=False):
        solver = cp_model.CpSolver()
        solution_printer = VarArraySolutionPrinter(self.item_variables, self._items, self._weapon, self.sp_assignment_vars, silent)
        solver.parameters.enumerate_all_solutions = True
        status = solver.solve(self.model, solution_printer)
        if not silent:
            print()
            print(f"Status = {solver.status_name(status)}")
            print(f"Number of solutions found: {solution_printer.solution_count}")

        return solution_printer.solution_count

    def find_best(self, factor):
        """
        Find the build where the sum of the scores of the items in that build is maximized and the constraints
        are satisfied.
        :return: Results.
        """
        itembonusses = [(itm.identifications.skillpoints[0] + itm.identifications.skillpoints[1]) * x for itm, x in zip(self._items, self.item_variables)]
        assignsp = self.sp_assignment_vars[0] + self.sp_assignment_vars[1]
        self.model.maximize(factor*(assignsp + sum(itembonusses)) + sum(self._objective))

        return self._find(silent=True)

    def find_allbest(self):
        """
        Find all builds satisfying the constraints.
        :return: Results.
        """
        self.model.clear_objective()

        return self._find()

class VarArraySolutionPrinter(cp_model.CpSolverSolutionCallback):
    """Print intermediate solutions."""

    def __init__(self, x, items, weapon, spass, silent):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self._x = x
        self._items = items
        self.solution_count = 0
        self._weapon = weapon
        self.spa = spass
        self.silent = silent

    def on_solution_callback(self) -> None:
        self.solution_count += 1
        res_items = []
        for itm, x in zip(self._items, self._x):
            if self.Value(x) == 1:
                res_items.append(itm)
        skps = []
        for skp in self.spa:
            skps.append(self.Value(skp))

        with open('tempoutput.txt', 'a') as f:
            f.write(f"{res_items}\n")
        if not self.silent:
            sys.stdout.write(f"\r{spinner[(int(self.UserTime())) % 4]}  Solving {self.solution_count} builds! {skps}")
            sys.stdout.flush()

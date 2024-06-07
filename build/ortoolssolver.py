"""Solves a simple assignment problem."""
import sys
from typing import Callable, TypeVar
from build.item import SkillpointsTuple
import numpy as np
from ortools.sat.python import cp_model

from build import item, build

np.set_printoptions(threshold=sys.maxsize)
T = TypeVar('T')
types = ['helmet', 'chestplate', 'leggings', 'boots', 'ring', 'bracelet', 'necklace']
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
        self._preitems = []  # TODO: add these
        item_count = []

        self.model = cp_model.CpModel()

        self._items: list[item.Item] = []
        self.item_variables = []
        t_var_dict = {}

        for item_type in types:
            t_items = [itm for itm in items if item_type in itm.type]
            if len(t_items) <= 1:
                self._preitems = self._preitems + t_items
                item_count.append(0)
                # TODO append item reqs
                continue

            positems = [i for i in t_items if score_function(i) > score_function(item.NO_ITEM)]
            self._items += positems
            item_count.append(len(positems))

            if item_type == 'ring':  # build has 2 rings
                t_vars = [self.model.new_int_var(0, 2, f"x[{item_type},{itm.name}]") for itm in positems]
                self.model.add(sum(t_vars) == 2)
            else:
                t_vars = [self.model.new_bool_var(f"x[{item_type},{itm.name}]") for itm in positems]
                self.model.add_exactly_one(t_vars)

            self.item_variables += t_vars
            t_var_dict[item_type] = t_vars

        sp_bonuses = SkillpointsTuple([], [], [], [], [])
        for itm, x in zip(self._items, self.item_variables):
            for sp_bonus, itm_sp_bonus in zip(sp_bonuses, itm.identifications.skillpoints):
                if itm_sp_bonus != 0:
                    sp_bonus.append(itm_sp_bonus * x)
        ## Anselm
        sp_maxs = SkillpointsTuple(70, 70, 150, 10, 10)

        for item_type in types:
            t_items = [itm for itm in items if item_type in itm.type]
            if len(t_items) <= 1:
                continue

            positems = [i for i in t_items if score_function(i) > score_function(item.NO_ITEM)]

            t_vars = t_var_dict[item_type]

            sp_reqs = SkillpointsTuple([], [], [], [], [])
            for itm, x in zip(positems, t_vars):
                for sp_req, itm_sp_bonus, itm_sp_req in zip(sp_reqs, itm.identifications.skillpoints, itm.requirements.skillpoints):
                    if itm_sp_req != 0:
                        sp_req.append((itm_sp_bonus + itm_sp_req) * x)
            if item_type != 'ring':
                for sp_req, sp_bonus, sp_max in zip(sp_reqs, sp_bonuses, sp_maxs):
                    self.model.add(sp_max >= sum(sp_req) - sum(sp_bonus))
            else:
                for sp_req, sp_bonus, sp_max in zip(sp_reqs, sp_bonuses, sp_maxs):
                    self.model.add(2*sp_max >= sum(sp_req) - sum(sp_bonus))

        ## Frederik
        # self.sp_assignment_vars = SkillpointsTuple(
        #     *(self.model.new_int_var(0, 104, f"sp_{name}") for name in ['str', 'dex', 'int', 'def', 'agi']))
        #
        # free_sp = 204 - sum(self.sp_assignment_vars)
        # self.model.add(free_sp >= 0)
        # for item_type in types:
        #     t_items = [itm for itm in items if item_type in itm.type]
        #     if len(t_items) <= 1:
        #         continue
        #
        #     positems = [i for i in t_items if score_function(i) > score_function(item.NO_ITEM)]
        #
        #     t_vars = t_var_dict[item_type]
        #
        #     sp_reqs = SkillpointsTuple([], [], [], [], [])
        #     for itm, x in zip(positems, t_vars):
        #         for sp_req, itm_sp_bonus, itm_sp_req in zip(sp_reqs, itm.identifications.skillpoints, itm.requirements.skillpoints):
        #             if itm_sp_req != 0:
        #                 sp_req.append((itm_sp_bonus + itm_sp_req + 1000) * x)
        #
        #     for sp_assign, sp_req, sp_bonus in zip(self.sp_assignment_vars, sp_reqs, sp_bonuses):
        #         self.model.add(sp_assign >= sum(sp_req) - 1000 - sum(sp_bonus))
        #
        # for sp_assign, sp_req, sp_bonus in zip(self.sp_assignment_vars, weapon.requirements.skillpoints, sp_bonuses):
        #     if sp_req != 0:
        #         self.model.add(sp_assign >= sp_req - sum(sp_bonus))
        #

        self._objective = [int(score_function(itm)) * x for itm, x in zip(self._items, self.item_variables)]
        # #print(self._objective)
        self.model.add(sum(self._objective) > 5800) # 5925
        # #self.model.add(sum(self._objective) < 1650)
        # #self.model.maximize(free_sp)
        hive_master = ["Abyss-Imbued Leggings","Boreal-Patterned Crown","Anima-Infused Cuirass","Chaos-Woven Greaves","Elysium-Engraved Aegis","Eden-Blessed Guards","Gaea-Hewn Boots","Hephaestus-Forged Sabatons","Obsidian-Framed Helmet","Twilight-Gilded Cloak","Contrast","Prowess","Intensity"]
        self.mutual_exclude(hive_master)

        print(item_count)

    def add_upper_bound(self, value: T, item_lambda: Callable[[item.Item], T]):
        if value is not None:
            a = []
            for itm, x in zip(self._items, self.item_variables):
                a.append(item_lambda(itm)*x)
            self.model.add(value >= sum(a))

    def add_lower_bound(self, value: T, item_lambda: Callable[[item.Item], T]):
        if value is not None:
            a = []
            for itm, x in zip(self._items, self.item_variables):
                a.append(item_lambda(itm)*x)
            self.model.add(value <= sum(a))

    def mutual_exclude(self, set_items):
        if len(set_items) > 1:
            a = []
            for itm, x in zip(self._items, self.item_variables):
                if itm.name in set_items:
                    a.append(x)
            self.model.add(sum(a) <= 1)

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
            for itm, x in zip(self._items, self.item_variables):
                if solver.value(x) == 1:
                    res_items.append(itm)
                elif solver.value(x) == 2:
                    res_items.append(itm)
                    res_items.append(itm)
        b = build.Build(self._weapon, *res_items)

        return [(b,res_score)]

    def find_allbest(self):
        """
        Find the build where the sum of the scores of the items in that build is maximized and the constraints
        are satisfied.
        :return: The score of the best build and the items in that build.
        """
        solver = cp_model.CpSolver()
        solution_printer = VarArraySolutionPrinter(self.item_variables, self._items, self._weapon, [0])# self.sp_assignment_vars)
        solver.parameters.enumerate_all_solutions = True
        status = solver.solve(self.model, solution_printer)
        print()
        print(f"Status = {solver.status_name(status)}")
        print(f"Number of solutions found: {solution_printer.solution_count}")

        return solution_printer.results

class VarArraySolutionPrinter(cp_model.CpSolverSolutionCallback):
    """Print intermediate solutions."""

    def __init__(self, x, items, weapon, spass):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self._x = x
        self._items = items
        self.solution_count = 0
        self.results = []
        self._weapon = weapon
        self.spa = spass

    def on_solution_callback(self) -> None:
        self.solution_count += 1
        res_items = []
        for itm, x in zip(self._items, self._x):
            if self.Value(x) == 1:
                res_items.append(itm)
            elif self.Value(x) == 2:
                res_items.append(itm)
                res_items.append(itm)

        b = build.Build(self._weapon, *res_items)
        reqsp, bonsp = b.calc_sp()
        if sum(reqsp) <= 205:
            #self.results.append((b, reqsp))
            self.results.append(0)
            with open('tempoutput.txt', 'a') as f:
                f.write(f"{b.items}\n")

        sys.stdout.write(f"\r{spinner[(int(self.UserTime())) % 4]}  Solving {len(self.results)}/{self.solution_count} valid builds! {reqsp}")
        sys.stdout.flush()

        #if self.UserTime() > 60:
        #    self.StopSearch()

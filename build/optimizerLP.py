from typing import Callable, TypeVar
import sys

import numpy as np

from core.optimizer.linearProgramming import BinaryLinearProgramm
from build import item
from utils.decorators import single_use
from build import build

np.set_printoptions(threshold=sys.maxsize)
T = TypeVar('T')
types = ['helmet', 'chestplate', 'leggings', 'boots', 'ring', 'bracelet', 'necklace']


class LPBuildOptimizer(BinaryLinearProgramm):
    def __init__(self, items: list[item.Item],
                 score_function: Callable[[item.Item], float],
                 weapon: item.Item):
        """
        Create a linear programming optimizer for a Build.
        :param items: A list of ingredients to use in the Build.
        :param score_function: A function that returns the score of an individual ingredient.
        :weapon: The weapon used in the build.
        """
        self._weapon = weapon
        self._items = []
        self._preitems = []  # TODO: add these
        item_count = []
        b_eq = []
        bounds = []
        for i, t in enumerate(types):
            t_items = [it for it in items if t in it.type]
            if len(t_items) == 0:
                continue
            if t == 'ring':
                if len(t_items) <= 2:
                    self._preitems = self._preitems + t_items
                else:
                    self._items = self._items + t_items
                    b_eq.append(2)
                    item_count.append(len(t_items))
                    bounds.append((0, 2))
            else:
                if len(t_items) == 1:
                    self._preitems = self._preitems + t_items
                else:
                    self._items = self._items + t_items
                    b_eq.append(1)
                    item_count.append(len(t_items))
                    bounds.append((0, 1))
        print(item_count)
        self._score = score_function

        # TODO: Preprocessing for preitems

        A_eq = np.zeros((len(item_count), sum(item_count)), dtype=int)
        col = 0
        for i, val in enumerate(item_count):
            A_eq[i, col:col + val] = 1
            col += val
        c = [-round(self._score(it),6) for it in self._items]
        super().__init__(
            c=c,
            A_ub=[],
            b_ub=[],
            A_eq=A_eq,
            b_eq=b_eq,
            bounds=bounds
        )

    def find_best(self):
        """
        Find the build where the sum of the scores of the items in that build is maximized and the constraints
        are satisfied.
        :return: The score of the best build and the items in that build.
        """
        res = self.solve()
        if not res.success:
            return 0, []
        res_score = -round(res.fun,4)
        res_items = [self._items[i] for i, x in enumerate(res.x) if x >= 0.999] + self._preitems
        return res_score, res_items

    def find_best_validn(self, n: int):
        """
        Find N builds where the sum of the scores of the items in that build is maximized and the constraints
        are satisfied.
        :return: The score of the best build and the items in that build.
        """
        results = []
        spinner = ['|', '/', '-', '\\']
        self.A_ub.append([-score for score in self.c])
        self.b_ub.append(6695)
        i = 0
        print(self._weapon)
        try:
            while len(results) < n:
                res = self.solve()

                if not res.success:
                    break
                res_score = -round(res.fun,6)
                res_items = [self._items[i] for i, x in enumerate(res.x) if x >= 0.999] + self._preitems

                i += 1
                sys.stdout.write(f"\r{spinner[(i//3)%4]}  Solving {len(results)}/{i} valid builds! Current score: {res_score}")
                sys.stdout.flush()

                b = build.Build(self._weapon, *res_items)
                reqsp, bonsp = b.calc_sp()
                if sum(reqsp) < 205:
                    results.append((res_score, res_items, sum(reqsp)))
                self.b_ub[-1] = res_score-0.00001
            sys.stdout.write("\r")
            sys.stdout.flush()
            print(f"{len(results)} valid builds out of N={i} tested builds found!")
        except KeyboardInterrupt:
            sys.stdout.write("\r")
            sys.stdout.flush()
            print(f"Interrupted at N={i}")
            print(f"{len(results)} valid builds found!")
        return results

    def find_bestn2(self, n: int):
        """
        Find N builds where the sum of the scores of the items in that build is maximized and the constraints
        are satisfied.
        :return: The score of the best build and the items in that build.
        """
        results = []
        spinner = ['|', '/', '-', '\\']
        self.A_ub.append([-score for score in self.c])
        self.b_ub.append(10000)
        try:
            for i in range(n):
                res = self.solve()

                sys.stdout.write(f"\r{spinner[(i//3)%4]}  Solving N={i}/{n}")
                sys.stdout.flush()



                if not res.success:
                    break
                res_score = -round(res.fun,4)
                res_items = [self._items[i] for i, x in enumerate(res.x) if x >= 0.999] + self._preitems
                results.append((res_score, res_items))
                self.b_ub[-1] = res_score-0.001
            sys.stdout.write("\r")
            sys.stdout.flush()
        except KeyboardInterrupt:
            sys.stdout.write("\r")
            sys.stdout.flush()
            print(f"Interrupted at N={i}")
        return results

    def find_bestn(self, n: int):
        """
        Find N builds where the sum of the scores of the items in that build is maximized and the constraints
        are satisfied.
        :return: The score of the best build and the items in that build.
        """
        results = []
        spinner = ['|', '/', '-', '\\']
        try:
            for i in range(n):
                res = self.solve()

                sys.stdout.write(f"\r{spinner[(i//3)%4]}  Solving N={i}/{n}")
                sys.stdout.flush()



                if not res.success:
                    break
                res_score = -round(res.fun,4)
                res_items = [self._items[i] for i, x in enumerate(res.x) if x >= 0.999] + self._preitems
                results.append((res_score, res_items))
                self.A_ub.append(res.x)
                self.b_ub.append(7)
            sys.stdout.write("\r")
            sys.stdout.flush()
        except KeyboardInterrupt:
            sys.stdout.write("\r")
            sys.stdout.flush()
            print(f"Interrupted at N={i}")
        return results

    def add_max_constraint(self, value: T, item_lambda: Callable[[item.Item], T]):
        """
        Add a constraint that sum(ingr_lambda(i)) ≤ value for the weighted ingredients in the Build.
        """
        if value is not None:
            self.A_ub.append([item_lambda(it) for it in self._items])
            self.b_ub.append(value)

    def add_min_constraint(self, value: T, item_lambda: Callable[[item.Item], T]):
        """
        Add a constraint that sum(ingr_lambda(i)) ≥ value for the weighted ingredients in the Build.
        """
        self.add_max_constraint(-value, lambda i: -item_lambda(i))

    @single_use
    def set_max_str_req(self, value: int):
        self.add_max_constraint(value, lambda i: i.requirements.strength)

    @single_use
    def set_max_dex_req(self, value: int):
        self.add_max_constraint(value, lambda i: i.requirements.dexterity)

    @single_use
    def set_max_int_req(self, value: int):
        self.add_max_constraint(value, lambda i: i.requirements.intelligence)

    @single_use
    def set_max_def_req(self, value: int):
        self.add_max_constraint(value, lambda i: i.requirements.defence)

    @single_use
    def set_max_agi_req(self, value: int):
        self.add_max_constraint(value, lambda i: i.requirements.agility)

    def add_max_sp_sum_req(self, value: int, strength=True, dexterity=True, intelligence=True, defence=True,
                           agility=True):
        def sp_sum(it: item.Item):
            val = 0
            if strength:
                val += it.requirements.strength - it.identifications["rawStrength"].max
            if dexterity:
                val += it.requirements.dexterity - it.identifications["rawDexterity"].max
            if intelligence:
                val += it.requirements.intelligence - it.identifications["rawIntelligence"].max
            if defence:
                val += it.requirements.defence - it.identifications["rawDefence"].max
            if agility:
                val += it.requirements.agility - it.identifications["rawAgility"].max
            return val

        self.add_max_constraint(value, lambda i: sp_sum(i))

    def set_identification_max(self, identification: item.IdentificationType, value: int):
        self.add_max_constraint(value, lambda i: i.identifications[identification].max)

    def set_identification_min(self, identification: item.IdentificationType, value: int):
        self.add_min_constraint(value, lambda i: i.identifications[identification].max)

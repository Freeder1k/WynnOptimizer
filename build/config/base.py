from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Callable

from build import item
from build.item import IdentificationType


class HybridOptimizerConfig:

    def __init__(self, items: list[item.Item],
                 score_function: Callable[[item.Item], float]):
        """
        Class that contains relevant config information for the hybrid optimizer to run.
        :param item: The items to include in the search.
        :param score_function: A function that determines the score of a single item. Higher = better.
        """
        self.items = items
        self.score_function = score_function
        self.max_str_req = None
        self.max_dex_req = None
        self.max_int_req = None
        self.max_def_req = None
        self.max_agi_req = None
        self.max_sp_sum_req: list[tuple[int, dict[str, bool]]] = []
        self.max_id_reqs = {}
        self.min_id_reqs = {}
        self.N = 1

    def set_max_str_req(self, value: int):
        self.max_str_req = value
        return self

    def set_max_dex_req(self, value: int):
        self.max_dex_req = value
        return self

    def set_max_int_req(self, value: int):
        self.max_int_req = value
        return self

    def set_max_def_req(self, value: int):
        self.max_def_req = value
        return self

    def set_max_agi_req(self, value: int):
        self.max_agi_req = value
        return self

    def add_max_sp_sum_req(self, value: int, strength=True, dexterity=True, intelligence=True, defence=True,
                           agility=True):
        self.max_sp_sum_req.append((value, {"strength": strength, "dexterity": dexterity, "intelligence": intelligence,
                                            "defence": defence, "agility": agility}))

    def set_identification_max(self, identification: IdentificationType, value: int):
        self.max_id_reqs[identification] = value
        return self

    def set_identification_min(self, identification: IdentificationType, value: int):
        self.min_id_reqs[identification] = value
        return self

    def set_num_builds(self, value: int):
        self.N = value
        return self

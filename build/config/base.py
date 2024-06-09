from typing import Callable

from build import item
from build.item import IdentificationType


class OptimizerConfig:

    def __init__(self, items: list[item.Item],
                 score_function: Callable[[item.Item], float]):
        """
        Class that contains relevant config information for the optimizer to run.
        :param items: The items to include in the search.
        :param score_function: A function that determines the score of a single item. Higher = better.
        """
        self.items = items
        self.score_function = score_function
        self.max_ids = {}
        self.min_ids = {}
        self.max_reqs = {}
        self.min_reqs = {}
        self.weapon = item.NO_ITEM
        self.mastery = [False, False, False, False, False, False]
        self.skilltree = ''

    def set_requirement_max(self, element: str, value: int):
        self.max_reqs[element] = value
        return self

    def set_requirement_min(self, element: str, value: int):
        self.min_reqs[element] = value
        return self

    def set_identification_max(self, identification: str, value: int):
        self.max_ids[identification] = value
        return self

    def set_identification_min(self, identification: str, value: int):
        self.min_ids[identification] = value
        return self

    def set_weapon(self, i: item.Weapon):
        self.weapon = i
        return self

    def set_elemental_mastery(self, mastery: list[bool]):
        self.mastery = mastery
        return self

    def set_skilltree(self, skilltree: str):
        self.skilltree = skilltree
        return self

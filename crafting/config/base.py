from abc import ABC, abstractmethod
from dataclasses import dataclass

from crafting import ingredient


class OptimalCrafterConfigBase(ABC):
    def __init__(self, ingredients: list[ingredient.Ingredient], ids: list[str], min_score: int):
        """
        Class that contains relevant config information for the optimizer to run.
        :param ingredients: The ingredients to include in the search.
        :param ids: relevant identifications for the optimization (currently limited to 5). These will be id1-id5 (in
        order) in the constraints and score functions.
        :param min_score: A minimum score value (can improve performance).
        """
        self.ingredients = ingredients
        self.ids = ids
        self.min_score = min_score

    @staticmethod
    @abstractmethod
    def constraints(charges, duration, durability, req_str, req_dex, req_int, req_def, req_agi, id1_min, id1_max,
                    id2_min, id2_max, id3_min, id3_max, id4_min, id4_max, id5_min, id5_max) -> bool:
        """
        Function to determine if a craft should be viable for selection.
        Make sure it is compilable by numba.
        """
        pass

    @staticmethod
    @abstractmethod
    def score(charges, duration, durability, req_str, req_dex, req_int, req_def, req_agi, id1_min, id1_max, id2_min,
              id2_max, id3_min, id3_max, id4_min, id4_max, id5_min, id5_max) -> float:
        """
        Function to determine the score of a craft. Should return values > 0 for viable crafts.
        Make sure it is compilable by numba.
        """
        pass


@dataclass
class MaxSPReqs:
    strength: int
    dexterity: int
    intelligence: int
    defence: int
    agility: int
    total: int


class LinearOptimizerConfigBase(ABC):
    def __init__(self, ingredients: list[ingredient.Ingredient], mods: list[int], profession: str, min_charges: int,
                 min_duration: int, min_durability: int, sp_constr: MaxSPReqs, id_reqs: dict[str, int]):
        """
        Class that contains relevant config information for the ILP optimizer to run.
        """
        self.ingredients = ingredients
        self.mods = mods
        self.profession = profession
        self.min_charges = min_charges
        self.min_duration = min_duration
        self.min_durability = min_durability
        self.sp_constr = sp_constr
        self.id_reqs = id_reqs

    @staticmethod
    @abstractmethod
    def score(ingr: ingredient.Ingredient) -> float:
        """
        Function to determine the score of a single ingredient.
        Higher = better. Can return any positive or negative value.
        """
        pass

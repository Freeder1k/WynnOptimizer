from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Callable

from craft import ingredient
from craft.ingredient import IdentificationType


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
                 min_duration: int, min_durability: int, sp_constr: MaxSPReqs, id_reqs: dict[str, int],
                 relevant_ids: list[IdentificationType]):
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
        self.relevant_ids = relevant_ids

    @staticmethod
    @abstractmethod
    def score(ingr: ingredient.Ingredient) -> float:
        """
        Function to determine the score of a single ingredient.
        Higher = better. Can return any positive or negative value.
        """
        pass


class HybridOptimizerConfig:

    def __init__(self, ingredients: list[ingredient.Ingredient],
                 score_function: Callable[[ingredient.Ingredient], float],
                 crafting_skill: str, relevant_ids: list[IdentificationType]):
        """
        Class that contains relevant config information for the hybrid optimizer to run.
        :param ingredients: The ingredients to include in the search.
        :param score_function: A function that determines the score of a single ingredient. Higher = better.
        :param crafting_skill: The crafting skill the craft is for.
        :param relevant_ids: IDs that are used in the scoring function.
        """
        self.ingredients = [i for i in ingredients if crafting_skill in i.requirements.skills]
        self.score_function = score_function
        self.crafting_skill = crafting_skill
        self.relevant_ids = relevant_ids
        self.min_charges = None
        self.min_duration = None
        self.min_durability = None
        self.max_str_req = None
        self.max_dex_req = None
        self.max_int_req = None
        self.max_def_req = None
        self.max_agi_req = None
        self.max_sp_sum_req: list[tuple[int, dict[str, bool]]] = []
        self.max_id_reqs = {}
        self.min_id_reqs = {}

    def set_min_charges(self, value: int):
        self.min_charges = value
        return self

    def set_min_duration(self, value: int):
        self.min_duration = value
        return self

    def set_min_durability(self, value: int):
        self.min_durability = value
        return self

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

    def add_max_sp_sum_req(self, value: int, strength=False, dexterity=False, intelligence=False, defence=False,
                           agility=False):
        self.max_sp_sum_req.append((value, {"strength": strength, "dexterity": dexterity, "intelligence": intelligence,
                                            "defence": defence, "agility": agility}))

    def set_identification_max(self, identification: IdentificationType, value: int):
        self.max_id_reqs[identification] = value
        if identification not in self.relevant_ids:
            self.relevant_ids.append(identification)
        return self

    def set_identification_min(self, identification: IdentificationType, value: int):
        self.min_id_reqs[identification] = value
        if identification not in self.relevant_ids:
            self.relevant_ids.append(identification)
        return self

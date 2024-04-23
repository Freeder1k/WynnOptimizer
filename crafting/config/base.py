from abc import ABC, abstractmethod

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

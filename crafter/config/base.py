from abc import ABC, abstractmethod

from crafter import ingredient


class OptimalCrafterConfigBase(ABC):
    def __init__(self, ingredients: list[ingredient.Ingredient], ids: list[str], min_score: int):
        self.ingredients = ingredients
        self.ids = ids
        self.min_score = min_score

    @staticmethod
    @abstractmethod
    def constraints(charges, duration, durability, req_str, req_dex, req_int, req_def, req_agi,
                    id1_min, id1_max, id2_min, id2_max, id3_min, id3_max, id4_min, id4_max, id5_min, id5_max):
        pass

    @staticmethod
    @abstractmethod
    def score(charges, duration, durability, req_str, req_dex, req_int, req_def, req_agi,
              id1_min, id1_max, id2_min, id2_max, id3_min, id3_max, id4_min, id4_max, id5_min, id5_max):
        pass

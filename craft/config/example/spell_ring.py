import cupy

from ..base import OptimalCrafterConfigBase
from ... import ingredient


class SpellRingConfig(OptimalCrafterConfigBase):
    __create_key = object()

    def __init__(self, create_key, ingredients, ids, min_score):
        assert (create_key == self.__create_key), \
            "Please use the load() method to create an instance of this object."
        super().__init__(ingredients, ids, min_score)

    @staticmethod
    def constraints(charges, duration, durability, req_str, req_dex, req_int, req_def, req_agi, id1_min, id1_max,
                    id2_min, id2_max, id3_min, id3_max, id4_min, id4_max, id5_min, id5_max):
        return (
                durability > -735 + 50 and id1_max > 0 and id4_max >= 0 and id5_max >= 0
                and req_str <= 100
                and req_dex <= 120
                and req_int <= 65
                and req_def <= 0
                and req_agi <= 0
        )

    @staticmethod
    def score(charges, duration, durability, req_str, req_dex, req_int, req_def, req_agi, id1_min, id1_max, id2_min,
              id2_max, id3_min, id3_max, id4_min, id4_max, id5_min, id5_max) -> cupy.float32:
        return (
            100 * id1_max
            + 56 * id2_max
            + 35 * id3_max
            + round(min((durability + 735) * 0.1, 25.))
        )

    @classmethod
    def load(cls):
        eff_ings = [ingr for ingr in ingredient.get_all_ingredients().values() if
                    ingr.modifiers.abs_total() > 0]
        ings1 = [ingr for ingr in ingredient.get_all_ingredients().values() if
                 abs(ingr.identifications["spellDamage"].max) > 0]
        ings2 = [ingr for ingr in ingredient.get_all_ingredients().values() if
                 abs(ingr.identifications["thunderDamage"].max) > 0]
        ings3 = [ingr for ingr in ingredient.get_all_ingredients().values() if
                 abs(ingr.identifications["earthDamage"].max) > 0]
        ingredients = {i.name for i in eff_ings + ings1 + ings2 + ings3}
        ingredients.add("Stolen Pearls")
        ingredients = [ingredient.get_ingredient(name) for name in [
        ] + list(ingredients)]

        ingredients = [ingr for ingr in ingredients if "jeweling" in ingr.requirements.skills]
        ids = ["spellDamage", "thunderDamage", "earthDamage", "manaRegen", "rawIntelligence"]
        return cls(cls.__create_key, ingredients, ids, 2000)

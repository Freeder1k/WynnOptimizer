from typing import Callable
import copy
from build import item
from build.item import IdentificationType

hive_master = ["Abyss-Imbued Leggings","Boreal-Patterned Crown","Anima-Infused Cuirass","Chaos-Woven Greaves","Elysium-Engraved Aegis","Eden-Blessed Guards","Gaea-Hewn Boots","Hephaestus-Forged Sabatons","Obsidian-Framed Helmet","Twilight-Gilded Cloak","Contrast","Prowess","Intensity"]
hive_earth = ["Ambertoise Shell","Beetle Aegis","Elder Oak Roots","Humbark Moccasins","Subur Clip","Golemlus Core"]
hive_thunder = ["Sparkling Visor","Insulated Plate Mail","Static-Charged Leggings","Thunderous Step","Bottled Thunderstorm","Lightning Flash"]
hive_water = ["Whitecap Crown","Stillwater Blue","Trench Scourer","Silt of the Seafloor","Coral Ring","Moon Pool Circlet"]
hive_fire = ["Sparkweaver","Soulflare","Cinderchain","Mantlewalkers","Clockwork","Dupliblaze"]
hive_air = ["Pride of the Aerie","Gale's Freedom","Turbine Greaves","Flashstep","Breezehands","Vortex Bracer"]



class OptimizerConfig:

    def __init__(self, items: list[item.Item],
                 score_function: Callable[[item.Item], float]):
        """
        Class that contains relevant config information for the optimizer to run.
        :param items: The items to include in the search.
        :param score_function: A function that determines the score of a single item. Higher = better.
        """
        self.items = items
        if 'ring2' not in [i.type for i in items]:
            extra_rings = []
            for itm in items:
                if itm.type == 'ring':
                    itm2 = copy.deepcopy(itm)
                    itm2.type = 'ring2'
                    extra_rings.append(itm2)
            items += extra_rings
        self.exclusive_sets = [hive_master, hive_earth, hive_thunder, hive_water, hive_fire, hive_air]
        self.score_function = score_function
        self.max_ids = {}
        self.min_ids = {}
        self.max_reqs = {}
        self.max_sp = {}
        self.min_sp = {}
        self.weapon = item.NO_ITEM
        self.mastery = [False, False, False, False, False, False]
        self.skilltree = ''
        self.sdfactor = 0

    def set_requirement_max(self, element: str, value: int):
        self.max_reqs[element] = value
        return self

    def set_sp_max(self, element: str, value: int):
        self.max_sp[element] = value
        return self

    def set_sp_min(self, element: str, value: int):
        self.min_sp[element] = value
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
        self.mastery = [False] + mastery
        return self

    def set_skilltree(self, skilltree: str):
        self.skilltree = skilltree
        return self

    def set_sdfactor(self, value):
        self.sdfactor = value
        return self

from dataclasses import dataclass
from enum import StrEnum


@dataclass
class Identification:
    raw: int
    min: int = None
    max: int = None

    def __init__(self, data: int | dict):
        if isinstance(data, int):
            self.raw = data
        else:
            self.min = data['min']
            self.max = data['max']
            self.raw = data.get('raw', 0.5 * (self.min + self.max))


@dataclass
class Modifiers:
    left: int = 0
    right: int = 0
    above: int = 0
    under: int = 0
    touching: int = 0
    notTouching: int = 0


class Skill(StrEnum):
    WEAPONSMITHING = "weaponsmithing"
    WOODWORKING = "woodworking"
    ARMOURING = "armouring"
    TAILORING = "tailoring"
    JEWELING = "jeweling"
    COOKING = "cooking"
    ALCHEMISM = "alchemism"
    SCRIBING = "scribing"


@dataclass
class Requirements:
    skills: list[Skill]
    strength: int = 0
    dexterity: int = 0
    intelligence: int = 0
    defence: int = 0
    agility: int = 0
    level: int = 0

    def __init__(self, item_only_ids: dict, requirements: dict):
        self.skills = [Skill(skill) for skill in requirements['skills']]
        self.strength = item_only_ids.get('strength', 0)
        self.dexterity = item_only_ids.get('dexterity', 0)
        self.intelligence = item_only_ids.get('intelligence', 0)
        self.defence = item_only_ids.get('defence', 0)
        self.agility = item_only_ids.get('agility', 0)
        self.level = requirements.get('level', 0)


@dataclass
class Ingredient:
    name: str
    charges: int
    duration: int
    durability: int
    identifications: dict[str, Identification]
    modifiers: Modifiers
    requirements: Requirements

    @classmethod
    def from_api_json(cls, name, data: dict):
        try:
            return cls(
                name,
                data['consumableOnlyIDs']['charges'] if 'consumableOnlyIDs' in data else 0,
                data['consumableOnlyIDs']['duration'] if 'consumableOnlyIDs' in data else 0,
                data['itemOnlyIDs']['durabilityModifier'] if 'itemOnlyIDs' in data else 0,
                {k: Identification(v) for k, v in data['identifications'].items()} if 'identifications' in data else {},
                Modifiers(**data['ingredientPositionModifiers']),
                Requirements(data['itemOnlyIDs'], data['requirements']),
            )
        except Exception as e:
            print(name)
            raise e

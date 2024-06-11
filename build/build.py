# import craft.ingredient
# from utils.integer import Base64
from build.item import Item, Crafted, Weapon
import utils.skillpoints as sp
from utils.integer import Base64


class Build:
    def __init__(self, weapon: Weapon, i1: Item, i2: Item, i3: Item, i4: Item, i5: Item, i6: Item, i7: Item, i8: Item):
        """
        Wynncraft build class.
        """
        self.weapon = weapon
        self.items = (i1, i2, i3, i4, i5, i6, i7, i8)
        self._item = None
        self._required_sp = None
        self._bonus_sp = None

    def build(self) -> Item:
        """
        Build from the items.
        :return: A new Item object representing the build.
        """
        if self._item is not None:
            return self._item

        name = "build"  # Future: Come up with naming scheme

        # calculate the build stats
        result = self.weapon
        for i in range(8):
            result = result + (self.items[i])

        self._item = Item(name, "build", result.identifications, result.requirements)

        return self._item

    def calc_sp(self):
        if self._required_sp is not None:
            return self._required_sp, self._bonus_sp

        self._required_sp, self._bonus_sp = sp.skillpoints(self)

        return self._required_sp, self._bonus_sp

    def __str__(self):
        return str(self.items)

    def __repr__(self):
        return str(self.items)

    def generate_link(self, skilltree = ""):
        build_string = 'https://hppeng-wynn.github.io/builder?v=7#9_'
        for itm in self.items:
            if isinstance(itm, Crafted):
                build_string += "CR-"+itm.name
            else:
                build_string += itm.b64_hash()
        build_string += self.weapon.b64_hash()
        for skillpoint in sp.skillPoints:
            build_string += Base64.fromInt(self.build().identifications[skillpoint].max,2)#.rjust(2, "0")
        build_string += Base64.fromInt(106,2)#.rjust(2, "0")  # Level
        build_string += "0000"  # This would be where armor powders go
        build_string += Base64.fromInt((len(self.weapon.powders)-1)//6 + 1)
        powder_hash = 0
        for i, powder in enumerate(self.weapon.powders):
            powder_hash = (powder_hash << 5) + {'e':6,'t':12,'w':18,'f':24,'a':36}[powder]
            if (i+1)%6 == 0 and i != 0:
                build_string += Base64.fromInt(powder_hash,5)
                print(i, powder_hash)
                powder_hash = 0
        if powder_hash != 0:
            build_string += Base64.fromInt(powder_hash,5)
        build_string += '0z0z0+0+0+0+0-'  # This would be where tomes go
        build_string += skilltree

        return build_string


    # Havent done this yet
    '''
    def b64_hash(self):
        return "".join([Base64.fromInt(craft.ingredient.get_ing_id(i.name)).rjust(2, "0") for i in self.ingredients])

    @classmethod
    def from_ingredient_strings(cls, i1: str, i2: str, i3: str, i4: str, i5: str, i6: str):
        return cls(*(craft.ingredient.get_ingredient(ing) for ing in (i1, i2, i3, i4, i5, i6)))

    def __str__(self):
        return f"Recipe({', '.join(str(i) for i in self.ingredients)})"

    def __repr__(self):
        return self.__str__()'''
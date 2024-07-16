from ortools.sat.python.cp_model import LinearExpr

from cp_utils.LinearExprFactory import LinearExprFactory
from wynndata.base import SkillpointsTuple


class CPRequirements:
    strength: LinearExpr
    dexterity: LinearExpr
    intelligence: LinearExpr
    defence: LinearExpr
    agility: LinearExpr

    def __init__(self, lin_expr_fac: LinearExprFactory):
        self.lin_expr_fac = lin_expr_fac

    def __getattr__(self, item):
        expr = self.lin_expr_fac.generate(lambda i: getattr(i.requirements, item), name=f"requirements.{item}")
        setattr(self, item, expr)
        return expr

    def __getitem__(self, key):
        match key:
            case 'strength', 'str':
                return self.strength
            case 'dexterity', 'dex':
                return self.dexterity
            case 'intelligence', 'int':
                return self.intelligence
            case 'defence', 'def':
                return self.defence
            case 'agility', 'agi':
                return self.agility
            case _:
                raise KeyError(key)

    @property
    def skillpoints(self) -> SkillpointsTuple[LinearExpr]:
        return SkillpointsTuple(self.strength, self.dexterity, self.intelligence, self.defence, self.agility)

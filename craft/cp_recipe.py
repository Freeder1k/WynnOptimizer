from ortools.sat.python.cp_model import LinearExpr

from cp_utils.cp_identifications import CPIdentifications
from cp_utils.cp_requirements import CPRequirements
from cp_utils.linear_expr_factory import LinearExprFactory


class CPRecipe:
    def __init__(self, lin_expr_fac_raw: LinearExprFactory, lin_expr_fac_effective: LinearExprFactory):
        self.lin_expr_fac = lin_expr_fac_raw
        self.requirements = CPRequirements(lin_expr_fac_effective)
        self.identifications = CPIdentifications(lin_expr_fac_effective)
        self._charges = None
        self._duration = None
        self._durability = None

    @property
    def charges(self) -> LinearExpr:
        if self._charges is None:
            self._charges = self.lin_expr_fac.generate(lambda i: i.charges) + 3
        return self._charges

    @property
    def duration(self) -> LinearExpr:
        if self._duration is None:
            self._duration = self.lin_expr_fac.generate(lambda i: i.duration)
        return self._duration

    @property
    def durability(self) -> LinearExpr:
        if self._durability is None:
            self._durability = self.lin_expr_fac.generate(lambda i: i.durability // 1000) + 735
        return self._durability

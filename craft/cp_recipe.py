from ortools.sat.python.cp_model import LinearExpr

from cp_utils.cp_identifications import CPIdentifications
from cp_utils.cp_requirements import CPRequirements
from cp_utils.linear_expr_factory import LinearExprFactory


class CPRecipe:
    def __init__(self, base_lin_expr_fac: LinearExprFactory, ids_lin_expr_fac: LinearExprFactory, reqs_lin_expr_fac: LinearExprFactory):
        self.lin_expr_fac = base_lin_expr_fac
        self.requirements = CPRequirements(reqs_lin_expr_fac)
        self.identifications = CPIdentifications(ids_lin_expr_fac)
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

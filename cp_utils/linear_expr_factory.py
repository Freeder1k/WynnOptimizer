from abc import ABC, abstractmethod
from typing import Callable, Any

from ortools.sat.python.cp_model import LinearExpr


class LinearExprFactory(ABC):
    @abstractmethod
    def generate(self, value_func: Callable[[Any], int], lb=None, ub=None, name: str = None) -> LinearExpr:
        """
        Generate a linear expression from a value function.
        :param value_func: Function that returns the desired value of an ingredient.
        :param lb: The lower bound of the linear expression (optional).
        :param ub: The upper bound of the linear expression (optional).
        :param name: The name of the linear expression.
        """
        pass

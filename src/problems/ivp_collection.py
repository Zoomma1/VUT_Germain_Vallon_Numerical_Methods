from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable


ExactSolution = Callable[[float], float] | None


@dataclass
class IVP:
    name: str
    description: str
    f: Callable[[float, float], float]
    f_string: str
    x0: float
    y0: float
    x_end: float
    exact: ExactSolution = field(default=None)

    def exact_at(self, x: float) -> float | None:
        return self.exact(x) if self.exact is not None else None

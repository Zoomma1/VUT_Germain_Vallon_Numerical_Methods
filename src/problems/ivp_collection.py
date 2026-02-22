from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable

import math


ExactSolution = Callable[[float], float] | None


@dataclass
class IVP:
    name: str
    description: str
    f: Callable[[float, float], float]
    x0: float
    y0: float
    x_end: float
    exact: ExactSolution = field(default=None)

    def exact_at(self, x: float) -> float | None:
        return self.exact(x) if self.exact is not None else None



# Ressource 1
# Exercise 1.7.3
# dx/dt = (2t - x)^2, x(0) = 2
ex_1_7_3 = IVP(
    name="Ex 1.7.3 – (2t−x)²",
    description="dx/dt = (2t - x)^2,  x(0) = 2. Approximate x(1).",
    f=lambda t, x: (2 * t - x) ** 2,
    x0=0.0,
    y0=2.0,
    x_end=1.0,
    exact=None,
)

# Ressource 1
# Exercise 1.7.4
# dx/dt = t - x, x(0) = 1; exact: x(t) = t - 1 + 2*e^(-t)
ex_1_7_4 = IVP(
    name="Ex 1.7.4 – t−x",
    description="dx/dt = t - x,  x(0) = 1. Exact: x = t - 1 + 2*e^(-t).",
    f=lambda t, x: t - x,
    x0=0.0,
    y0=1.0,
    x_end=1.0,
    exact=lambda t: t - 1 + 2 * math.exp(-t),
)


ALL_PROBLEMS: list[IVP] = [
    ex_1_7_3,
    ex_1_7_4,
]

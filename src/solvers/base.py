from __future__ import annotations
import math
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Callable

RHSFunc = Callable[[float, float], float]

DIVERGENCE_THRESHOLD = 1e15


@dataclass
class SolverResult:
    xs: list[float]
    ys: list[float]
    method_name: str
    step_size: float
    n_steps: int = field(init=False)

    def __post_init__(self):
        self.n_steps = len(self.xs) - 1

    def final_value(self) -> float:
        return self.ys[-1]

    def at(self, x_target: float) -> float | None:
        for x, y in zip(self.xs, self.ys):
            if abs(x - x_target) < 1e-12:
                return y
        return None


class Solver(ABC):

    @property
    @abstractmethod
    def name(self) -> str:
        ""

    @abstractmethod
    def _step(self, f: RHSFunc, x: float, y: float, h: float) -> float:
        ""

    def solve(
        self,
        f: RHSFunc,
        x0: float,
        y0: float,
        x_end: float,
        h: float,
    ) -> SolverResult:
        xs = [x0]
        ys = [y0]
        x, y = x0, y0

        while x < x_end - 1e-12:
            h_actual = min(h, x_end - x)
            y = self._step(f, x, y, h_actual)
            x = x + h_actual
            xs.append(x)
            ys.append(y)
            if not math.isfinite(y) or abs(y) > DIVERGENCE_THRESHOLD:
                raise OverflowError(
                    f"Solution diverged (|y| > {DIVERGENCE_THRESHOLD:.0e}) at x={x:.6f}"
                )

        return SolverResult(xs=xs, ys=ys, method_name=self.name, step_size=h)

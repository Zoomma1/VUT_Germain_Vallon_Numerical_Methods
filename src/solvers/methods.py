from __future__ import annotations
import math

from .base import Solver, RHSFunc, DIVERGENCE_THRESHOLD



def _euler_step(f: RHSFunc, x: float, y: float, h: float) -> float:
    return y + f(x, y) * h


class EulerDumb(Solver):
    @property
    def name(self) -> str:
        return "Euler (dumb)"

    def _step(self, f: RHSFunc, x: float, y: float, h: float) -> float:
        return _euler_step(f, x, y, h)

    def solve(self, f, x0, y0, x_end, h):
        nc = math.ceil((x_end - x0) / h)
        xs = [x0]
        ys = [y0]
        x, y = x0, y0
        for _ in range(nc):
            dydx = f(x, y)
            y = y + dydx * h
            x = x + h
            xs.append(x)
            ys.append(y)
            if not math.isfinite(y) or abs(y) > DIVERGENCE_THRESHOLD:
                raise OverflowError(
                    f"Solution diverged (|y| > {DIVERGENCE_THRESHOLD:.0e}) at x={x:.6f}"
                )

        from .base import SolverResult
        return SolverResult(xs=xs, ys=ys, method_name=self.name, step_size=h)


class EulerModular(Solver):
    @property
    def name(self) -> str:
        return "Euler (modular)"

    def _step(self, f: RHSFunc, x: float, y: float, h: float) -> float:
        return _euler_step(f, x, y, h)


class RangeKutta(Solver):
    @property
    def name(self) -> str:
        return "RangeKutta (classical)"

    def _step(self, f: RHSFunc, x: float, y: float, h: float) -> float:
        k1 = f(x,           y)
        k2 = f(x + h / 2.0, y + k1 * h / 2.0)
        k3 = f(x + h / 2.0, y + k2 * h / 2.0)
        k4 = f(x + h,       y + k3 * h)
        return y + (k1 + 2.0 * k2 + 2.0 * k3 + k4) * h / 6.0


ALL_SOLVERS: list[Solver] = [
    EulerDumb(),
    EulerModular(),
    RangeKutta(),
]

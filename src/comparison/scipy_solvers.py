from __future__ import annotations

import numpy as np
from scipy.integrate import solve_ivp

from solvers.base import Solver, RHSFunc, SolverResult, DIVERGENCE_THRESHOLD


class ScipySolver(Solver):
    def __init__(
        self,
        method: str = "RK45",
        rtol: float = 1e-8,
        atol: float = 1e-10,
    ) -> None:
        self.method = method
        self.rtol = rtol
        self.atol = atol

    @property
    def name(self) -> str:
        return f"SciPy {self.method}"

    def _step(self, f: RHSFunc, x: float, y: float, h: float) -> float:
        raise NotImplementedError(
            "ScipySolver does not support _step directly; use solve()."
        )

    def solve(
        self,
        f: RHSFunc,
        x0: float,
        y0: float,
        x_end: float,
        h: float,
    ) -> SolverResult:
        n_steps = max(1, round((x_end - x0) / h))
        t_eval = np.linspace(x0, x_end, n_steps + 1)

        def _blowup(t, y_vec):
            return DIVERGENCE_THRESHOLD - abs(y_vec[0])
        _blowup.terminal = True
        _blowup.direction = -1

        sol = solve_ivp(
            fun=lambda t, y_vec: [f(t, y_vec[0])],
            t_span=(x0, x_end),
            y0=[y0],
            method=self.method,
            t_eval=t_eval,
            rtol=self.rtol,
            atol=self.atol,
            dense_output=False,
            events=_blowup,
        )

        # If the blowup event fired, report it clearly.
        if sol.t_events and len(sol.t_events[0]) > 0:
            t_blow = sol.t_events[0][0]
            raise OverflowError(
                f"Solution diverged (|y| > {DIVERGENCE_THRESHOLD:.0e}) "
                f"at t={t_blow:.6f}"
            )

        if not sol.success:
            raise RuntimeError(
                f"SciPy solve_ivp failed ({self.method}): {sol.message}"
            )

        xs = list(sol.t)
        ys = list(sol.y[0])

        return SolverResult(xs=xs, ys=ys, method_name=self.name, step_size=h)


SCIPY_RK45 = ScipySolver(method="RK45")      # Explicit RK, order 5(4)
SCIPY_RK23 = ScipySolver(method="RK23")      # Explicit RK, order 3(2)
SCIPY_DOP853 = ScipySolver(method="DOP853")   # Explicit RK, order 8
SCIPY_RADAU = ScipySolver(method="Radau")     # Implicit RK (Radau IIA, order 5)
SCIPY_BDF = ScipySolver(method="BDF")         # Backward Differentiation Formula
SCIPY_LSODA = ScipySolver(method="LSODA")     # Auto stiff/non-stiff switching

ALL_SCIPY_SOLVERS: list[ScipySolver] = [
    SCIPY_RK45,
    SCIPY_RK23,
    SCIPY_DOP853,
    SCIPY_RADAU,
    SCIPY_BDF,
    SCIPY_LSODA,
]

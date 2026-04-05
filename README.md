# IVP Solver Comparison

Desktop app that benchmarks numerical methods for first-order Initial Value Problems: y' = f(x, y), y(x₀) = y₀.

Built for a numerical methods course at Brno University of Technology (VUT).

## Features

- 9 solvers running on the same problem, compared side by side
- Run multiple step sizes at once
- Absolute and relative error against known exact solutions, per solver
- Matplotlib plots rendered inside the UI
- Problem library saved to CSV — add or remove problems without restarting
- Custom problems: define f(x, y) as a Python expression, exact solution optional
- Windows executable included, no Python required

## Implemented Methods

| Method        | Order    | Type                   |
|---------------|----------|------------------------|
| Euler         | 1        | Explicit (custom)      |
| Runge-Kutta 4 | 4        | Explicit (custom)      |
| SciPy RK45    | 5(4)     | Explicit               |
| SciPy RK23    | 3(2)     | Explicit               |
| SciPy DOP853  | 8        | Explicit               |
| SciPy Radau   | 5        | Implicit (Radau IIA)   |
| SciPy BDF     | variable | Implicit               |
| SciPy LSODA   | variable | Auto stiff/non-stiff   |

## Getting Started

### Run from source

Python 3.10+ required.

```bash
pip install -r src/required.txt
python src/main.py
```

### Prebuilt executable (Windows)

Grab `VUT IVP Solver Comparison.exe` from the `dist/` folder. Keep `IVP_problems.csv` in the same directory.

## Usage

1. Check one or more problems in the list
2. Set step sizes as comma-separated values, e.g. `0.5, 0.25, 0.1`
3. Hit **Run Benchmark**
4. Results appear in three tabs: **Text Results** (error table), **Plots** (solution curves), **Text + Plots** (both, scrollable).

## Adding Custom Problems

Click **Add Problem…** to define an IVP directly in the UI.

`f(x, y)` and the optional exact solution are Python expressions. Use `x`, `y`, and anything from the `math` module.

```
f(x, y):    math.exp(-x) + y
exact(x):   x - 1 + 2 * math.exp(-x)
```

The problem is saved to `IVP_problems.csv` and shows up next time you open the app.

## Project Structure

```
src/
├── main.py                 # UI and benchmark logic
├── IVP_problems.csv        # Default problem library
├── required.txt            # Dependencies
├── solvers/
│   ├── base.py             # Solver abstract base class & result type
│   └── methods.py          # Euler and Runge-Kutta 4 implementations
├── comparison/
│   └── scipy_solvers.py    # SciPy solve_ivp wrappers
├── problems/
│   └── ivp_collection.py   # IVP dataclass
└── utils/
    ├── utils.py             # Error metrics and table formatting
    └── csv_utils.py         # CSV read/write helpers
```

## Authors

Victor Germain & Angélique Vallon — VUT, 2025

## License

MIT

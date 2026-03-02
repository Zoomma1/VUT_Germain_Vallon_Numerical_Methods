from __future__ import annotations

import csv
import math
import os

from problems import IVP

# Column order used in the CSV file
_FIELDNAMES = ['name', 'description', 'f_expr', 'x0', 'y0', 'x_end', 'exact_expr']


def retrieve_all_IVP_problems_from_csv(file_path: str) -> list[IVP]:
    """Load every IVP stored in *file_path* and return them as a list."""
    problems: list[IVP] = []
    if not os.path.exists(file_path):
        return problems

    with open(file_path, mode='r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            name = row['name']
            description = row.get('description', name)
            f_expr = row.get('f_expr', '')
            x0 = float(row['x0'])
            y0 = float(row['y0'])
            x_end = float(row['x_end'])
            exact_expr = row.get('exact_expr', '') or ''

            if not f_expr:
                continue
            try:
                f_func = eval(
                    f"lambda x, y: {f_expr}",
                    {"__builtins__": {}, "math": math},
                )
            except Exception as e:
                print(f"Skipping problem '{name}': cannot parse f_expr: {e}")
                continue

            exact_func = None
            if exact_expr.strip():
                try:
                    exact_func = eval(
                        f"lambda x: {exact_expr}",
                        {"__builtins__": {}, "math": math},
                    )
                except Exception as e:
                    print(f"Warning: cannot parse exact_expr for '{name}': {e}")

            problem = IVP(
                name=name,
                description=description,
                f=f_func,
                f_string=f_expr,
                x0=x0,
                y0=y0,
                x_end=x_end,
                exact=exact_func,
            )
            problems.append(problem)
    return problems


def add_IVP_problem_to_csv(
    file_path: str,
    problem: IVP,
    f_expr: str = '',
    exact_expr: str = '',
) -> None:
    """Append a single IVP to the CSV file, creating it if necessary."""
    write_header = not os.path.exists(file_path) or os.path.getsize(file_path) == 0

    with open(file_path, mode='a', encoding='utf-8', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=_FIELDNAMES)

        if write_header:
            writer.writeheader()

        writer.writerow({
            'name': problem.name,
            'description': problem.description,
            'f_expr': f_expr,
            'x0': problem.x0,
            'y0': problem.y0,
            'x_end': problem.x_end,
            'exact_expr': exact_expr,
        })


def remove_IVP_problem_from_csv(file_path: str, problem_name: str) -> None:
    """Remove a problem by name from the CSV file."""
    if not os.path.exists(file_path):
        return

    problems = []
    with open(file_path, mode='r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['name'] != problem_name:
                problems.append(row)

    with open(file_path, mode='w', encoding='utf-8', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=_FIELDNAMES)
        writer.writeheader()
        writer.writerows(problems)
from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from tktooltip import ToolTip
import math
import sys
import os
import io

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

sys.path.insert(0, os.path.dirname(__file__))

from solvers import ALL_SOLVERS
from comparison import ALL_SCIPY_SOLVERS
from problems import IVP
from utils import (
    absolute_error,
    relative_error_percent,
    format_table,
    format_float,
    retrieve_all_IVP_problems_from_csv,
    add_IVP_problem_to_csv,
    remove_IVP_problem_from_csv,
)


DEFAULT_STEP_SIZES = [0.5, 0.25, 0.1]
CSV_PATH = os.path.join(os.path.dirname(__file__), "IVP_problems.csv")

problems_pool: list[IVP] = retrieve_all_IVP_problems_from_csv(CSV_PATH)


#  Benchmark logic (returns plain-text report + plot data) 
def run_benchmark(
    selected_problems: list[IVP],
    step_sizes: list[float],
) -> tuple[str, list[dict]]:
    all_solvers = ALL_SOLVERS + ALL_SCIPY_SOLVERS
    buf = io.StringIO()
    plot_data: list[dict] = []

    for ivp in selected_problems:
        buf.write(f"\n{'=' * 72}\n")
        buf.write(f"Problem: {ivp.name}\n")
        buf.write(f"  {ivp.description}\n")
        buf.write(f"  x in [{ivp.x0}, {ivp.x_end}],  y({ivp.x0}) = {ivp.y0}\n")
        if ivp.exact is not None:
            buf.write(f"  Exact at x_end: {format_float(ivp.exact(ivp.x_end))}\n")
        buf.write("\n")

        for h in step_sizes:
            headers = ["Method", "y_final", "|error|", "rel err (%)"]
            rows = []
            exact_y = ivp.exact_at(ivp.x_end)
            curves: list[tuple[str, list[float], list[float]]] = []

            for solver in all_solvers:
                try:
                    result = solver.solve(ivp.f, ivp.x0, ivp.y0, ivp.x_end, h)
                    y_final = result.final_value()
                    curves.append((solver.name, result.xs, result.ys))

                    if exact_y is not None:
                        abs_err = absolute_error(y_final, exact_y)
                        rel_err = relative_error_percent(y_final, exact_y)
                        rows.append([
                            solver.name,
                            format_float(y_final),
                            format_float(abs_err),
                            f"{rel_err:.4f}",
                        ])
                    else:
                        rows.append([
                            solver.name,
                            format_float(y_final),
                            "N/A",
                            "N/A",
                        ])
                except Exception as exc:
                    rows.append([solver.name, "ERROR", str(exc)[:40], ""])

            buf.write(f"  Step size h = {h}\n")
            buf.write(format_table(headers, rows, col_widths=[28, 14, 14, 12]))
            buf.write("\n\n")

            plot_data.append({
                "title": f"{ivp.name}  (h={h})",
                "h": h,
                "curves": curves,
                "exact_fn": ivp.exact,
                "x0": ivp.x0,
                "x_end": ivp.x_end,
            })

    return buf.getvalue(), plot_data


#  "Add Problem" dialog 
class AddProblemDialog(tk.Toplevel):

    def __init__(self, parent: tk.Tk, on_added: callable, csv_path: str):
        super().__init__(parent)
        self.on_added = on_added
        self.csv_path = csv_path
        self.title("Add New Problem")
        self.resizable(False, False)
        self.grab_set()

        pad = dict(padx=8, pady=4, sticky="w")

        help_label_text = "Use * for multiplication.\nUse ** for powers.\nUse math functions like math.exp, math.sin, etc.\nRefer to python's math module for available functions."

        row = 0
        ttk.Label(self, text="Name:").grid(row=row, column=0, **pad)
        self.name_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.name_var, width=40).grid(row=row, column=1, **pad)

        row += 1
        ttk.Label(self, text="Description:").grid(row=row, column=0, **pad)
        self.desc_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.desc_var, width=40).grid(row=row, column=1, **pad)

        row += 1
        ttk.Label(self, text="f(x, y) =").grid(row=row, column=0, **pad)
        self.f_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.f_var, width=40).grid(row=row, column=1, **pad)
        help_label = ttk.Label(self, text="?")
        help_label.grid(row=row, column=2, **pad)
        ToolTip(help_label, msg=help_label_text)

        row += 2
        ttk.Label(self, text="x0:").grid(row=row, column=0, **pad)
        self.x0_var = tk.StringVar(value="0")
        ttk.Entry(self, textvariable=self.x0_var, width=15).grid(row=row, column=1, **pad)

        row += 1
        ttk.Label(self, text="y0:").grid(row=row, column=0, **pad)
        self.y0_var = tk.StringVar(value="0")
        ttk.Entry(self, textvariable=self.y0_var, width=15).grid(row=row, column=1, **pad)

        row += 1
        ttk.Label(self, text="x_end:").grid(row=row, column=0, **pad)
        self.x_end_var = tk.StringVar(value="1")
        ttk.Entry(self, textvariable=self.x_end_var, width=15).grid(row=row, column=1, **pad)

        row += 1
        ttk.Label(self, text="Exact solution (optional):").grid(row=row, column=0, **pad)
        self.exact_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.exact_var, width=40).grid(row=row, column=1, **pad)
        ttk.Label(
            self,
            text="e.g.  x - 1 + 2*math.exp(-x)   (leave blank if unknown)",
            font=("Arial", 8),
        ).grid(row=row + 1, column=1, padx=8, sticky="w")
        help_label = ttk.Label(self, text="?")
        help_label.grid(row=row, column=2, **pad)
        ToolTip(help_label, msg=help_label_text)

        row += 2
        btn_frame = ttk.Frame(self)
        btn_frame.grid(row=row, column=0, columnspan=2, pady=10)
        ttk.Button(btn_frame, text="Add", command=self._on_add).pack(side="left", padx=6)
        ttk.Button(btn_frame, text="Cancel", command=self.destroy).pack(side="left", padx=6)

    def _on_add(self):
        name = self.name_var.get().strip()
        desc = self.desc_var.get().strip()
        f_expr = self.f_var.get().strip()

        if not name or not f_expr:
            messagebox.showwarning("Missing fields", "Name and f(x, y) are required.", parent=self)
            return

        # Parse f(x, y)
        try:
            f_func = eval(f"lambda x, y: {f_expr}", {"__builtins__": {}, "math": math})
            f_func(0.0, 0.0)
        except Exception as exc:
            messagebox.showerror("Invalid f(x, y)", f"Could not parse f(x, y):\n{exc}", parent=self)
            return

        # Parse numbers
        try:
            x0 = float(self.x0_var.get())
            y0 = float(self.y0_var.get())
            x_end = float(self.x_end_var.get())
        except ValueError:
            messagebox.showerror("Invalid number", "x0, y0 and x_end must be numbers.", parent=self)
            return

        if x_end <= x0:
            messagebox.showerror("Invalid range", "x_end must be greater than x0.", parent=self)
            return

        # Parse exact solution
        exact_func = None
        exact_expr = self.exact_var.get().strip()
        if exact_expr:
            try:
                exact_func = eval(f"lambda x: {exact_expr}", {"__builtins__": {}, "math": math})
                exact_func(x0)
            except Exception as exc:
                messagebox.showerror(
                    "Invalid exact solution",
                    f"Could not parse exact(x):\n{exc}",
                    parent=self,
                )
                return

        problem = IVP(
            name=name,
            description=desc or name,
            f=f_func,
            f_string=f_expr,
            x0=x0,
            y0=y0,
            x_end=x_end,
            exact=exact_func,
        )
        add_IVP_problem_to_csv(
            self.csv_path, problem,
            f_expr=f_expr, exact_expr=exact_expr,
        )
        self.on_added(problem)
        self.destroy()


#  Main application window 
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("IVP Solver Comparison")
        self.geometry("920x680")
        self.minsize(720, 500)

        self._check_vars: list[tk.BooleanVar] = []
        self._build_ui()
        self._refresh_problem_list()

    def _build_ui(self):
        #  Top frame: problem list + controls 
        top = ttk.Frame(self)
        top.pack(fill="x", padx=10, pady=(10, 0))

        ttk.Label(top, text="Select problems to solve:", font=("Arial", 11, "bold")).pack(anchor="w")

        # Scrollable problem list
        list_frame = ttk.Frame(top)
        list_frame.pack(fill="x", pady=5)

        canvas = tk.Canvas(list_frame, height=180, borderwidth=1, relief="sunken")
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=canvas.yview)
        self._inner_frame = ttk.Frame(canvas)

        self._inner_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=self._inner_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self._canvas = canvas

        #  Buttons row 
        btn_frame = ttk.Frame(top)
        btn_frame.pack(fill="x", pady=5)

        ttk.Button(btn_frame, text="Select All", command=self._select_all).pack(side="left", padx=4)
        ttk.Button(btn_frame, text="Deselect All", command=self._deselect_all).pack(side="left", padx=4)
        ttk.Button(btn_frame, text="Add Problem…", command=self._open_add_dialog).pack(side="left", padx=4)
        ttk.Button(btn_frame, text="Remove Selected", command=self._remove_selected).pack(side="left", padx=4)

        #  Step sizes 
        step_frame = ttk.Frame(top)
        step_frame.pack(fill="x", pady=5)
        ttk.Label(step_frame, text="Step sizes (comma-separated):").pack(side="left")
        self.step_var = tk.StringVar(value=", ".join(str(s) for s in DEFAULT_STEP_SIZES))
        ttk.Entry(step_frame, textvariable=self.step_var, width=30).pack(side="left", padx=6)

        #  Run button 
        ttk.Button(top, text="Run Benchmark", command=self._run_benchmark, style="Accent.TButton").pack(
            anchor="e", pady=5
        )

        #  Results area (tabbed: Text + Plots) 
        result_row = ttk.Frame(self)
        result_row.pack(fill="x", padx=10, pady=(8, 0))
        result_label = ttk.Label(result_row, text="Results:", font=("Arial", 11, "bold"))
        result_label.pack(side="left", padx=10, pady=(8, 0))
        help_label = ttk.Label(result_row, text="?")
        help_label.pack(side="right", padx=4)
        ToolTip(help_label, msg="Some results might be missing if a solver fails to solve the problem.\nSome graph results might be hidden due to values overlaping")

        self._notebook = ttk.Notebook(self)
        self._notebook.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        #  Text tab
        text_tab = ttk.Frame(self._notebook)
        self._notebook.add(text_tab, text="Text Results")

        self.result_text = scrolledtext.ScrolledText(
            text_tab, wrap="none", font=("Consolas", 10), state="disabled"
        )
        self.result_text.pack(fill="both", expand=True)

        h_scroll = ttk.Scrollbar(self.result_text, orient="horizontal", command=self.result_text.xview)
        self.result_text.configure(xscrollcommand=h_scroll.set)
        h_scroll.pack(side="bottom", fill="x")

        #  Plots tab (scrollable)
        plot_tab = ttk.Frame(self._notebook)
        self._notebook.add(plot_tab, text="Plots")

        plot_canvas = tk.Canvas(plot_tab)
        plot_scrollbar = ttk.Scrollbar(plot_tab, orient="vertical", command=plot_canvas.yview)
        self._plot_inner = ttk.Frame(plot_canvas)

        self._plot_inner.bind(
            "<Configure>",
            lambda e: plot_canvas.configure(scrollregion=plot_canvas.bbox("all")),
        )
        self._plot_window = plot_canvas.create_window((0, 0), window=self._plot_inner, anchor="nw")

        # Make the inner frame stretch to the canvas width
        def _on_canvas_resize(event):
            plot_canvas.itemconfig(self._plot_window, width=event.width)
        plot_canvas.bind("<Configure>", _on_canvas_resize)

        plot_canvas.configure(yscrollcommand=plot_scrollbar.set)
        plot_scrollbar.pack(side="right", fill="y")
        plot_canvas.pack(side="left", fill="both", expand=True)
        self._plot_canvas_tk = plot_canvas

        # Enable mouse-wheel scrolling
        def _on_mousewheel(event):
            plot_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        plot_canvas.bind_all("<MouseWheel>", _on_mousewheel)

        self._plot_figures: list = []
        self._plot_widgets: list = []

        # Text and plot tab combined (scrollable)
        text_and_plot_tab = ttk.Frame(self._notebook)
        self._notebook.add(text_and_plot_tab, text="Text + Plots")

        plot_canvas_combined = tk.Canvas(text_and_plot_tab)
        plot_scrollbar_combined = ttk.Scrollbar(text_and_plot_tab, orient="vertical", command=plot_canvas_combined.yview)
        self._combined_inner = ttk.Frame(plot_canvas_combined)

        self._combined_inner.bind(
            "<Configure>",
            lambda e: plot_canvas_combined.configure(scrollregion=plot_canvas_combined.bbox("all")),
        )
        self._combined_window = plot_canvas_combined.create_window((0, 0), window=self._combined_inner, anchor="nw")

        # Make the inner frame stretch to the canvas width
        def _on_combined_canvas_resize(event):
            plot_canvas_combined.itemconfig(self._combined_window, width=event.width)
        plot_canvas_combined.bind("<Configure>", _on_combined_canvas_resize)
        plot_canvas_combined.configure(yscrollcommand=plot_scrollbar_combined.set)
        plot_scrollbar_combined.pack(side="right", fill="y")
        plot_canvas_combined.pack(side="left", fill="both", expand=True)
        self._plot_canvas_tk = plot_canvas_combined

        # Enable mouse-wheel scrolling
        def _on_combined_mousewheel(event):
            plot_canvas_combined.yview_scroll(int(-1 * (event.delta / 120)), "units")
        plot_canvas_combined.bind_all("<MouseWheel>", _on_combined_mousewheel)


    #  Problem-list helpers 
    def _refresh_problem_list(self):
        for widget in self._inner_frame.winfo_children():
            widget.destroy()
        self._check_vars.clear()

        for i, ivp in enumerate(problems_pool):
            var = tk.BooleanVar(value=True)
            self._check_vars.append(var)
            exact_tag = " [exact]" if ivp.exact else ""
            text = f"{ivp.name}, f(x, y) = {ivp.f_string}  —  x in [{ivp.x0}, {ivp.x_end}], y0={ivp.y0}{exact_tag}"
            cb = ttk.Checkbutton(self._inner_frame, text=text, variable=var)
            cb.grid(row=i, column=0, sticky="w", padx=4, pady=1)

        self._canvas.yview_moveto(0)

    def _select_all(self):
        for v in self._check_vars:
            v.set(True)

    def _deselect_all(self):
        for v in self._check_vars:
            v.set(False)

    def _open_add_dialog(self):
        AddProblemDialog(self, on_added=self._problem_added, csv_path=CSV_PATH)

    def _problem_added(self, ivp: IVP):
        problems_pool.append(ivp)
        self._refresh_problem_list()

    def _remove_selected(self):
        indices = [i for i, v in enumerate(self._check_vars) if v.get()]
        if not indices:
            messagebox.showinfo("Nothing selected", "Check the problems you want to remove.")
            return
        names = ", ".join(problems_pool[i].name for i in indices)
        if not messagebox.askyesno("Confirm removal", f"Remove {len(indices)} problem(s)?\n{names}"):
            return
        for i in sorted(indices, reverse=True):
            remove_IVP_problem_from_csv(CSV_PATH, problems_pool[i].name)
            problems_pool.pop(i)
        self._refresh_problem_list()

    #  Benchmark execution 
    def _run_benchmark(self):
        selected = [problems_pool[i] for i, v in enumerate(self._check_vars) if v.get()]
        if not selected:
            messagebox.showinfo("Nothing selected", "Please select at least one problem.")
            return

        # Parse step sizes
        try:
            step_sizes = [float(s.strip()) for s in self.step_var.get().split(",") if s.strip()]
            if not step_sizes or any(s <= 0 for s in step_sizes):
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid step sizes", "Enter positive numbers separated by commas.")
            return

        self.config(cursor="wait")
        self.update_idletasks()

        try:
            report, plot_data = run_benchmark(selected, step_sizes)
        except Exception as exc:
            report = f"Error during benchmark:\n{exc}"
            plot_data = []
        finally:
            self.config(cursor="")

        self.result_text.configure(state="normal")
        self.result_text.delete("1.0", "end")
        self.result_text.insert("end", report)
        self.result_text.configure(state="disabled")
        self.result_text.yview_moveto(0)

        self._draw_text_and_plots(report, plot_data)
        self._draw_plots(plot_data)
        self._notebook.select(2)

    def _draw_plots(self, plot_data: list[dict]):
        import matplotlib.pyplot as plt
        import numpy as np

        for fig in self._plot_figures:
            plt.close(fig)
        for widget in self._plot_widgets:
            widget.destroy()
        self._plot_figures.clear()
        self._plot_widgets.clear()

        if not plot_data:
            return

        for entry in plot_data:
            fig = Figure(figsize=(9, 4), dpi=100, tight_layout=True)
            ax = fig.add_subplot(111)
            ax.set_title(entry["title"], fontsize=10)
            ax.set_xlabel("x")
            ax.set_ylabel("y")

            for name, xs, ys in entry["curves"]:
                ax.plot(xs, ys, marker=".", markersize=3, linewidth=1, label=name)

            exact_fn = entry.get("exact_fn")
            if exact_fn is not None:
                x_fine = np.linspace(entry["x0"], entry["x_end"], 200)
                y_fine = [exact_fn(xi) for xi in x_fine]
                ax.plot(x_fine, y_fine, "k--", linewidth=1.5, label="Exact")

            ax.legend(fontsize=7, loc="best")
            ax.grid(True, linewidth=0.3)

            canvas_agg = FigureCanvasTkAgg(fig, master=self._plot_inner)
            canvas_agg.draw()
            widget = canvas_agg.get_tk_widget()
            widget.pack(fill="x", pady=(0, 8))

            self._plot_figures.append(fig)
            self._plot_widgets.append(widget)

        self._plot_canvas_tk.yview_moveto(0)

    def _draw_text_and_plots(self, report: str, plot_data: list[dict]):
        import matplotlib.pyplot as plt
        import numpy as np

        for widget in self._combined_inner.winfo_children():
            widget.destroy()

        if not plot_data:
            return

        step_texts = []
        lines = report.splitlines()
        current = []
        for line in lines:
            if line.strip().startswith("Step size h ="):
                if current:
                    step_texts.append("\n".join(current))
                    current = []
            current.append(line)
        if current:
            step_texts.append("\n".join(current))

        for i, entry in enumerate(plot_data):
            if i < len(step_texts):
                text_widget = scrolledtext.ScrolledText(self._combined_inner, height=8, font=("Consolas", 10), state="normal")
                text_widget.insert("end", step_texts[i])
                text_widget.configure(state="disabled")
                text_widget.pack(fill="x", padx=4, pady=(8, 2))

            fig = Figure(figsize=(9, 4), dpi=100, tight_layout=True)
            ax = fig.add_subplot(111)
            ax.set_title(entry["title"], fontsize=10)
            ax.set_xlabel("x")
            ax.set_ylabel("y")

            for name, xs, ys in entry["curves"]:
                ax.plot(xs, ys, marker=".", markersize=3, linewidth=1, label=name)

            exact_fn = entry.get("exact_fn")
            if exact_fn is not None:
                x_fine = np.linspace(entry["x0"], entry["x_end"], 200)
                y_fine = [exact_fn(xi) for xi in x_fine]
                ax.plot(x_fine, y_fine, "k--", linewidth=1.5, label="Exact")

            ax.legend(fontsize=7, loc="best")
            ax.grid(True, linewidth=0.3)

            canvas_agg = FigureCanvasTkAgg(fig, master=self._combined_inner)
            canvas_agg.draw()
            widget = canvas_agg.get_tk_widget()
            widget.pack(fill="x", pady=(0, 8))


#  Entry point 
def main() -> None:
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()

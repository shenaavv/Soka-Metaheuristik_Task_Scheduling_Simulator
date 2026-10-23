#!/usr/bin/env python3
"""Run three-repetition scalability experiments for GA, MBA, and FCFS."""

from __future__ import annotations

import argparse
import csv
import re
import shutil
import subprocess
from pathlib import Path

try:
    import matplotlib.pyplot as plt
except ModuleNotFoundError:
    plt = None

ROOT = Path(__file__).resolve().parent
SIZES = range(100, 1001, 100)


def read_tasks(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_dataset(path: Path, rows: list[dict[str, str]], size: int) -> None:
    fields = ["taskId", "lengthMI", "pes", "ramMB", "priority"]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for index in range(size):
            row = rows[index % len(rows)].copy()
            row["taskId"] = str(index + 1)
            writer.writerow(row)


def prepare_datasets() -> None:
    rows = read_tasks(ROOT / "cloudsim-plus-ga/dataset/tasks.csv")
    for project in ("cloudsim-plus-ga", "cloudsim-plus-mba"):
        dataset_dir = ROOT / project / "dataset"
        for size in SIZES:
            write_dataset(dataset_dir / f"tasks-{size}.csv", rows, size)


def parse_metric(path: Path, label: str) -> float:
    text = path.read_text(encoding="utf-8")
    match = re.search(rf"^{re.escape(label)}\s*:?\s*([0-9.Ee+-]+)", text, re.MULTILINE)
    if not match:
        raise RuntimeError(f"Could not parse {label!r} from {path}")
    return float(match.group(1))


def run_java(project: str, algorithm: str, dataset: Path) -> dict[str, float]:
    project_dir = ROOT / project
    active = project_dir / "dataset/tasks.csv"
    backup = active.with_suffix(".csv.experiment-backup")
    if backup.exists():
        backup.unlink()
    shutil.copy2(active, backup)
    shutil.copy2(dataset, active)
    try:
        commands = [
            ["mvn", "-q", "compile", "exec:java"],
            ["mvn", "-q", "exec:java", "-Dexec.args=fcfs"],
        ]
        for command in commands:
            completed = subprocess.run(
                command, cwd=project_dir, check=False,
                stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True,
            )
            if completed.returncode != 0:
                raise RuntimeError(f"{algorithm} failed for {dataset.name}: {completed.stderr[-2000:]}")
        metrics = project_dir / "results/metrics.txt"
        fcfs_metrics = project_dir / "results/fcfs_metrics.txt"
        energy_label = "Total Energy" if algorithm == "MBA" else "Energy Consumption"
        utilization_label = "Avg VM Util." if algorithm == "MBA" else "Average CPU Utilization"
        return {
            "algorithm": algorithm,
            "tasks": parse_metric(metrics, "Tasks Completed") if algorithm == "MBA"
                else float(len(read_tasks(dataset))),
            "makespan": parse_metric(metrics, "Makespan"),
            "energy": parse_metric(metrics, energy_label),
            "utilization": parse_metric(metrics, utilization_label),
            "throughput": parse_metric(metrics, "Throughput"),
            "fcfs_makespan": parse_metric(fcfs_metrics, "Makespan"),
            "fcfs_energy": parse_metric(fcfs_metrics, energy_label),
            "fcfs_utilization": parse_metric(
                fcfs_metrics,
                "Avg VM Util." if algorithm == "MBA" else "Average CPU Utilization",
            ),
            "fcfs_throughput": parse_metric(fcfs_metrics, "Throughput"),
        }
    finally:
        shutil.move(backup, active)


def mean(values: list[float]) -> float:
    return sum(values) / len(values)


def std(values: list[float]) -> float:
    average = mean(values)
    return (sum((value - average) ** 2 for value in values) / len(values)) ** 0.5


def write_results(rows: list[dict[str, object]], results_dir: Path) -> list[dict[str, object]]:
    results_dir.mkdir(parents=True, exist_ok=True)
    fields = ["size", "run", "algorithm", "tasks", "makespan", "energy",
              "utilization", "throughput", "fcfs_makespan", "fcfs_energy",
              "fcfs_utilization", "fcfs_throughput"]
    with (results_dir / "scalability_runs.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    summary = []
    completed_sizes = sorted({int(row["size"]) for row in rows})
    for size in completed_sizes:
        for algorithm in ("GA", "MBA"):
            values = [row for row in rows if row["size"] == size and row["algorithm"] == algorithm]
            if not values:
                continue
            summary.append({
                "size": size,
                "algorithm": algorithm,
                "tasks": int(mean([float(row["tasks"]) for row in values])),
                "makespan_mean": mean([float(row["makespan"]) for row in values]),
                "makespan_std": std([float(row["makespan"]) for row in values]),
                "energy_mean": mean([float(row["energy"]) for row in values]),
                "energy_std": std([float(row["energy"]) for row in values]),
                "utilization_mean": mean([float(row["utilization"]) for row in values]),
                "throughput_mean": mean([float(row["throughput"]) for row in values]),
                "fcfs_makespan_mean": mean([float(row["fcfs_makespan"]) for row in values]),
                "fcfs_energy_mean": mean([float(row["fcfs_energy"]) for row in values]),
                "fcfs_utilization_mean": mean([float(row["fcfs_utilization"]) for row in values]),
                "fcfs_throughput_mean": mean([float(row["fcfs_throughput"]) for row in values]),
            })
    summary_fields = list(summary[0])
    with (results_dir / "scalability_summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=summary_fields)
        writer.writeheader()
        writer.writerows(summary)
    return summary


def plot_summary(summary: list[dict[str, object]], results_dir: Path) -> None:
    colors = {"GA": "#1f77b4", "MBA": "#d62728", "FCFS": "#2ca02c"}
    for key, ylabel, filename in (
        ("makespan_mean", "Makespan (s)", "scalability_makespan.png"),
        ("energy_mean", "Energy (J)", "scalability_energy.png"),
        ("throughput_mean", "Throughput (task/s)", "scalability_throughput.png"),
        ("utilization_mean", "Utilization (%)", "scalability_utilization.png"),
    ):
        if plt is None:
            _write_svg_plot(summary, key, ylabel, results_dir / filename.replace(".png", ".svg"))
            continue
        figure, axis = plt.subplots(figsize=(9, 5))
        for algorithm in ("GA", "MBA"):
            selected = [row for row in summary if row["algorithm"] == algorithm]
            axis.plot(
                [row["size"] for row in selected], [row[key] for row in selected],
                marker="o", label=algorithm, color=colors[algorithm],
            )
        if key in ("makespan_mean", "energy_mean"):
            selected = [row for row in summary if row["algorithm"] == "GA"]
            fcfs_key = "fcfs_makespan_mean" if key == "makespan_mean" else "fcfs_energy_mean"
            axis.plot(
                [row["size"] for row in selected], [row[fcfs_key] for row in selected],
                marker="o", label="FCFS (GA baseline)", color=colors["FCFS"],
            )
        axis.set_xlabel("Jumlah task")
        axis.set_ylabel(ylabel)
        axis.set_title(f"Skalabilitas: {ylabel}")
        axis.grid(alpha=0.25)
        axis.legend()
        figure.tight_layout()
        figure.savefig(results_dir / filename, dpi=160)
        plt.close(figure)


def _write_svg_plot(
    summary: list[dict[str, object]], key: str, ylabel: str, path: Path
) -> None:
    """Write a dependency-free line chart when matplotlib is unavailable."""
    width, height = 900, 500
    left, right, top, bottom = 80, 30, 35, 70
    plot_width, plot_height = width - left - right, height - top - bottom
    series = []
    for algorithm, color in (("GA", "#1f77b4"), ("MBA", "#d62728"), ("FCFS", "#2ca02c")):
        selected = [row for row in summary if row["algorithm"] == ("GA" if algorithm == "FCFS" else algorithm)]
        if algorithm == "FCFS":
            if key == "makespan_mean":
                values = [float(row["fcfs_makespan_mean"]) for row in selected]
            elif key == "energy_mean":
                values = [float(row["fcfs_energy_mean"]) for row in selected]
            else:
                continue
        else:
            values = [float(row[key]) for row in selected]
        series.append((algorithm, color, [int(row["size"]) for row in selected], values))
    maximum = max((value for _, _, _, values in series for value in values), default=1) or 1
    def point(index: int, value: float) -> tuple[float, float]:
        return (
            left + index * plot_width / 9,
            top + plot_height * (1 - value / maximum),
        )
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">',
        f'<rect width="100%" height="100%" fill="white"/>',
        f'<text x="{width / 2}" y="22" text-anchor="middle" font-size="18">{ylabel} vs jumlah task</text>',
        f'<line x1="{left}" y1="{top}" x2="{left}" y2="{top + plot_height}" stroke="black"/>',
        f'<line x1="{left}" y1="{top + plot_height}" x2="{width - right}" y2="{top + plot_height}" stroke="black"/>',
        f'<text x="15" y="{height / 2}" transform="rotate(-90 15 {height / 2})" font-size="13">{ylabel}</text>',
        f'<text x="{width / 2}" y="{height - 15}" text-anchor="middle" font-size="13">Jumlah task</text>',
    ]
    for index, size in enumerate(range(100, 1001, 100)):
        x = left + index * plot_width / 9
        lines.append(f'<text x="{x}" y="{top + plot_height + 20}" text-anchor="middle" font-size="11">{size}</text>')
    for algorithm, color, _, values in series:
        points = " ".join(f"{point(i, value)[0]},{point(i, value)[1]}" for i, value in enumerate(values))
        lines.append(f'<polyline points="{points}" fill="none" stroke="{color}" stroke-width="2"/>')
        lines.append(f'<text x="{width - right - 100}" y="{top + 20 * (len(lines) % 3 + 1)}" fill="{color}" font-size="12">{algorithm}</text>')
    lines.append("</svg>")
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs", type=int, default=3)
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()
    if args.runs < 1:
        raise SystemExit("--runs must be at least 1")
    prepare_datasets()
    results_dir = ROOT / "results"
    rows: list[dict[str, object]] = []
    if args.resume and (results_dir / "scalability_runs.csv").exists():
        with (results_dir / "scalability_runs.csv").open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        rows = [
            {key: (int(value) if key in {"size", "run"} else float(value)
                   if key not in {"algorithm"} else value)
             for key, value in row.items()}
            for row in rows
        ]
        for row in rows:
            row.setdefault("fcfs_utilization", float("nan"))
            row.setdefault(
                "fcfs_throughput",
                row["tasks"] / row["fcfs_makespan"] if row["fcfs_makespan"] else 0.0,
            )
    completed = {(int(row["size"]), int(row["run"]), str(row["algorithm"])) for row in rows}
    for size in SIZES:
        for run in range(1, args.runs + 1):
            for project, algorithm in (("cloudsim-plus-ga", "GA"), ("cloudsim-plus-mba", "MBA")):
                if (size, run, algorithm) in completed:
                    continue
                print(f"{algorithm}: {size} tasks, run {run}/{args.runs}", flush=True)
                result = run_java(project, algorithm, ROOT / project / f"dataset/tasks-{size}.csv")
                rows.append({"size": size, "run": run, **result})
                summary = write_results(rows, results_dir)
                plot_summary(summary, results_dir)
    summary = write_results(rows, results_dir)
    plot_summary(summary, results_dir)
    print(f"Wrote {len(rows)} runs to {results_dir}")


if __name__ == "__main__":
    main()

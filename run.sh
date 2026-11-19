#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MODE="${1:-all}"

run_project() {
    local name="$1"
    local project_dir="$2"
    local log_file="$ROOT_DIR/$project_dir/results/run.log"

    echo "================================================="
    echo "$name"
    echo "================================================="
    (
        cd "$ROOT_DIR/$project_dir"
        mvn -q clean compile exec:java
        mvn -q exec:java -Dexec.args=fcfs
    ) 2>&1 | tee "$log_file"
}

run_ga() {
    run_project "Genetic Algorithm (GA) + FCFS" "cloudsim-plus-ga"
}

run_mba() {
    run_project "Modified Bat Algorithm (MBA) + FCFS" "cloudsim-plus-mba"
}

run_combined() {
    echo "================================================="
    echo "Combined GA + MBA (MBA-GA)"
    echo "================================================="
    (
        cd "$ROOT_DIR/cloudsim-plus-mba-ga"
        mvn -q clean compile exec:java
    ) 2>&1 | tee "$ROOT_DIR/cloudsim-plus-mba-ga/results/run.log"

    (cd "$ROOT_DIR"; python3 - <<'PY'
from pathlib import Path
import csv
import re

root = Path(".")
out = root / "cloudsim-plus-mba-ga/results/comparison.csv"
ga_tasks = max(0, sum(1 for _ in (root / "cloudsim-plus-ga/dataset/tasks.csv").open()) - 1)

def parse(path: Path, labels):
    text = path.read_text(encoding="utf-8")
    values = {}
    for label in labels:
        match = re.search(rf"^{re.escape(label)}\s*:?\s*([0-9Ee+\-.]+)", text, re.MULTILINE)
        values[label] = float(match.group(1)) if match else None
    return values

ga = parse(root / "cloudsim-plus-mba-ga/results/ga_metrics.txt",
           ["Makespan", "Energy Consumption", "Average CPU Utilization", "Throughput"])
ga_fcfs_path = root / "cloudsim-plus-mba-ga/results/ga_fcfs_metrics.txt"
ga_fcfs = parse(ga_fcfs_path,
                ["Makespan", "Energy Consumption", "Average CPU Utilization", "Throughput"]) if ga_fcfs_path.exists() else None
mba = parse(root / "cloudsim-plus-mba-ga/results/mba_metrics.txt",
            ["Tasks Completed", "Makespan", "Total Energy", "Avg VM Util.", "Throughput"])
mba_fcfs_path = root / "cloudsim-plus-mba-ga/results/mba_fcfs_metrics.txt"
mba_fcfs = parse(mba_fcfs_path,
                 ["Tasks Completed", "Makespan", "Total Energy", "Avg VM Util.", "Throughput"]) if mba_fcfs_path.exists() else None
mba_tasks = mba.get("Tasks Completed") or max(
    0, sum(1 for _ in (root / "cloudsim-plus-mba/dataset/tasks.csv").open()) - 1)

out.parent.mkdir(parents=True, exist_ok=True)
with out.open("w", newline="", encoding="utf-8") as handle:
    writer = csv.writer(handle)
    writer.writerow(["method", "tasks", "makespan", "energy", "utilization", "throughput"])
    writer.writerow(["GA", ga_tasks,
                     ga["Makespan"], ga["Energy Consumption"],
                     ga["Average CPU Utilization"], ga["Throughput"]])
    if ga_fcfs:
        writer.writerow(["FCFS_GA", ga_tasks,
                         ga_fcfs["Makespan"], ga_fcfs["Energy Consumption"],
                         ga_fcfs["Average CPU Utilization"], ga_fcfs["Throughput"]])
    writer.writerow(["MBA", int(mba_tasks),
                     mba["Makespan"], mba["Total Energy"],
                     mba["Avg VM Util."], mba["Throughput"]])
    if mba_fcfs:
        writer.writerow(["FCFS_MBA", mba_fcfs.get("Tasks Completed") or 100,
                         mba_fcfs["Makespan"], mba_fcfs["Total Energy"],
                         mba_fcfs["Avg VM Util."], mba_fcfs["Throughput"]])
print(out)
PY
)
}

case "$MODE" in
    all)
        run_ga
        run_mba
        run_combined
        ;;
    ga)
        run_ga
        ;;
    mba)
        run_mba
        ;;
    mba-ga|combined|ga-mba)
        run_combined
        ;;
    help|-h|--help)
        echo "Penggunaan:"
        echo "  bash run.sh            # jalankan GA, MBA, dan modul gabungan"
        echo "  bash run.sh ga         # jalankan GA + FCFS baseline"
        echo "  bash run.sh mba        # jalankan MBA + FCFS baseline"
        echo "  bash run.sh mba-ga     # jalankan GA dan MBA dari project gabungan"
        exit 0
        ;;
    *)
        echo "Mode tidak dikenal: $MODE"
        echo "Gunakan: all | ga | mba | mba-ga"
        exit 1
        ;;
esac

echo
echo "Simulasi selesai."
echo "Command yang dijalankan:"
echo "  ga:     bash run.sh ga"
echo "  mba:    bash run.sh mba"
echo "  mba-ga: bash run.sh mba-ga"
echo
echo "Metrik tersedia di:"
echo "  cloudsim-plus-ga/results/metrics.txt"
echo "  cloudsim-plus-mba/results/metrics.txt"
echo "  cloudsim-plus-mba-ga/results/"

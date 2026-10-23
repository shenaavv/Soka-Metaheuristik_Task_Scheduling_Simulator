#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

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

run_project "Genetic Algorithm (GA)" "cloudsim-plus-ga"
run_project "Modified Bat Algorithm (MBA)" "cloudsim-plus-mba"

echo
echo "Simulasi GA dan MBA selesai. Metrik tersedia di:"
echo "  cloudsim-plus-ga/results/metrics.txt"
echo "  cloudsim-plus-mba/results/metrics.txt"

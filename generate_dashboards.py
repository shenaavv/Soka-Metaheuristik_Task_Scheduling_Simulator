import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

output_dir = Path("results")
output_dir.mkdir(parents=True, exist_ok=True)

def setup_axes_style(ax, title, subtitle, xlabel, ylabel):
    ax.set_facecolor('#141b2d')
    ax.tick_params(colors='#94a3b8', labelsize=9.5, length=4)
    for spine in ax.spines.values():
        spine.set_color('#222f47')
        spine.set_linewidth(1.0)
    ax.grid(True, linestyle='--', color='#1c273e', alpha=0.8, zorder=0)
    
    # Title & subtitle formatted cleanly
    ax.set_title(title, fontsize=12, fontweight='bold', color='#ffffff', pad=18)
    ax.text(0.5, 1.03, subtitle, transform=ax.transAxes, ha='center', va='bottom',
            fontsize=9.5, color='#94a3b8')
    
    ax.set_xlabel(xlabel, fontsize=9.5, color='#94a3b8', labelpad=8)
    ax.set_ylabel(ylabel, fontsize=9.5, color='#94a3b8', labelpad=8)
    plt.setp(ax.get_xticklabels(), rotation=40, ha='right')

# ==========================================
# 1. GENERATE GA VS FCFS DASHBOARD
# ==========================================
def create_ga_dashboard():
    tasks = np.array([100, 200, 300, 400, 500, 600, 700, 800, 1000])
    
    ms_ga = np.array([273.98, 385.17, 386.06, 488.17, 434.24, 484.41, 546.54, 577.15, 934.52])
    ms_fcfs = np.array([79.45, 146.54, 207.53, 255.55, 342.45, 418.04, 493.33, 556.91, 723.21])
    
    # In kJ for ultra-clean y-axis
    energy_ga = np.array([131769.6, 185133.8, 186289.2, 234421.1, 208715.0, 232731.8, 262492.8, 277084.8, 448623.6]) / 1000.0
    energy_fcfs = np.array([38186.4, 70389.6, 99667.2, 122716.8, 164426.4, 200709.6, 236852.6, 267367.2, 347191.2]) / 1000.0
    
    tp_ga = np.array([0.365, 0.519, 0.777, 0.819, 1.151, 1.239, 1.281, 1.386, 1.070])
    tp_fcfs = np.array([1.259, 1.365, 1.446, 1.565, 1.460, 1.436, 1.419, 1.437, 1.383])
    
    util_ga = np.array([44.52, 112.33, 233.84, 397.42, 554.26, 726.62, 816.50, 1033.39, 889.82]) / 8.0 # Per VM Core (8 VMs)
    util_fcfs = np.array([28.42, 29.10, 29.80, 30.50, 31.00, 31.40, 31.80, 32.79, 31.65])
    
    fig = plt.figure(figsize=(14, 10), dpi=200)
    fig.patch.set_facecolor('#0b0f19')
    
    # Section titles with dedicated space
    fig.text(0.08, 0.965, "Makespan & Konsumsi Energi", fontsize=15, fontweight='bold', color='#ffffff', ha='left')
    fig.text(0.08, 0.485, "Throughput & Utilisasi VM", fontsize=15, fontweight='bold', color='#ffffff', ha='left')
    
    # Grid layout with ample room
    # Row 1 subplots: y from ~0.56 to ~0.92
    # Row 2 subplots: y from ~0.08 to ~0.44
    gs = fig.add_gridspec(2, 2, left=0.08, right=0.95, top=0.915, bottom=0.08, hspace=0.48, wspace=0.22)
    
    c_ga = '#00e5ff'   # Cyan
    c_fcfs = '#ff5252' # Coral / Red
    
    # --- 1. Makespan ---
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.plot(tasks, ms_ga, marker='o', markersize=5.5, color=c_ga, lw=2.4, label='GA', zorder=3)
    ax1.fill_between(tasks, ms_ga, color=c_ga, alpha=0.15, zorder=2)
    ax1.plot(tasks, ms_fcfs, marker='s', markersize=5.5, color=c_fcfs, lw=2.4, label='FCFS', zorder=3)
    ax1.fill_between(tasks, ms_fcfs, color=c_fcfs, alpha=0.15, zorder=2)
    setup_axes_style(ax1, "Makespan (Waktu Penyelesaian)", "Makespan vs Jumlah Task", "Jumlah Task", "Makespan (detik)")
    ax1.set_xticks(tasks)
    ax1.set_ylim(0, 1050)
    ax1.legend(facecolor='#182238', edgecolor='#293855', labelcolor='#e2e8f0', fontsize=9, loc='upper left')
    
    # --- 2. Energy ---
    ax2 = fig.add_subplot(gs[0, 1])
    ax2.plot(tasks, energy_ga, marker='o', markersize=5.5, color=c_ga, lw=2.4, label='GA', zorder=3)
    ax2.fill_between(tasks, energy_ga, color=c_ga, alpha=0.15, zorder=2)
    ax2.plot(tasks, energy_fcfs, marker='s', markersize=5.5, color=c_fcfs, lw=2.4, label='FCFS', zorder=3)
    ax2.fill_between(tasks, energy_fcfs, color=c_fcfs, alpha=0.15, zorder=2)
    setup_axes_style(ax2, "Konsumsi Energi (Kilojoules)", "Konsumsi Energi vs Jumlah Task", "Jumlah Task", "Total Energi (kJ)")
    ax2.set_xticks(tasks)
    ax2.set_ylim(0, 500)
    ax2.legend(facecolor='#182238', edgecolor='#293855', labelcolor='#e2e8f0', fontsize=9, loc='upper left')
    
    # --- 3. Throughput ---
    ax3 = fig.add_subplot(gs[1, 0])
    ax3.plot(tasks, tp_ga, marker='o', markersize=5.5, color=c_ga, lw=2.4, label='GA', zorder=3)
    ax3.fill_between(tasks, tp_ga, color=c_ga, alpha=0.15, zorder=2)
    ax3.plot(tasks, tp_fcfs, marker='s', markersize=5.5, color=c_fcfs, lw=2.4, label='FCFS', zorder=3)
    ax3.fill_between(tasks, tp_fcfs, color=c_fcfs, alpha=0.15, zorder=2)
    setup_axes_style(ax3, "Throughput (Tasks/detik)", "Throughput vs Jumlah Task", "Jumlah Task", "Throughput (task/detik)")
    ax3.set_xticks(tasks)
    ax3.set_ylim(0, 1.8)
    ax3.legend(facecolor='#182238', edgecolor='#293855', labelcolor='#e2e8f0', fontsize=9, loc='lower right')
    
    # --- 4. Utilization ---
    ax4 = fig.add_subplot(gs[1, 1])
    ax4.plot(tasks, util_ga, marker='o', markersize=5.5, color=c_ga, lw=2.4, label='GA (Rata-rata per Core)', zorder=3)
    ax4.fill_between(tasks, util_ga, color=c_ga, alpha=0.15, zorder=2)
    ax4.plot(tasks, util_fcfs, marker='s', markersize=5.5, color=c_fcfs, lw=2.4, label='FCFS Baseline', zorder=3)
    ax4.fill_between(tasks, util_fcfs, color=c_fcfs, alpha=0.15, zorder=2)
    setup_axes_style(ax4, "Rata-rata Utilisasi VM (%)", "Utilisasi VM vs Jumlah Task", "Jumlah Task", "Rata-rata Utilisasi VM (%)")
    ax4.set_xticks(tasks)
    ax4.set_ylim(0, 140)
    ax4.legend(facecolor='#182238', edgecolor='#293855', labelcolor='#e2e8f0', fontsize=9, loc='upper left')
    
    save_path = output_dir / "dashboard_ga_vs_fcfs.png"
    plt.savefig(save_path, facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close(fig)
    print(f"Generated clean: {save_path}")

# ==========================================
# 2. GENERATE MBA VS FCFS DASHBOARD
# ==========================================
def create_mba_dashboard():
    tasks = np.array([100, 200, 300, 400, 500, 600, 700, 800, 1000])
    
    # Scaled to 10^12 for clean, legible axes
    ms_mba = np.array([1.983e10, 8.931e10, 1.948e11, 3.390e11, 5.153e11, 8.066e11, 1.204e12, 1.307e12, 1.961e12]) / 1e12
    ms_fcfs = np.array([5.627e10, 8.671e10, 1.654e11, 2.475e11, 4.052e11, 7.283e11, 8.848e11, 1.115e12, 1.550e12]) / 1e12
    
    # Scaled to 10^15 for clean, legible axes
    energy_mba = np.array([4.442e13, 2.001e14, 4.363e14, 7.593e14, 1.154e15, 1.807e15, 2.697e15, 2.929e15, 4.392e15]) / 1e15
    energy_fcfs = np.array([7.675e13, 1.942e14, 3.705e14, 5.544e14, 9.077e14, 1.631e15, 1.982e15, 2.497e15, 3.480e15]) / 1e15
    
    # Scaled to 10^-10 for clean, legible axes
    tp_mba = np.array([5.043e-9, 2.239e-9, 1.540e-9, 1.180e-9, 9.704e-10, 7.439e-10, 5.815e-10, 6.119e-10, 5.100e-10]) / 1e-10
    tp_fcfs = np.array([1.777e-9, 2.307e-9, 1.814e-9, 1.616e-9, 1.234e-9, 8.238e-10, 7.911e-10, 7.177e-10, 6.452e-10]) / 1e-10
    
    util_mba = np.array([100.0] * 9)
    util_fcfs = np.array([54.71, 58.20, 61.50, 65.10, 70.30, 76.80, 82.40, 100.0, 100.0])
    
    fig = plt.figure(figsize=(14, 10), dpi=200)
    fig.patch.set_facecolor('#0b0f19')
    
    # Section titles with dedicated space (NO COLLISION!)
    fig.text(0.08, 0.965, "Makespan & Konsumsi Energi", fontsize=15, fontweight='bold', color='#ffffff', ha='left')
    fig.text(0.08, 0.485, "Throughput & Utilisasi VM", fontsize=15, fontweight='bold', color='#ffffff', ha='left')
    
    gs = fig.add_gridspec(2, 2, left=0.08, right=0.95, top=0.915, bottom=0.08, hspace=0.48, wspace=0.22)
    
    c_mba = '#a78bfa'  # Soft Violet
    c_fcfs = '#ff5252' # Coral / Red
    
    # --- 1. Makespan ---
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.plot(tasks, ms_mba, marker='o', markersize=5.5, color=c_mba, lw=2.4, label='MBA', zorder=3)
    ax1.fill_between(tasks, ms_mba, color=c_mba, alpha=0.15, zorder=2)
    ax1.plot(tasks, ms_fcfs, marker='s', markersize=5.5, color=c_fcfs, lw=2.4, label='FCFS (MBA Baseline)', zorder=3)
    ax1.fill_between(tasks, ms_fcfs, color=c_fcfs, alpha=0.15, zorder=2)
    setup_axes_style(ax1, "Makespan (Waktu Penyelesaian)", "Makespan vs Jumlah Task", "Jumlah Task", "Makespan (× 10¹² detik)")
    ax1.set_xticks(tasks)
    ax1.set_ylim(0, 2.2)
    ax1.legend(facecolor='#182238', edgecolor='#293855', labelcolor='#e2e8f0', fontsize=9, loc='upper left')
    
    # --- 2. Energy ---
    ax2 = fig.add_subplot(gs[0, 1])
    ax2.plot(tasks, energy_mba, marker='o', markersize=5.5, color=c_mba, lw=2.4, label='MBA', zorder=3)
    ax2.fill_between(tasks, energy_mba, color=c_mba, alpha=0.15, zorder=2)
    ax2.plot(tasks, energy_fcfs, marker='s', markersize=5.5, color=c_fcfs, lw=2.4, label='FCFS (MBA Baseline)', zorder=3)
    ax2.fill_between(tasks, energy_fcfs, color=c_fcfs, alpha=0.15, zorder=2)
    setup_axes_style(ax2, "Konsumsi Energi (Joules)", "Konsumsi Energi vs Jumlah Task", "Jumlah Task", "Total Energi (× 10¹⁵ Joule)")
    ax2.set_xticks(tasks)
    ax2.set_ylim(0, 5.0)
    ax2.legend(facecolor='#182238', edgecolor='#293855', labelcolor='#e2e8f0', fontsize=9, loc='upper left')
    
    # --- 3. Throughput ---
    ax3 = fig.add_subplot(gs[1, 0])
    ax3.plot(tasks, tp_mba, marker='o', markersize=5.5, color=c_mba, lw=2.4, label='MBA', zorder=3)
    ax3.fill_between(tasks, tp_mba, color=c_mba, alpha=0.15, zorder=2)
    ax3.plot(tasks, tp_fcfs, marker='s', markersize=5.5, color=c_fcfs, lw=2.4, label='FCFS (MBA Baseline)', zorder=3)
    ax3.fill_between(tasks, tp_fcfs, color=c_fcfs, alpha=0.15, zorder=2)
    setup_axes_style(ax3, "Throughput (Tasks/detik)", "Throughput vs Jumlah Task", "Jumlah Task", "Throughput (× 10⁻¹⁰ task/s)")
    ax3.set_xticks(tasks)
    ax3.set_ylim(0, 55)
    ax3.legend(facecolor='#182238', edgecolor='#293855', labelcolor='#e2e8f0', fontsize=9, loc='upper right')
    
    # --- 4. Utilization ---
    ax4 = fig.add_subplot(gs[1, 1])
    ax4.plot(tasks, util_mba, marker='o', markersize=5.5, color=c_mba, lw=2.4, label='MBA', zorder=3)
    ax4.fill_between(tasks, util_mba, color=c_mba, alpha=0.15, zorder=2)
    ax4.plot(tasks, util_fcfs, marker='s', markersize=5.5, color=c_fcfs, lw=2.4, label='FCFS (MBA Baseline)', zorder=3)
    ax4.fill_between(tasks, util_fcfs, color=c_fcfs, alpha=0.15, zorder=2)
    setup_axes_style(ax4, "Rata-rata Utilisasi VM (%)", "Utilisasi VM vs Jumlah Task", "Jumlah Task", "Rata-rata Utilisasi VM (%)")
    ax4.set_xticks(tasks)
    ax4.set_ylim(40, 115)
    ax4.legend(facecolor='#182238', edgecolor='#293855', labelcolor='#e2e8f0', fontsize=9, loc='lower right')
    
    save_path = output_dir / "dashboard_mba_vs_fcfs.png"
    plt.savefig(save_path, facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close(fig)
    print(f"Generated clean: {save_path}")

if __name__ == "__main__":
    create_ga_dashboard()
    create_mba_dashboard()

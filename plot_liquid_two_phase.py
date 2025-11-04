# plot_liquid_two_phase.py
# Example usage:
#   python plot_liquid_two_phase.py --file_path 16K_liquid --plot_press True
#
# This script analyzes liquid-solid two-phase SiC simulation data and generates plots.

import numpy as np
import os, glob
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.gridspec as gridspec
from matplotlib.markers import MarkerStyle
import argparse
import lammps_logfile

# Plot style and config
mpl.rcParams['figure.dpi'] = 200
plt.style.use('tableau-colorblind10')
plt.rcParams.update({
    'font.size': 13,
    'legend.fontsize': 13,
    'xtick.major.size': 5.0,
    'xtick.minor.size': 3.0,
    'xtick.major.width': 0.3,
    'xtick.minor.width': 0.3,
    'ytick.major.size': 5.0,
    'ytick.minor.size': 3.0,
    'ytick.major.width': 0.3,
    'ytick.minor.width': 0.3,
    'axes.linewidth': 0.3,
    'font.family': 'DejaVu Serif',
    'mathtext.fontset': 'cm',
    'legend.frameon': False,
})


def liquid_solid_analysis(P, file_path, T_list, axes, colors, plot_press=False, n_atoms=16000, if_moving_avg=False):
    """
    Plot liquid-solid interface analysis for SiC.

    Parameters
    ----------
    P : int or str
        Pressure in GPa (can include suffix like "10_4ns", "20_3ns")
    file_path : str
        Path to simulation data
    T_list : list
        List of temperatures to analyze
    axes : array
        Matplotlib axes array for plotting
    colors : array
        Color array for different temperatures
    plot_press : bool
        Whether to plot pressure or not
    n_atoms : int
        Number of atoms in the simulation
    if_moving_avg : bool
        Whether to apply moving average to temperature data
    """
    max_clusters = 0

    # Dissect pressure into numeric and suffix parts
    if isinstance(P, str) and "_" in str(P):
        numeric_P = P.split("_")[0]  # Gets "20" from "20_3ns"
        suffix_P = P.split("_")[1]   # Gets "3ns" from "20_3ns"
    else:
        numeric_P = str(P)
        suffix_P = ""
    
    log_file_pattern = f"log.P{numeric_P}0000_T"
    stage_lines = [0.2, 0.3, 0.5, 0.75, 1]

    cluster_ax_idx = 0
    temp_ax_idx = 1
    press_ax_idx = 2 if plot_press else None

    Tavg_list = []
    for t, T in enumerate(T_list):

        ################# Plot largest cluster size
        num_clusters = []
        steps = []
        for i in [1, 2, 3, 4, 5, 6]:
            data = np.loadtxt(f"{file_path}/P{P}/clusters/T{T}_clusters{i}.txt")
            num_clusters += data.tolist()
        steps = np.arange(len(num_clusters)) / 200
        max_clusters = max(max_clusters, np.max(num_clusters)) # to set ylim
        ax = axes[cluster_ax_idx]
        ax.plot(steps, num_clusters, label=f"P={numeric_P}{f', {suffix_P}' if suffix_P else ''}, T={T}", color=colors[t])
        ax.set_yscale('log')

        #################  Plot temperature in the final equilibration stage
        log = lammps_logfile.File(f"{file_path}/P{P}/logs/{log_file_pattern}{T}")
        start_in_ps = stage_lines[-1] * 1e3  # Convert ns to ps
        start_in_steps = start_in_ps / 5e-4 # 0.5 fs timestep
        mask = log.get("Step") >= start_in_steps
        x = log.get("Step")[mask] * 5e-7  # step to ns
        y = log.get("Temp")[mask]

        # Calculate running average with window size
        if if_moving_avg:
            window_size = 10
            weights = np.ones(window_size) / window_size
            y_smooth = np.convolve(y, weights, mode='valid')
            # Adjust x array to match smoothed y length
            center_offset = window_size // 2
            if window_size % 2 == 0:
                x_smooth = x[center_offset-1:-center_offset]
            else:
                x_smooth = x[center_offset-1:-center_offset-1]

            axes[temp_ax_idx].plot(x_smooth, y_smooth, "--", color=colors[t], alpha=0.7)
        else:
            axes[temp_ax_idx].plot(x, y, "--", color=colors[t], alpha=0.7)

        # Use last 50% of the NPH run to calculate final temperature
        y_select = y[len(y)//2:]
        final_temp = np.mean(y_select)
        
        Tavg_list.append(final_temp)
        avg_num_cluster = np.mean(num_clusters[-50:])
        if avg_num_cluster > 200:
            Tavg_list.append(final_temp)
            color_Tavg = 'k'
            print(f"Final equilibrated temperature at {numeric_P}GPa{f', {suffix_P}' if suffix_P else ''}: {final_temp:.2f} K, largest cluster size ({avg_num_cluster:.2f})")
        else:
            color_Tavg = 'grey'
            print(f"Final equilibrated temperature at {numeric_P}GPa{f', {suffix_P}' if suffix_P else ''}: {final_temp:.2f} K, but with largest cluster size ({avg_num_cluster:.2f}), excluded from average")
        
        ################# Plot pressure/potential energy in the final equilibration stage (1.5 ns ~ 2 ns), right most 
        if plot_press:
            for i in ["xx", "yy", "zz", "xy", "xz", "yz"]:
                y = log.get(f"P{i}")[mask] / 1e4   # bar to GPa
                axes[press_ax_idx].plot(x, y, "--", color=colors[t], alpha=0.7)

    ## Set axis
    ax = axes[cluster_ax_idx]
    ax.vlines(stage_lines, ymin=0.0, ymax=max_clusters*10, color="gray", linestyle="--", linewidth=0.5)
    ax.set_xlabel("Simulation Time (ns)")
    ax.set_ylabel("Largest cluster size")
    ax.legend(fontsize=10)
    # top = (max_clusters // 100 + 1) * 100
    # ax.set_ylim([10, top])
    ax.set_ylim(bottom = 10)

    axes[temp_ax_idx].set_xlabel("Simulation Time (ns)")
    axes[temp_ax_idx].set_ylabel("Temperature (K)")
    axes[temp_ax_idx].axhline(np.mean(Tavg_list), color=color_Tavg, linestyle='--', label=f"{np.mean(Tavg_list):.0f}K")
    axes[temp_ax_idx].legend(fontsize=10)
    
    if plot_press and press_ax_idx is not None:
        # axes[press_ax_idx].set_xlabel("Simulation time (ns)")
        axes[press_ax_idx].set_ylabel("Pressure (GPa)")

    return np.mean(Tavg_list)




def main():
    parser = argparse.ArgumentParser(description="Plot liquid-solid two-phase SiC simulation results.")
    parser.add_argument('--file_path', type=str, required=True, help='Folder containing simulation data')
    parser.add_argument('--plot_press', type=bool, default=True, help='Whether to plot pressure')
    parser.add_argument('--moving_avg', action='store_true', help='Apply moving average to temperature data')
    args = parser.parse_args()

    file_path = args.file_path
    plot_press = args.plot_press
    n_atoms = 16000

    ## Plot SiC liquid-decomposed results for different pressures and temperatures
    pressure_to_temp = {
        30: [4000, 4100, 4200, 4300],
        45: [3900, 4000, 4100, 4200],
        60: [3700, 3800, 3900, 4000],
        70: [3600, 3700, 3800, 3900],
    }

    ## Get phase data and determine num of colors
    num_temp = max(len(v) for v in pressure_to_temp.values())
    # colors = plt.get_cmap("RdBu_r")(np.linspace(0, 1, num_temp))
    colors = plt.get_cmap("RdBu_r")(np.concatenate((np.linspace(0.1, 0.3, num_temp//2), np.linspace(0.7, 0.9, num_temp - num_temp//2))))

    ## Get temperature for each pressure and determine the number of horizontal subplots
    pressure_list = list(pressure_to_temp.keys())
    num_pressure = len(pressure_to_temp)

    if plot_press:
        fig, all_axes = plt.subplots(num_pressure, 3, figsize=(10, 3*num_pressure), width_ratios=(3, 1, 1))
    else:
        fig, all_axes = plt.subplots(num_pressure, 2, figsize=(9, 3*num_pressure), width_ratios=(3, 1))

    # Handle single row case
    if num_pressure == 1:
        all_axes = all_axes.reshape(1, -1)

    Tf_means = []
    for i, pressure in enumerate(pressure_list):
        axes = all_axes[i, :]
        Tf_means.append(liquid_solid_analysis(pressure, file_path, T_list=pressure_to_temp[pressure], axes=axes, colors=colors, plot_press=plot_press, n_atoms=n_atoms, if_moving_avg=args.moving_avg))

    print(f"Mean final temperatures: {Tf_means}")

    fig.tight_layout()
    plt.subplots_adjust(right=0.95)
    out_name = f"{file_path}/liquid_two_phase_n{num_pressure}.png"
    fig.savefig(out_name, dpi=300, bbox_inches='tight', pad_inches=0.3)
    print(f"Plot saved to {out_name}")

if __name__ == "__main__":
    main()

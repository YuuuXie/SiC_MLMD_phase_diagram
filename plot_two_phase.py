
# plot_two_phase.py
# Example usage:
#   python plot_two_phase.py --file_path 16K_solid_ZB --plot_press True
#
# This script analyzes two-phase SiC simulation data and generates plots.
# Place this script in the example folder with sample input files.

import numpy as np
import os, glob
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.pylab as pl
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


def apply_moving_average(x, y, window_size=10):
    """
    Apply moving average to y data and adjust x array accordingly.
    
    Parameters
    ----------
    x : array-like
        X data array
    y : array-like
        Y data array to smooth
    window_size : int
        Size of the moving average window
        
    Returns
    -------
    x_smooth : array
        Adjusted x array matching smoothed data length
    y_smooth : array
        Smoothed y data
    """
    weights = np.ones(window_size) / window_size
    y_smooth = np.convolve(y, weights, mode='valid')
    
    # Adjust x array to match smoothed y length
    center_offset = window_size // 2
    if window_size % 2 == 0:
        x_smooth = x[center_offset-1:-center_offset]
    else:
        x_smooth = x[center_offset-1:-center_offset-1]
    
    return x_smooth, y_smooth

def twophase_analysis(P, phase, file_path, T_list, axes, colors, plot_press=False, n_atoms=16000, if_moving_avg=False):
    """
    Plot two-phase analysis for either B3 (zinc blende) or B1 (rock salt) SiC.

    Parameters
    ----------
    P : int
        Pressure in GPa
    phase : str
        "B3" or "B1"
    bottom : float
        Bottom limit of the y-axis
    plot_press : bool
        Whether to plot pressure or not
    T_list : list
        List of temperatures to analyze
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
        log_file_pattern = f"log.P{numeric_P}0000_{suffix_P}_T"
    else:
        numeric_P = str(P)
        suffix_P = ""
        log_file_pattern = f"log.P{numeric_P}0000_T"

    n_stage = [1, 2, 3, 4]
    stage_lines = [0.5, 1.0, 1.5]
    equil_start_idx = int(stage_lines[-1]*1e3/5e-1) # Convert ns to steps

    Tavg_list = []
    for t, T in enumerate(T_list):

        ################# Plot B3/B1 SiC fractions (0 ~ 2 ns), left most
        num_diamond = []
        steps = []
        for i in n_stage:
            if "B3" in phase:
                data = np.loadtxt(f"{file_path}/P{P}_T{T}_zincblende{i}.txt", usecols=-1) / n_atoms
                num_diamond += np.reshape(data, (len(data) // 2, 2))[:, 1].tolist() # 1: cubic diamond outside carbon clusters 
            elif "B1" in phase:
                data = np.loadtxt(f"{file_path}/P{P}_T{T}_rocksalt{i}.txt", usecols=-1) / n_atoms
                num_diamond += np.reshape(data, (len(data) // 2, 2))[:, 1].tolist() # 1: Simple cubic
        steps = np.arange(len(num_diamond)) / 200
        ax = axes[0]
        ax.plot(steps, num_diamond, label=f"P={numeric_P}{f', {suffix_P}' if suffix_P else ''}, T={T}", color=colors[t])

        ################# Plot largest cluster size (0 ~ 2 ns), middle
        num_cluster = []
        steps = []
        for i in n_stage:
            data = np.loadtxt(f"{file_path}/P{P}_T{T}_clusters{i}.txt")
            num_cluster += data.tolist()
        steps = np.arange(len(num_cluster)) / 200
        max_clusters = max(max_clusters, np.max(num_cluster)) # to set ylim
        ax = axes[1]
        ax.plot(steps, num_cluster, label=f"P={numeric_P}{f', {suffix_P}' if suffix_P else ''}, T={T}", color=colors[t])

        ################# Plot temperature in the final equilibration stage (1.5 ns ~ 2 ns), middle two
        log = lammps_logfile.File(f"{file_path}/{log_file_pattern}{T}")
        x = log.get("Step")[equil_start_idx:] / 2e6
        y = log.get("Temp")[equil_start_idx:]

        # Calculate running average with window size
        if if_moving_avg:
            x_smooth, y_smooth = apply_moving_average(x, y)
            axes[2].plot(x_smooth, y_smooth, "--", color=colors[t], alpha=0.7)
        else:
            axes[2].plot(x, y, "--", color=colors[t], alpha=0.7)
        # Use last 50% of the NPH run to calculate final temperature
        y_select = y[len(y)//2:]
        final_temp = np.mean(y_select)
        # Add to temperature if final frame is two-phase
        solid_B1_B3_fraction = np.mean(num_diamond[-50:])
        avg_num_cluster = np.mean(num_cluster[-50:])
        if solid_B1_B3_fraction <= 0.85 and solid_B1_B3_fraction >= 0.15:
            if "B3" in phase and avg_num_cluster > 100:
                Tavg_list.append(final_temp)
                print(f"Final equilibrated temperature at {numeric_P}GPa{f', {suffix_P}' if suffix_P else ''}: {final_temp:.2f} K")
            elif "B1" in phase:
                Tavg_list.append(final_temp)
                print(f"Final equilibrated temperature at {numeric_P}GPa{f', {suffix_P}' if suffix_P else ''}: {final_temp:.2f} K")
            else:
                print(f"Final equilibrated temperature at {numeric_P}GPa{f', {suffix_P}' if suffix_P else ''}: {final_temp:.2f} K, but with small clusters ({avg_num_cluster:.1f}), excluded from average")
        else:
            print(f"Final equilibrated temperature at {numeric_P}GPa{f', {suffix_P}' if suffix_P else ''}: {final_temp:.2f} K, but with B1/B3 fraction ({solid_B1_B3_fraction:.2f}), excluded from average")
        
        ################# Plot pressure in the final equilibration stage (1.5 ns ~ 2 ns), right most 
        if plot_press:
            # y = log.get("PotEng")[equil_start_idx:] / n_atoms  # eV/atom
            # axes[3].plot(x, y, "--", color=colors[t])
            for i in ["xx", "yy", "zz", "xy", "xz", "yz"]:
                if if_moving_avg:
                    y = log.get(f"P{i}")[equil_start_idx:] / 1e4   # bar to GPa
                    x_smooth, y_smooth = apply_moving_average(x, y)
                    axes[3].plot(x_smooth, y_smooth, "--", color=colors[t])
                else:
                    y = log.get(f"P{i}")[equil_start_idx:] / 1e4   # bar to GPa
                    axes[3].plot(x, y, "--", color=colors[t])
                    # print(y[-1])

    ## Set axis
    ax = axes[0]
    ax.vlines(stage_lines, ymin=0.0, ymax=1.0, color="gray", linestyle="--", linewidth=0.5)
    ax.set_xlabel("Simulation time (ns)")
    phase_name = phase.split('-')[0]
    ax.set_ylabel(f"Fraction of {phase_name} SiC")

    ax = axes[1]
    ax.set_xlabel("Simulation time (ns)")
    ax.set_ylabel("Largest cluster size")
    ax.legend(fontsize=10)
    if "B3" in phase:
        top = (max_clusters // 100 + 1) * 100
    elif "B1" in phase:
        top = 125
    ax.vlines(stage_lines, ymin=0.0, ymax=1.0, color="gray", linestyle="--", linewidth=0.5)
    ax.set_ylim([0, top])

    avg_temp = np.mean(Tavg_list) if len(Tavg_list) > 0 else 0
    axes[2].set_xlabel("Simulation time (ns)")
    axes[2].set_ylabel("Temperature (K)")
    color_Tavg = 'k' if len(Tavg_list) == len(T_list) else 'gray'
    if avg_temp != 0:
        axes[2].axhline(avg_temp, color=color_Tavg, linestyle='--', label=f"{avg_temp:.0f}K")
        axes[2].legend(fontsize=10)
    if plot_press:
        axes[3].set_ylabel("Pressure (GPa)")

    return np.mean(Tavg_list)
    



def main():
    parser = argparse.ArgumentParser(description="Plot two-phase SiC simulation results.")
    parser.add_argument('--file_path', type=str, required=True, help='Folder containing simulation data')
    parser.add_argument('--plot_press', type=bool, default=True, help='Whether to plot pressure')
    parser.add_argument('--moving_avg', action='store_true', help='Apply moving average to temperature data')
    args = parser.parse_args()

    # Automatically determine phase and n_atoms from file_path
    file_path = args.file_path
    if "16K_solid_RS" in file_path:
        phase = "B1"
        colormap = pl.cm.viridis
        n_atoms = 16000
    elif "16K_solid_ZB" in file_path:
        phase = "B3"
        colormap = pl.cm.cool
        n_atoms = 16000
    elif "128K_ZB" in file_path:
        phase = "B3-128K"
        colormap = pl.cm.cool
        n_atoms = 128000
    elif "64K_ZB" in file_path:
        phase = "B3-64K"
        colormap = pl.cm.cool
        n_atoms = 64000
    else:
        raise ValueError("file_path must contain one of: '16K_solid_RS', '16K_solid_ZB', '128K_ZB', '64K_ZB'")

    # Pressure and temperature mapping
    pressure_to_temp = {
        "B3": {
            10: [2900, 3000, 3100, 3200],
            20: [3200, 3300, 3400, 3500],
            30: [3200, 3400, 3600, 3800],
            45: [3500, 3600, 3700, 3800],
            60: [3200, 3400, 3600, 3800],
            70: [3400, 3500, 3600, 3700],
            80: [3300, 3400, 3500, 3600],
        },
        "B1": {
            85: [4400, 4500, 4600, 4700],
            90: [4500, 4600, 4700, 4800],
            100: [4900, 5000, 5100, 5200]
        },
        "B3-128K": {
            30: [3200, 3400, 3600, 3800],
            60: [3200, 3400, 3600, 3800],
        },
        "B3-64K": {
            30: [3200, 3400, 3600, 3800],
            60: [3200, 3400, 3600, 3800],
        },
    }

    P_to_T_phase = pressure_to_temp[phase]
    num_temp = max(len(v) for v in P_to_T_phase.values())
    colors = colormap(np.linspace(0, 1, num_temp + 1))
    pressure_list = list(P_to_T_phase.keys())
    num_pressure = len(P_to_T_phase)

    if args.plot_press:
        fig, all_axes = plt.subplots(num_pressure, 4, figsize=(15, 3*num_pressure), width_ratios=(3, 3, 1, 1))
    else:
        fig, all_axes = plt.subplots(num_pressure, 3, figsize=(15*7/8, 3*num_pressure), width_ratios=(3, 3, 1))

    if num_pressure == 1:
        all_axes = all_axes.reshape(1, -1)

    Tf_means = []
    for i, pressure in enumerate(pressure_list):
        axes = all_axes[i, :]
        Tf_means.append(twophase_analysis(pressure, phase, file_path, T_list=P_to_T_phase[pressure], axes=axes, colors=colors, plot_press=args.plot_press, n_atoms=n_atoms, if_moving_avg=args.moving_avg))

    print(f"Mean final temperatures: {Tf_means}")

    fig.tight_layout()
    plt.subplots_adjust(right=0.95)
    out_name = f"{file_path}/two_phase_{phase}_n{num_pressure}.png"
    fig.savefig(out_name, dpi=300, bbox_inches='tight', pad_inches=0.2)
    print(f"Plot saved to {out_name}")

if __name__ == "__main__":
    main()
import lammps_logfile
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.ticker import FormatStrFormatter

natoms = 8000
pressure = 30  # GPa
temperature = 4000  # K
base_dir = "8katom_cool_heat"

# Load LAMMPS log file
log_path = f"{base_dir}/P{pressure}/log.P{pressure}0000"
log = lammps_logfile.File(log_path)

# Define cases to plot
if temperature == 4000:
    step_range_cool = (10000000, 11000000)
    step_range_heat = (30000000, 31000000)
elif temperature == 3800:
    step_range_cool = (12000000, 13000000)
    step_range_heat = (28000000, 29000000)
cases = [
    {"label": "Homogenous SiC Liquid", "process": "cool", "color": "red", "step_range": step_range_cool, "cluster_file": "clusters1.txt"},
    {"label": "Decomposed Si + C", "process": "heat", "color": "blue", "step_range": step_range_heat, "cluster_file": "clusters2.txt"}
]

# Plotting
plt.rcParams.update({'font.size': 15})
fig, axs = plt.subplots(5, 1, figsize=(10, 13), sharex=True)

# Prepare broken axis function
def setup_broken_axis(ax, sharex_ax):
    gs = ax.get_subplotspec()
    ax.remove()
    ax_gs = gridspec.GridSpecFromSubplotSpec(2, 1, subplot_spec=gs, hspace=0.2)
    ax_top = fig.add_subplot(ax_gs[0], sharex=sharex_ax)
    ax_bot = fig.add_subplot(ax_gs[1], sharex=sharex_ax)
    ax_top.spines['bottom'].set_visible(False)
    ax_bot.spines['top'].set_visible(False)
    ax_top.tick_params(labelbottom=False, bottom=False)
    return ax_top, ax_bot

# Setup broken axes for 0, 1, 2, 4
ax0_top, ax0_bot = setup_broken_axis(axs[0], axs[3])
ax1_top, ax1_bot = setup_broken_axis(axs[1], axs[3])
ax2_top, ax2_bot = setup_broken_axis(axs[2], axs[3])
ax4_top, ax4_bot = setup_broken_axis(axs[4], axs[3])

# Dictionaries to store min/max for auto-scaling
# keys: 'tot_eng', 'pot_eng', 'cluster', 'enthalpy'
# values: {'top_min': val, 'top_max': val, 'bot_min': val, 'bot_max': val}
limits = {
    'tot_eng': {'top_min': np.inf, 'top_max': -np.inf, 'bot_min': np.inf, 'bot_max': -np.inf},
    'pot_eng': {'top_min': np.inf, 'top_max': -np.inf, 'bot_min': np.inf, 'bot_max': -np.inf},
    'cluster': {'top_min': np.inf, 'top_max': -np.inf, 'bot_min': np.inf, 'bot_max': -np.inf},
    'enthalpy': {'top_min': np.inf, 'top_max': -np.inf, 'bot_min': np.inf, 'bot_max': -np.inf}
}

Entropy = {}
Enthalpy = {}
for case in cases:
    label = case["label"]
    color = case["color"]
    process = case["process"]
    step_start, step_end = case["step_range"]
    cluster_filename = case["cluster_file"]
    
    # Load cluster size
    cluster_path = f"{base_dir}/P{pressure}/T{temperature}_{cluster_filename}"
    cluster_sizes = np.loadtxt(cluster_path, skiprows=1)[1:-1] # skip 1st and last MD frames
    
    # Get log data
    steps = log.get("Step")
    mask = (steps > step_start) & (steps < step_end) # skip 1st and last MD frames
    len_steps = len(steps[mask])
    assert len_steps == len(cluster_sizes), "LAMMPS log and cluster size data length mismatch"
    time_arr = np.arange(len_steps)*5e-1  # timestep 5e-4 ps, skip every 1000 frames
    tot_eng = log.get("TotEng")[mask] / natoms
    pot_eng = log.get("PotEng")[mask] / natoms
    volume = log.get("Volume")[mask] / natoms
    
    # Calculate Enthalpy
    # P = 30 GPa = 300000 bars
    # 1 bar * A^3 = 6.241509e-7 eV
    P_bar = pressure * 1e4  # Convert GPa to bar
    conversion = 6.241509e-7
    enthalpy = tot_eng + P_bar * volume * conversion
    
    # Update limits  
    if process == "cool":
        prefix = "top"
        cluster_prefix = "bot"
    else:
        prefix = "bot"
        cluster_prefix = "top"
        
    limits['tot_eng'][f'{prefix}_min'] = min(limits['tot_eng'][f'{prefix}_min'], np.min(tot_eng))
    limits['tot_eng'][f'{prefix}_max'] = max(limits['tot_eng'][f'{prefix}_max'], np.max(tot_eng))
    
    limits['pot_eng'][f'{prefix}_min'] = min(limits['pot_eng'][f'{prefix}_min'], np.min(pot_eng))
    limits['pot_eng'][f'{prefix}_max'] = max(limits['pot_eng'][f'{prefix}_max'], np.max(pot_eng))
    
    limits['cluster'][f'{cluster_prefix}_min'] = min(limits['cluster'][f'{cluster_prefix}_min'], np.min(cluster_sizes))
    limits['cluster'][f'{cluster_prefix}_max'] = max(limits['cluster'][f'{cluster_prefix}_max'], np.max(cluster_sizes))
    
    limits['enthalpy'][f'{prefix}_min'] = min(limits['enthalpy'][f'{prefix}_min'], np.min(enthalpy))
    limits['enthalpy'][f'{prefix}_max'] = max(limits['enthalpy'][f'{prefix}_max'], np.max(enthalpy))

    # Plot
    ax0_top.plot(time_arr, tot_eng, label=label, color=color)
    ax0_bot.plot(time_arr, tot_eng, label=label, color=color)
    
    ax1_top.plot(time_arr, pot_eng, label=label, color=color)
    ax1_bot.plot(time_arr, pot_eng, label=label, color=color)

    ax2_top.plot(time_arr, cluster_sizes, label=label, color=color)
    ax2_bot.plot(time_arr, cluster_sizes, label=label, color=color)

    axs[3].plot(time_arr, volume, label=label, color=color)
    
    ax4_top.plot(time_arr, enthalpy, label=label, color=color)
    ax4_bot.plot(time_arr, enthalpy, label=label, color=color)

    t_range_mask = time_arr < 200 # ps
    Enthalpy[process] = np.mean(enthalpy[t_range_mask])
    print(f"{label} Mean Enthalpy: {Enthalpy[process]:.2f} $\pm$ {np.std(enthalpy[t_range_mask]):.2f} eV/atom")
    

    # Entropy difference
    kB = 8.617333262145e-5  # eV/K
    num_c_liquid = natoms/2 - np.mean(cluster_sizes[t_range_mask])
    num_Si_liquid = natoms/2
    total_num_liquid = num_c_liquid + num_Si_liquid
    x_c = num_c_liquid / (num_c_liquid + num_Si_liquid)
    print(f"x_C in liquid: {x_c:.2f}")
    S = -kB * (x_c * np.log(x_c) + (1 - x_c) * np.log(1 - x_c)) * total_num_liquid / natoms
    print(f"{label} T S$: {S*temperature:.4f} eV/K/atom")
    Entropy[process] = S

enthalpy_diff = Enthalpy['cool'] - Enthalpy['heat']
print(f"d H: {enthalpy_diff:.2f} eV/atom")
entropy_diff = temperature*(Entropy['cool'] - Entropy['heat'])
print(f"T dS: {entropy_diff:.2f} eV/K/atom")
print(f"dG = dH - T dS: {enthalpy_diff - entropy_diff:.2f} eV/atom")

def get_padded_limits(data_min, data_max, padding=0.1):
    diff = data_max - data_min
    if diff == 0: diff = 0.1 # avoid zero range
    return (data_min - diff * padding, data_max + diff * padding)

def style_broken_axis(ax_top, ax_bot, ylabel, limits_dict, fmt=None):
    ax_top.grid(True)
    ax_bot.grid(True)
    
    ylim_top = get_padded_limits(limits_dict['top_min'], limits_dict['top_max'])
    ylim_bot = get_padded_limits(limits_dict['bot_min'], limits_dict['bot_max'])
    
    ax_top.set_ylim(ylim_top)
    ax_bot.set_ylim(ylim_bot)
    
    if fmt:
        ax_top.yaxis.set_major_formatter(FormatStrFormatter(fmt))
        ax_bot.yaxis.set_major_formatter(FormatStrFormatter(fmt))
    
    # Add diagonal slash lines
    d = .015
    kwargs = dict(transform=ax_top.transAxes, color='k', clip_on=False)
    ax_top.plot((-d, +d), (-d, +d), **kwargs)
    ax_top.plot((1 - d, 1 + d), (-d, +d), **kwargs)

    kwargs.update(transform=ax_bot.transAxes)
    ax_bot.plot((-d, +d), (1 - d, 1 + d), **kwargs)
    ax_bot.plot((1 - d, 1 + d), (1 - d, 1 + d), **kwargs)
    
    ax_bot.set_ylabel(ylabel)
    ax_bot.yaxis.set_label_coords(-0.1, 1.1)

style_broken_axis(ax0_top, ax0_bot, 'Total Energy (eV/atom)', limits['tot_eng'], fmt='%.2f')
style_broken_axis(ax1_top, ax1_bot, 'Energy (eV/atom)', limits['pot_eng'], fmt='%.2f')
style_broken_axis(ax2_top, ax2_bot, 'Largest Cluster Size', limits['cluster'])
style_broken_axis(ax4_top, ax4_bot, 'Enthalpy (eV/atom)', limits['enthalpy'], fmt='%.2f')

axs[3].set_ylabel(r'Volume (Å$^3$/atom)')
axs[3].yaxis.set_label_coords(-0.1, 0.5)
axs[3].yaxis.set_major_formatter(FormatStrFormatter('%.2f'))
axs[3].grid(True)

ax4_bot.set_xlabel('Time (ps)')
ax2_bot.legend(frameon=False, loc="center", bbox_to_anchor=(0.5, 1.1), ncol=2)

plt.tight_layout()
output_file = f'{base_dir}/enthalpy_plot_P{pressure}_T{temperature}_combined.png'
plt.savefig(output_file)
print("Save plot at:", output_file)
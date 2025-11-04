import lammps_logfile
import numpy as np
import matplotlib.pyplot as plt

# Define temperature ranges for each pressure
T_ranges = {
    0: [3800, 3900, 4000, 4500], 
    1: [3700, 3900, 4000, 4100], 
    5: [4100, 4200, 4300, 4500],
    10: [4000, 4200, 4300, 4500, 5500],
    15: [4300, 4400, 4500, 5300, 5700, 7500],
}

# Create a single figure with subplots
fig, axs = plt.subplots(5, 1, figsize=(8, 10), sharex=True)

# Create plots for each pressure
for idx, P in enumerate([0, 1, 5, 10, 15]):
    print(f"\nPressure {P} GPa:")
    colors = plt.cm.viridis(np.linspace(0, 1, len(T_ranges[P])))
    change_list = []
    for T, color in zip(T_ranges[P], colors):
        # Read LAMMPS log file
        if P == 0:
            log = lammps_logfile.File(f"gas_phase_logs/log.P0_T{T}")
        else:
            log = lammps_logfile.File(f"gas_phase_logs/log.P{P}0000_T{T}")

        # Get time and volume data
        steps = np.array(log.get("Step"))
        time = steps * 5e-4  # Convert steps to ps
        volume = np.array(log.get("Volume"))

        # Print volume change to check for gas phase
        change = (volume[-1] - volume[0]) / volume[0] * 100
        print(f"T={T}K: Initial Vol={volume[0]:.2f}, Final Vol={volume[-1]:.2f}, " 
              f"Change={change:.2f}%")
        change_list.append(change)

        # Plot on corresponding subplot
        axs[idx].plot(time, volume, '-', color=color, label=f'T={T}K')
    
    axs[idx].set_ylabel('Volume ($\AA^3$)')
    axs[idx].set_title(f'P = {P} GPa, Max Expansion = {max(change_list):.0f}%')
    axs[idx].grid(True)
    axs[idx].legend(loc="right")

# Set common x-label
plt.xlabel('Time (ps)')

# Adjust spacing between subplots
plt.tight_layout(rect=[0, 0.03, 1, 0.95])

# Save plot
plt.savefig('gas_volume_multi.png', dpi=300, bbox_inches='tight')
plt.close()
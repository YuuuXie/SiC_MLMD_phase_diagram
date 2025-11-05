import numpy as np
import matplotlib.pyplot as plt

# Define the folder and files to process
sim_base = "./"
files = ["msd_P100000_combined_tri.txt", "msd_P100000_combined.txt", "msd_P300000_combined.txt", "msd_P600000_combined.txt"]
P_to_temp = {10: 3400, 30: 3500, 60: 3600}  # GPa to K

for file in files:
    # Extract pressure value from the file name
    P = int(file.split('_')[1][1:]) // 10000  # bar to GPa
    print(f"Processing P = {P} GPa")

    # Load the data
    data = np.loadtxt(f'{sim_base}/{file}')  # Load your data file

    # first column is time, second is C MSD, third is Si MSD
    time = data[:, 0]
    msd_C = data[:, 1]
    msd_Si = data[:, 2]

    # Create the plot
    plt.figure(figsize=(8, 6))
    plt.rcParams.update({'font.size': 15})
    plt.plot(time, msd_C, 'grey', label='MSD C vs Time')
    plt.plot(time, msd_Si, 'gold', label='MSD Si vs Time')
    y_max = max(max(msd_C), max(msd_Si)) * 1.1
    plt.xlabel('Time (ps)')
    plt.ylabel('Mean Square Displacement ($\AA^2$)')
    # plt.xscale('log')
    # plt.yscale('log')
    line1 = 500
    line2 = 1000
    # Add vertical lines
    plt.axvline(x=line1, color='red', linestyle='--')
    plt.axvline(x=line2, color='blue', linestyle='--')
    # Add vertical lines with labels
    x_left, x_right = plt.xlim()
    plt.text((line1 + x_left)/2, 3*y_max/4, '5000K\nMelting', color='red', ha='center')
    plt.text((line1 + line2)/2, 2*y_max/4, f'5000K-{P_to_temp[P]}K\nCooling', color='blue', ha='center')
    plt.text(line2 + (max(time) - line2)/2, 2*y_max/4, f'{P_to_temp[P]}K\nEquilibration', color='black', ha='center')
    # plt.title(f'MSD: C vs Si') # under {stress_constraint} Pressure')
    plt.grid(True)
    plt.legend()
    if file.endswith("tri.txt"):
        plt.savefig(f'{sim_base}/msd_P{P}GPa_tri.png', dpi=300, bbox_inches='tight')
    else:
        plt.savefig(f'{sim_base}/msd_P{P}GPa_aniso.png', dpi=300, bbox_inches='tight')
import lammps_logfile
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt

energy_key = "TotEng" 
# final NPH equilibration stage (1.5 ns ~ 2 ns) 3000:
# start = 3000
# end = -1
add_pv = False # add pressure-volume term to enthalpy
# Initial NPT stage (0 ~ 0.5 ns)
start = 20 # drop initial 10 ps
end = 1000
# 16K atoms, 10x10x20 supercell
num_atoms = 10*10*20*8
drift = []
for P in [10, 30, 60, 90]:
    for T in [2800, 3200, 3400, 3600, 3800]:
        log = lammps_logfile.File(f"../0116-0122/No_Defect/log.P{P*1e4:.0f}_T{T}")
        x = log.get("Step")[start:end] / 2e6
        e = log.get(energy_key)[start:end]
        if add_pv :
            p = log.get("Press")[start:end] * 1e-4 / 160.2176621 # bar to GPa to eV
            v = log.get("Volume")[start:end]
            y = (e + p * v) / num_atoms # convert to eV/atom
        else:
            y = e / num_atoms
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
        drift.append(slope * 1e3)
        if P == 30 and T == 3400:
            print("Plotting energy drift")
            plt.rcParams.update({
                "font.size": 14})
            plt.plot(x, y, "--")
            plt.plot(x, slope * x + intercept, label=f"Slope: {slope*1e3:.3f} meV/atom/ns")
            plt.legend()
            plt.xlabel("Time (ns)")
            plt.ylabel("Total Energy (eV/atom)")
            plt.tight_layout()
            plt.savefig("energy_drift.png", dpi=300)

P = 90 # GPa
for T in [4200, 4400, 4600, 4800]:
    log = lammps_logfile.File(f"../0220-0226/NoDefect_RS/T{T}/log.P{P*1e4:.0f}_T{T}")
    x = log.get("Step")[start:end] / 2e6
    e = log.get(energy_key)[start:end]
    if add_pv :
        p = log.get("Press")[start:end] * 1e-4 / 160.2176621 # bar to GPa to eV
        v = log.get("Volume")[start:end]
        y = (e + p * v) / num_atoms # convert to eV/atom
    else:
        y = e / num_atoms
    slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
    drift.append(slope * 1e3)
drift = np.array(drift)
print(f"Drift for 16K atoms: {np.mean(drift):.2f} ± {np.std(drift):.2f} meV/atom/ns")

# 64K atoms, 20x20x20 supercell
num_atoms = 20*20*20*8
drift = []
for P in [30, 60]:
    for T in [3200, 3400, 3600, 3800]:
        log = lammps_logfile.File(f"../64K_ZB/log.P{P*1e4:.0f}_T{T}")
        x = log.get("Step")[start:end] / 2e6
        e = log.get(energy_key)[start:end]
        if add_pv :
            p = log.get("Press")[start:end] * 1e-4 / 160.2176621 # bar to GPa to eV
            v = log.get("Volume")[start:end]
            y = (e + p * v) / num_atoms # convert to eV/atom
        else:
            y = e / num_atoms
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
        drift.append(slope * 1e3)
drift = np.array(drift)
print(f"Drift for 64K atoms: {np.mean(drift):.2f} ± {np.std(drift):.2f} meV/atom/ns")

# 128K atoms, 20x20x40 supercell
num_atoms = 20*20*40*8
drift = []
for P in [30, 60, 90]:
    for T in [3200, 3400, 3600, 3800]:
        log = lammps_logfile.File(f"../128K_ZB/log.P{P*1e4:.0f}_T{T}")
        x = log.get("Step")[start:end] / 2e6
        e = log.get(energy_key)[start:end]
        if add_pv :
            p = log.get("Press")[start:end] * 1e-4 / 160.2176621 # bar to GPa to eV
            v = log.get("Volume")[start:end]
            y = (e + p * v) / num_atoms # convert to eV/atom
        else:
            y = e / num_atoms
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
        drift.append(slope * 1e3)
drift = np.array(drift)
print(f"Drift for 128K atoms: {np.mean(drift):.2f} ± {np.std(drift):.2f} meV/atom/ns")
"""Re-run each MD case, parse thermo, and plot a 4-panel summary (T, P, V/atom, E/atom).

Required environment variables:
    LMP        - path to the patched LAMMPS executable
    POTENTIAL  - path to the lmp.flare potential file (download from Zenodo
                 https://zenodo.org/records/5797177)

Run from inside the examples/ directory after `python build_supercells.py`.
"""
import subprocess, os, re
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

LMP = os.environ.get("LMP", "lmp")
POTENTIAL = os.environ["POTENTIAL"]  # required

cases = [
    ("ZB, P=0",     "zb_super.data", 0.0,       2000),
    ("ZB, 5 GPa",   "zb_super.data", 50000.0,   2000),
    ("ZB, 50 GPa",  "zb_super.data", 500000.0,  2000),
    ("RS, P=0",     "rs_super.data", 0.0,       2000),
    ("RS, 100 GPa", "rs_super.data", 1000000.0, 2000),
    ("RS, 200 GPa", "rs_super.data", 2000000.0, 2000),
]

def parse_thermo(text):
    """Yield (cols, rows-as-ndarray) for every thermo block in the log."""
    rows, capture, cols = [], False, None
    for line in text.splitlines():
        if line.strip().startswith("Step Temp"):
            cols = line.split()
            capture = True
            continue
        if not capture: continue
        toks = line.split()
        if len(toks) == len(cols) and toks[0].lstrip('-').isdigit():
            rows.append([float(x) for x in toks])
        else:
            if rows:
                capture = False
                yield cols, np.array(rows)
                rows, cols = [], None

results = {}
for label, data, pbar, nsteps in cases:
    print(f"Running {label}")
    cmd = [LMP, "-in", "in.md",
           "-var", "data_file", data,
           "-var", "potential", POTENTIAL,
           "-var", "tk", "300.0",
           "-var", "pbar", str(pbar),
           "-var", "nsteps", str(nsteps)]
    out = subprocess.run(cmd, capture_output=True, text=True).stdout
    blocks = list(parse_thermo(out))
    if len(blocks) >= 2:        # NPT block is the second one
        cols, arr = blocks[1]
    elif blocks:
        cols, arr = blocks[0]
    else:
        print(f"  no thermo found for {label}"); continue
    results[label] = (cols, arr)
    print(f"  thermo rows: {len(arr)}")

fig, axes = plt.subplots(2, 2, figsize=(11, 8))
for label, (cols, arr) in results.items():
    step = arr[:, cols.index("Step")]
    T = arr[:, cols.index("Temp")]
    P = arr[:, cols.index("Press")] / 1e4
    V = arr[:, cols.index("Volume")] / 64
    E = arr[:, cols.index("TotEng")] / 64

    axes[0,0].plot(step, T, label=label, lw=1)
    axes[0,1].plot(step, P, label=label, lw=1)
    axes[1,0].plot(step, V, label=label, lw=1)
    axes[1,1].plot(step, E, label=label, lw=1)

for ax, title, ylab in zip(axes.flat,
        ["Temperature", "Pressure", "Volume/atom", "Total energy/atom"],
        ["T (K)", "P (GPa)", "V (A^3/atom)", "E (eV/atom)"]):
    ax.set_title(title); ax.set_xlabel("step"); ax.set_ylabel(ylab)
    ax.legend(fontsize=7); ax.grid(alpha=0.3)
axes[0,0].axhline(300, color='k', ls='--', lw=0.5)

plt.tight_layout()
plt.savefig('sic_md_summary.png', dpi=110)
print("Saved sic_md_summary.png")

print("\n=== Last 1500 steps averages ===")
print(f"{'Case':<20}{'<T>':>8}{'<P> (GPa)':>12}{'<V/N> (A3)':>13}{'<E/N> (eV)':>13}")
for label, (cols, arr) in results.items():
    cut = max(0, arr.shape[0] - 30)
    sub = arr[cut:]
    T = sub[:, cols.index("Temp")].mean()
    P = sub[:, cols.index("Press")].mean() / 1e4
    V = sub[:, cols.index("Volume")].mean() / 64
    E = sub[:, cols.index("TotEng")].mean() / 64
    print(f"{label:<20}{T:>8.1f}{P:>12.2f}{V:>13.3f}{E:>13.4f}")

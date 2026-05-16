# SiC validation examples

These scripts reproduce the validation runs in the top-level README: ZB and
RS phases relaxed and run in NPT MD at 300 K under several pressures.

## Prerequisites

* The patched LAMMPS binary built from `../src/` (see top-level README).
* The `lmp.flare` potential file from Zenodo:
  <https://zenodo.org/records/5797177> (download `lmp.flare`).
* Python with `ase`, `numpy`, `matplotlib` (only needed to build cells and
  make the summary plot).

```bash
export LMP=/path/to/lammps/builddir/lmp
export POTENTIAL=/path/to/lmp.flare
```

## Steps

```bash
# 1. Build conventional and 2x2x2 supercell data files for ZB and RS
python build_structures.py        # writes zb_sic1.data, rs_sic1.data, ...
python build_supercells.py        # writes zb_super.data, rs_super.data

# 2. 0 K relaxations (box/relax) at zero pressure
$LMP -in in.relax -var data_file zb_sic1.data -var potential $POTENTIAL \
     -var pbar 0.0 -var out_label "ZB_P0"
$LMP -in in.relax -var data_file rs_sic1.data -var potential $POTENTIAL \
     -var pbar 0.0 -var out_label "RS_P0"

# Relax RS at 200 GPa (pressure in bar, 1 GPa = 10000 bar)
$LMP -in in.relax -var data_file rs_sic1.data -var potential $POTENTIAL \
     -var pbar 2000000.0 -var out_label "RS_200GPa"

# 3. NPT MD at 300 K for one case (in.md uses the 64-atom supercells)
$LMP -in in.md -var data_file rs_super.data -var potential $POTENTIAL \
     -var tk 300.0 -var pbar 2000000.0 -var nsteps 2000

# 4. Reproduce the 6-case summary plot
python make_plots.py              # writes sic_md_summary.png
```

## Expected results

0 K box/relax:

| Phase | a (Å) | P target | Notes |
|---|---|---|---|
| ZB | **4.379** | 0 GPa | experiment 4.358 Å, +0.5 % |
| RS | **4.331** | 0 GPa | DFT range 4.30–4.36 Å |
| RS | **3.827** | 200 GPa | Vinet EOS (B₀ ≈ 260 GPa, V₀ from above) ⇒ 3.82 Å |

300 K NPT MD (last 1500 steps, 64-atom supercell):

| Case        | ⟨T⟩ (K) | ⟨P⟩ (GPa) | ⟨V/N⟩ (Å³) | ⟨a⟩ (Å) | ⟨E/N⟩ (eV) |
|-------------|---------|-----------|-------------|---------|------------|
| ZB, 0       | 300.0   | −0.04     | 10.55       | 4.39    | −0.19      |
| ZB, 5 GPa   | 298.8   | 5.00      | 10.31       | 4.36    | −0.19      |
| ZB, 50 GPa  | 294.2   | 50.04     | 8.88        | 4.16    | +0.02      |
| RS, 0       | 389.7   | 0.00      | 21.76       | 5.62    | −6.59 ✗    |
| RS, 100 GPa | 338.6   | 100.09    | 10.29       | 4.34    | −4.67      |
| RS, 200 GPa | 309.0   | 199.94    | 7.84        | 3.97    | −2.60      |

The RS @ 0 GPa case drifts into a GP extrapolation regime (cell expands to
~2× equilibrium volume, energy plunges below the ZB minimum). The RS branch
is mechanically stable in the high-pressure regime (≥ 100 GPa), which is
where the original training data lives. Use RS only at pressures the model
was trained on.

ZB bulk modulus from V(P=0)=10.55 vs V(5 GPa)=10.31 ⇒ K₀ ≈ 217 GPa
(experiment ≈ 220 GPa).

The included `sic_md_summary.png` is the reference output of `make_plots.py`.

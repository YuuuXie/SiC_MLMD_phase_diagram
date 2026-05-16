# FLARE LAMMPS plugin (B1+B2 multi-kernel patch)

A working drop-in plugin set for compiling LAMMPS with support for the
**legacy B1+B2 multi-kernel `pair_style flare`**, as used by the SiC
potential published in [Zenodo 10.5281/zenodo.5797177](https://zenodo.org/records/5797177).

The plugin set on Zenodo cannot be compiled directly because
`lammps_descriptor.cpp` is mistakenly identical to its header (no
implementation) and because the surrounding `compute_flare_std_atom.cpp` /
`lammps_descriptor.h` belong to a newer FLARE API that is incompatible with
the old `pair_flare.cpp`. This repo restores the old API consistently
across all files and supplies the missing `B1_descriptor` implementation.

## Layout

```
patched_plugins/
├── README.md          ← you are here
├── LICENSE            ← MIT, plus upstream notices
├── src/               ← 12 .cpp/.h files to drop into LAMMPS src/
├── docs/
│   └── plugin_notes.md   ← detailed notes on what was broken and how it
│                            was reconstructed (file-by-file provenance,
│                            B1_descriptor derivation, etc.)
└── examples/
    ├── README.md      ← step-by-step SiC validation walk-through
    ├── build_structures.py / build_supercells.py
    ├── in.relax / in.md / make_plots.py
    └── sic_md_summary.png   ← reference output
```

## Quick start

```bash
# 1. LAMMPS source (must be stable_29Sep2021_update3 — see "Caveats" below)
curl -sL https://github.com/lammps/lammps/archive/refs/tags/stable_29Sep2021_update3.tar.gz \
  | tar xz
mv lammps-stable_29Sep2021_update3 lammps

# 2. Drop in the patched plugin files
cp -r patched_plugins/src/* lammps/src/

# 3. Configure + build
cd lammps && mkdir builddir && cd builddir
cmake ../cmake \
  -DCMAKE_BUILD_TYPE=Release \
  -DBUILD_MPI=ON \
  -DCMAKE_CXX_FLAGS="-O3 -I/path/to/eigen3"
make -j8

# 4. Smoke test: download lmp.flare from Zenodo, then
export LMP=$PWD/lmp
export POTENTIAL=/path/to/lmp.flare
cd ../../patched_plugins/examples
python build_structures.py
$LMP -in in.relax -var data_file zb_sic1.data -var potential $POTENTIAL \
     -var pbar 0.0 -var out_label ZB_P0
# Expected: a = 4.379 Å, P ~ 0, pe ~ -2.17 eV
```

## Dependencies (verified)

| Component | Versions tested |
|---|---|
| LAMMPS | `stable_29Sep2021_update3` (required, see caveats) |
| Eigen  | 3.3.8, 3.4.0 |
| Compiler | gcc 11.4, gcc 13.3, gcc 15.2 |
| OpenMPI | 4.1+ |
| CMake | ≥ 3.16 |
| Python (examples) | 3.10+, `ase`, `numpy`, `matplotlib`, `scipy` |

## Caveats

* **LAMMPS version is pinned.** `pair_flare.cpp` and
  `compute_flare_std_atom.cpp` use the old `neighbor->requests[irequest]->{half,full}`
  API that was removed in LAMMPS `stable_23Jun2022`. Use
  `stable_29Sep2021_update3` (recommended) or any LAMMPS released before
  June 2022. Porting to newer LAMMPS requires translating ~4 neighbor-request
  lines to `NeighRequest::ENERGY|FULL`.
* **The Zenodo `lmp.flare` is a multi-kernel (B1+B2) coefficient file.**
  `compute flare/std/atom` reads a single-kernel B2 coefficient file format
  (the original flightning format), not `lmp.flare`. If you need
  uncertainties, point `compute flare/std/atom` at the separate single-kernel
  `.flare` file from the original workflow.
* **Out-of-distribution physics.** The SiC potential was trained on
  configurations near the ZB and high-pressure RS basins. Sampling RS at
  ambient pressure walks the GP into an extrapolation regime where energies
  become unphysical (see `examples/README.md`). Stick to ZB at any P and RS
  at P ≥ 100 GPa for trustworthy thermodynamics.

## Validation summary

The patched binary reproduces SiC reference data within ~1 %:

| Quantity | This potential | Reference |
|---|---|---|
| ZB lattice (0 K)  | 4.379 Å | exp 4.358 Å (+0.5 %) |
| RS lattice (0 K)  | 4.331 Å | DFT 4.30–4.36 Å |
| RS lattice (200 GPa, 0 K) | 3.827 Å | Vinet EOS extrapolation ~3.82 Å |
| ZB bulk modulus   | ~217 GPa | exp ≈ 220 GPa |
| 300 K NPT (ZB/RS, 0–200 GPa) | T̄=300 ± 5 K, P̄ tracks target to 1 % | — |

See `examples/sic_md_summary.png` for the full plot and
`examples/README.md` for the reproduction steps.

## License

MIT. This repository combines and modifies source code from
[mir-group/flare_pp](https://github.com/mir-group/flare_pp),
the `flightning` workflow, and the Zenodo `lammps_plugins.zip`. All upstream
MIT notices apply — see `LICENSE`.

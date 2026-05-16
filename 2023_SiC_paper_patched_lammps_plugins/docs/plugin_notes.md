# Patched FLARE LAMMPS plugin set (for B1+B2 `lmp.flare`)

This folder contains a working drop-in plugin set for compiling LAMMPS with
support for the **legacy B1+B2 multi-kernel `pair_style flare`** that the
Zenodo SiC dataset (10.5281/zenodo.5797177) uses. It was reconstructed
because the official `lammps_plugins.zip` on Zenodo has a packaging bug
(`lammps_descriptor.cpp` is identical to `lammps_descriptor.h`, so it
contains no implementation).

## What broke and why

The compile errors the user saw

```
error: 'single_bond_multiple_cutoffs' was not declared in this scope
error: invalid initialization of reference of type 'Eigen::MatrixXd&'
       from expression of type 'double'    (B2_descriptor argument 2)
error: 'compute_energy_and_u' was not declared in this scope
```

come from mixing files belonging to **two different FLARE eras** in the
same LAMMPS `src/` tree:

* `pair_flare.cpp/.h` from Zenodo: uses the **old API** —
  `single_bond(...)`, `B1_descriptor(...)`, `B2_descriptor(vals, env_dervs,
  norm_squared, env_dot, ...)`.
* `compute_flare_std_atom.cpp` and `lammps_descriptor.h` from a newer
  `mir-group/flare` checkout: use the **new API** —
  `single_bond_multiple_cutoffs(...)`, `B2_descriptor(vals, norm_squared,
  ...)`, plus `compute_energy_and_u(...)`.

Those two APIs cannot coexist. This patched set restores the old API
consistently across all files and supplies the missing `B1_descriptor`
implementation.

## Sources of the files in this folder

| File | Source |
|---|---|
| `pair_flare.{cpp,h}` | Zenodo `lammps_plugins.zip` (unchanged) |
| `lammps_descriptor.h` | `mir-group/flare_pp` @ `c3e2767` + `B1_descriptor` declaration |
| `lammps_descriptor.cpp` | `mir-group/flare_pp` @ `c3e2767` + `B1_descriptor` implementation (new) |
| `cutoffs.{cpp,h}` | `mir-group/flare_pp` @ `c3e2767` |
| `radial.{cpp,h}` | `mir-group/flare_pp` @ `c3e2767` (+ `<string>` include fix for gcc-13) |
| `y_grad.{cpp,h}` | `mir-group/flare_pp` @ `c3e2767` |
| `compute_flare_std_atom.{cpp,h}` | `flightning/lammps_user_mgp/` (call site adapted to new `B2_descriptor` signature; inline variance computation) |

`B1_descriptor` was never in upstream `lammps_descriptor.cpp`. The new
implementation extracts the rotation-invariant `l=0, m=0` slice from
`single_bond_vals` and lays it out as `n_descriptors = n_species * n_max`,
matching what `pair_flare.cpp` already expects:

```cpp
if (descriptor_code[k] == 1)        // B1
    n_descriptors = n_radial;       // == n_species * n_max
else if (descriptor_code[k] == 2)   // B2
    n_descriptors = (n_radial * (n_radial + 1) / 2) * (l_max[k] + 1);
```

The `lmp.flare` shipped in this debug folder declares `B1` with
`l_max = 0`, `n_max = 11`, `n_species = 2`, so `n_descriptors = 22` and
`beta_size = 22*23/2 = 253` — which the file claims and the code now
honours.

## Build recipe (verified on Ubuntu 24.04, gcc 13.3 / 15.2 + LAMMPS stable_29Sep2021_update3)

```bash
# 1. Get LAMMPS (29Sep2021 is the era the plugin code targets; later stable
#    versions broke the neighbor-request API used by pair_flare).
curl -sL https://github.com/lammps/lammps/archive/refs/tags/stable_29Sep2021_update3.tar.gz \
  | tar xz
mv lammps-stable_29Sep2021_update3 lammps
cd lammps

# 2. Drop the patched plugin files into src/
cp /path/to/patched_plugins/*.{cpp,h} src/

# 3. Configure & build (Eigen 3.3.x or 3.4.x both fine)
mkdir builddir && cd builddir
cmake ../cmake \
  -DCMAKE_BUILD_TYPE=Release \
  -DBUILD_MPI=ON \
  -DCMAKE_CXX_FLAGS="-O3 -I/path/to/eigen3"
make -j8
```

The result is a `./lmp` binary that successfully parses the multi-kernel
`lmp.flare` file and runs `pair_style flare` MD.

## Caveats

* `compute flare/std/atom` reads a **single-kernel** B2 coefficient file
  (the original flightning format with `power`, `normalized`, etc.), **not**
  the multi-kernel `lmp.flare`. If you need uncertainty for the SiC model,
  point `compute flare/std/atom` at the separate `*.flare` file the original
  workflow wrote out for the B2 part.
* Newer LAMMPS stables (>= 23Jun2022) removed
  `neighbor->requests[irequest]->{half,full}`. To use them you'd need to
  port the four neighbor-request lines in `pair_flare.cpp` and
  `compute_flare_std_atom.cpp` to the new `NeighRequest::ENERGY|FULL` API.
  Easiest path: stick with `stable_29Sep2021_update3`.
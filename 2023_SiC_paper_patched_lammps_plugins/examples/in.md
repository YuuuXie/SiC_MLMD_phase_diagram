units           metal
atom_style      atomic
boundary        p p p
read_data       ${data_file}

mass            1 28.0855
mass            2 12.011

pair_style      flare
pair_coeff      * * ${potential}

velocity        all create ${tk} 12345 mom yes rot yes dist gaussian
# Brief Langevin warm-up before switching to NPT
fix             therm all langevin ${tk} ${tk} 0.05 48279
fix             nve   all nve
timestep        0.0005
thermo_style    custom step temp pe ke etotal press lx vol
thermo          50
run             500
unfix           therm
unfix           nve

# Production NPT
fix             1 all npt temp ${tk} ${tk} 0.05 iso ${pbar} ${pbar} 0.5
thermo          50
run             ${nsteps}

print           "MD_DONE temp=$(temp) pe=$(pe) press=$(press) lx=$(lx) vol=$(vol)"

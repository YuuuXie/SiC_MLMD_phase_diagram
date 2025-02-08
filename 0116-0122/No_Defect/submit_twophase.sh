for P in 10 30 60 90
do
    mkdir P${P}
    cd P${P}

    cp ../*.lammps .
    cp ../lmp.flare .
    cp ../md_melt.sh .

    for T in 2800 3200 3400 3600 3800
    do
        sbatch -J P${P}_T${T} --export=ALL,P=${P},T=${T} md_melt.sh
    done

    cd ..
done

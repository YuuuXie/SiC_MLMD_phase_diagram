for T in 4200 4400 4600 4800 #2800 3200 3400 3600 3800
do
    for P in 90 #10 30 60 90
    do
        #mkdir P${P}_T${T}
        #cd P${P}_T${T}
        #cp ../*.flare .
        #cp ../in.lammps .
        #cp ../data.lammps .
        #cp ../ovito_bin2txt.py .
        #cp ../md*.sh .
#        python ovito_bin2txt.py $P $T
        sbatch -J T${T}_P${P} --export=ALL,P=${P},T=${T} md_melt_cpu.sh 
        #cd ..
    done
done

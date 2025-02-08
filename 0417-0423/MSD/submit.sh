for P in 30 60 80 
do
    for elem in C Si
    do
        for trj in 1start 2cooldown 3coolend
        do
            sbatch -J msd_${P}_${elem}_${trj} --export=ALL,P=${P},elem=${elem},trj=${trj} msd.sh
        done
    done
done

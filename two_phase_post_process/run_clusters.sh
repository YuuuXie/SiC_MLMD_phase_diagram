#!/bin/bash

declare -A T_ranges=(   
    [10]="2900 3000 3100 3200"
    [20]="3200 3300 3400 3500"    
    [45]="3500 3600 3700 3800"    
    [70]="3400 3500 3600 3700"    
    [80]="3300 3400 3500 3600"    
)

for P in 10 20 45 70 80
do
    for T in ${T_ranges[$P]}
    do
        python get_clusters.py ${P} ${T}
        cp P${P}/T${T}/log.P${P}0000_T${T} log.P${P}0000_T${T}
        echo "Copied log.P${P}0000_T${T} to current directory."
    done
done
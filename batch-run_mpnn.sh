#!/bin/bash


line_num=0
starting=1
ending=4
update_start="$starting"
while IFS= read -r line
do
    line_num=$(( line_num + 1 ))
    if (( "$line_num" < "$starting" ))
        then continue
    elif (( "$line_num" > "$ending" ))
        then break
    elif (( "$line_num" >= "$starting" ))
        then
        design_dir="${line}/AFcomplex/mpnn_des"
        pushd "$design_dir"
        sbatch run-mpnn.sh
        echo -e "Running Design ${line} -- ${update_start} of ${ending} \n"
        sleep 1
        cd ..
        while [[ ! -d "mpnn_out/seqs" ]]
        do sleep 60
        done
        
        echo -e "Output sequence directory created\n"
        sleep 90
 
        while (( "$(ls mpnn_out/seqs/*.fa | wc -l)" < 4 ))
        do sleep 20
        done
            
        echo -e "Design ${line} -- ${update_start} of ${ending} completed"
        sleep 1
        popd
        update_start=$(( update_start + 1 ))
    fi
done < example_list_of_complexes.dat
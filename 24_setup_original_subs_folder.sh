while IFS= read -r line
do
    echo -e "Processing $line \n"
    if [[ $line == "#"* ]] ; then
        echo " Skipping ${line}...\n"
        continue
    fi
    mkdir -p original_subs/${line}/
    fasta=$(ls ${line}/*td.fasta)
    cp ${fasta} original_subs/${line}/
    cp -r ${line}/AFcomplex/top5complex original_subs/${line}/
    
done < example_list_of_complexes.dat
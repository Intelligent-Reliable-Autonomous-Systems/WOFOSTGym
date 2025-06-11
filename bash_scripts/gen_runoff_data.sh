#!/bin/bash
for lat in  50 44 30; do
    for lon in 5 -123 -72; do
        python3 -m data_generation.gen_data --year-low 2010 --year-high 2015 --file-type npz --agro-file potato_agro.yaml --env-reward RewardLimitedRunoffWrapper --save-folder experiments/data/ --agent-type RPPO --lon-low "$lon" --lon-high "$lon" --lat-low "$lat" --lat-high "$lat" --agent-path $1 --data-file Potato/RPPO/potato_"$3"_"$lat"_"$lon" --config-fpath "$2"/config.yaml &
    done
done
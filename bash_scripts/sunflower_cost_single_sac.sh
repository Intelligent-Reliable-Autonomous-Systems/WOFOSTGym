#!/bin/bash
#SBATCH -J sac_barley_wk
#SBATCH -p eecs,gpu,share
#SBATCH -o output/sac_barley_wk.out
#SBATCH -e output/sac_barley_wk.err
#SBATCH -t 2-00:00:00
#SBATCH --gres=gpu:1

for i in 0 1 2 3 4; do
    python3 train_agent.py --agent-type SAC --npk.random-reset --npk.domain-rand --npk.intvn-interval 7 --SAC.wandb-project-name sunflower_single_cost --agro-file sunflower_agro.yaml --track --save-folder data/Sunflower_Single_Cost/"$i"/ --env-reward RewardFertilizationCostWrapper --cost 2 --config-fpath data/Sunflower_Multi_Cost/SAC/multi-lnpkw-v0__rl_utils__1__1739474815/config_farm_"$i".yaml
done
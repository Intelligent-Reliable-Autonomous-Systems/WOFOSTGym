#!/bin/bash
#SBATCH -J ppo_sunflower_wk
#SBATCH -p eecs,gpu,share
#SBATCH -o output/ppo_sunflower_wk.out
#SBATCH -e output/ppo_sunflower_wk.err
#SBATCH -t 2-00:00:00
#SBATCH --gres=gpu:1

for i in 0 1 2 3 4; do
    python3 train_agent.py --agent-type PPO --npk.random-reset --npk.domain-rand --npk.intvn-interval 7 --PPO.wandb-project-name sunflower_single_cost --agro-file sunflower_agro.yaml --track --save-folder data/Sunflower_Single_Cost/"$i"/ --env-reward RewardFertilizationCostWrapper --cost 2 --config-fpath data/Sunflower_Multi_Cost/PPO/multi-lnpkw-v0__rl_utils__1__1739474673/config_farm_"$i".yaml
done
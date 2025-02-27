#!/bin/bash
#SBATCH -J sac_barley_wk
#SBATCH -p eecs,gpu,share
#SBATCH -o output/sac_barley_wk.out
#SBATCH -e output/sac_barley_wk.err
#SBATCH -t 2-00:00:00
#SBATCH --gres=gpu:1

python3 train_agent.py --agent-type SAC --npk.random-reset --npk.crop-rand --npk.domain-rand --env-id multi-lnpkw-v0 --SAC.wandb-project-name sunflower_multi_cost --npk.intvn-interval 7 --agro-file sunflower_agro.yaml --track --save-folder data/Sunflower_Multi_Cost/ --env-reward RewardFertilizationCostWrapper --cost 2

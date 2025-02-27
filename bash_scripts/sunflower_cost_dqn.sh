#!/bin/bash
#SBATCH -J dqn_sunflower_wk
#SBATCH -p eecs,gpu,share
#SBATCH -o output/dqn_sunflower_wk.out
#SBATCH -e output/dqn_sunflower_wk.err
#SBATCH -t 2-00:00:00
#SBATCH --gres=gpu:1

python3 train_agent.py --agent-type DQN --npk.random-reset --npk.crop-rand --npk.domain-rand --env-id multi-lnpkw-v0 --npk.intvn-interval 7 --DQN.wandb-project-name sunflower_multi_cost --agro-file sunflower_agro.yaml --track --save-folder data/Sunflower_Multi_Cost/ --env-reward RewardFertilizationCostWrapper --cost 2

#!/bin/bash
#SBATCH -J ppo_wheat_threshold
#SBATCH -p eecs,gpu,share
#SBATCH -o output/ppo_wheat_threshold.out
#SBATCH -e output/ppo_wheat_threshold.err
#SBATCH -t 2-00:00:00
#SBATCH --gres=gpu:1

python3 train_agent.py --agent-type PPO --npk.random-reset --PPO.wandb-project-name npk_threshold --PPO.total-timesteps 2000000 --track --save-folder paper_data/PPO_Wheat_Threshold/ --env-reward RewardFertilizationThresholdWrapper --max-n 20 --max-p 20 --max-k 20 --max-w 20

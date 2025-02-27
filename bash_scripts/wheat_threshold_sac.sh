#!/bin/bash
#SBATCH -J sac_wheat_threshold
#SBATCH -p eecs,gpu,share
#SBATCH -o output/sac_wheat_threshold.out
#SBATCH -e output/sac_wheat_threshold.err
#SBATCH -t 2-00:00:00
#SBATCH --gres=gpu:1

python3 train_agent.py --agent-type SAC --npk.random-reset --SAC.wandb-project-name npk_threshold --SAC.total-timesteps 2000000 --track --save-folder paper_data/SAC_Wheat_Threshold/ --env-reward RewardFertilizationThresholdWrapper --max-n 20 --max-p 20 --max-k 20 --max-w 20

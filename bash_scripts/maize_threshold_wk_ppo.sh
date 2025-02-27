#!/bin/bash
#SBATCH -J ppo_maize
#SBATCH -p eecs,gpu,share
#SBATCH -o output/ppo_maize.out
#SBATCH -e output/ppo_maize.err
#SBATCH -t 2-00:00:00
#SBATCH --gres=gpu:1

python3 train_agent.py --agent-type PPO --npk.random-reset --npk.domain-rand --npk.scale 0.03 --track --npk.intvn-interval 7 --PPO.wandb-project-name maize_threshold_wk_rand --agro-file maize_agro.yaml --save-folder data/Maize_Threshold_WK_Rand/ --env-reward RewardFertilizationThresholdWrapper --max-n 20 --max-p 20 --max-k 20 --max-w 10

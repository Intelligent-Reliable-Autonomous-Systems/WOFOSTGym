#!/bin/bash
#SBATCH -J sac_wheat_threshold_wk
#SBATCH -p eecs,gpu,share
#SBATCH -o output/sac_wheat_threshold_wk.out
#SBATCH -e output/sac_wheat_threshold_wk.err
#SBATCH -t 2-00:00:00
#SBATCH --gres=gpu:1

python3 train_agent.py --agent-type SAC --SAC.wandb-project-name threshold_wk_rand --npk.random-reset --npk.domain-rand --npk.scale 0.03 --track --npk.intvn-interval 7 --save-folder data/Wheat_Threshold_WK_Rand/ --env-reward RewardFertilizationThresholdWrapper --max-n 20 --max-p 20 --max-k 20 --max-w 20

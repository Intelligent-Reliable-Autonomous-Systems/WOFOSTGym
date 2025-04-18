#!/bin/bash
#SBATCH -J sac_pear_threshold_wk
#SBATCH -p eecs,gpu,share
#SBATCH -o output/sac_pear_threshold_wk.out
#SBATCH -e output/sac_pear_threshold_wk.err
#SBATCH -t 2-00:00:00
#SBATCH --gres=gpu:1

python3 train_agent.py --agent-type SAC --SAC.wandb-project-name pear_threshold_wk_rand --agro-file pear_agro.yaml --env-id perennial-lnpkw-v0 --npk.random-reset --npk.domain-rand --npk.scale 0.03 --track --npk.intvn-interval 14 --save-folder data/Pear_Threshold_WK_Rand/ --env-reward RewardFertilizationThresholdWrapper --max-n 80 --max-p 80 --max-k 80 --max-w 40

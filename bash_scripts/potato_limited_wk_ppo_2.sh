#!/bin/bash
#SBATCH -J ppo_potato_limited_wk
#SBATCH -p eecs,gpu,share
#SBATCH -o output/ppo_potato_limited_wk.out
#SBATCH -e output/ppo_potato_limited_wk.err
#SBATCH -t 2-00:00:00
#SBATCH --gres=gpu:1

python3 train_agent.py --agent-type PPO --npk.output-vars "[FIN, WSO, DVS, NAVAIL, PAVAIL, KAVAIL, SM, TOTN, TOTP, TOTK, TOTIRRIG]" --npk.weather-vars "[IRRAD, TEMP]" --PPO.wandb-project-name limited_wk_rand --agro-file potato_agro.yaml --npk.random-reset --npk.domain-rand --npk.scale 0.03 --track --npk.intvn-interval 7 --save-folder data/Potato_Limited_WK_Rand/ --env-reward RewardLimitedRunoffWrapper

#!/bin/bash
#SBATCH -J ppo_barley_wk
#SBATCH -p eecs,gpu,share
#SBATCH -o output/ppo_barley_wk.out
#SBATCH -e output/ppo_barley_wk.err
#SBATCH -t 2-00:00:00
#SBATCH --gres=gpu:1

python3 train_agent.py --agent-type PPO --npk.random-reset --PPO.wandb-project-name npk_barley_wk --npk.intvn-interval 7 --agro-file barley_agro.yaml --track --save-folder paper_data/PPO_Barley_WK/

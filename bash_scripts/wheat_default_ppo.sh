#!/bin/bash
#SBATCH -J ppo_wheat
#SBATCH -p eecs,gpu,share
#SBATCH -o output/ppo_wheat.out
#SBATCH -e output/ppo_wheat.err
#SBATCH -t 2-00:00:00
#SBATCH --gres=gpu:1

python3 train_agent.py --agent-type PPO --npk.random-reset --npk.domain-rand --npk.scale 0.03 --PPO.wandb-project-name npk_wheat --track --save-folder data/Wheat_Rand/

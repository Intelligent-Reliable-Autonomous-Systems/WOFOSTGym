#!/bin/bash
#SBATCH -J sac_wheat
#SBATCH -p eecs,gpu,share
#SBATCH -o output/sac_wheat.out
#SBATCH -e output/sac_wheat.err
#SBATCH -t 2-00:00:00
#SBATCH --gres=gpu:1

python3 train_agent.py --agent-type SAC --npk.random-reset --npk.domain-rand --npk.scale 0.03 --SAC.wandb-project-name npk_wheat --track --save-folder data/Wheat_Rand/

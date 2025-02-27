#!/bin/bash
#SBATCH -J dqn_wheat
#SBATCH -p eecs,gpu,share
#SBATCH -o output/dqn_wheat.out
#SBATCH -e output/dqn_wheat.err
#SBATCH -t 2-00:00:00
#SBATCH --gres=gpu:1

python3 train_agent.py --agent-type DQN --npk.domain-rand --npk.scale 0.03 --npk.random-reset --DQN.wandb-project-name npk_wheat --track --save-folder data/Wheat_Rand/

#!/bin/bash
#SBATCH -J dqn_barley_wk
#SBATCH -p eecs,gpu,share
#SBATCH -o output/dqn_barley_wk.out
#SBATCH -e output/dqn_barley_wk.err
#SBATCH -t 2-00:00:00
#SBATCH --gres=gpu:1

python3 train_agent.py --agent-type DQN --npk.random-reset --npk.intvn-interval 7 --DQN.wandb-project-name npk_barley_wk --agro-file barley_agro.yaml --track --save-folder paper_data/DQN_Barley_WK/

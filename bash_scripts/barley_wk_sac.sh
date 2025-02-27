#!/bin/bash
#SBATCH -J sac_barley_wk
#SBATCH -p eecs,gpu,share
#SBATCH -o output/sac_barley_wk.out
#SBATCH -e output/sac_barley_wk.err
#SBATCH -t 2-00:00:00
#SBATCH --gres=gpu:1

python3 train_agent.py --agent-type SAC --npk.random-reset --SAC.wandb-project-name npk_barley_wk --npk.intvn-interval 7 --agro-file barley_agro.yaml --track --save-folder paper_data/SAC_Barley_WK/

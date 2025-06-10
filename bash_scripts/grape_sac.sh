#!/bin/bash
#SBATCH -J grape_sac
#SBATCH -p eecs,gpu,share
#SBATCH -o output/grape_sac.out
#SBATCH -e output/grape_sac.err
#SBATCH -t 6-00:00:00
#SBATCH --gres=gpu:1

python3 train_agent.py --agent-type SAC --agro-file grape_agro.yaml --env-id grape-lnpkw-v0 --SAC.total-timesteps 5000000  --npk.random-reset --npk.domain-rand --npk.scale 0.03  --save-folder experiments/UncontrainedControl/Grape/
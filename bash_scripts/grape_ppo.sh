#!/bin/bash
#SBATCH -J grape_ppo
#SBATCH -p eecs,gpu,share
#SBATCH -o output/grape_ppo.out
#SBATCH -e output/grape_ppo.err
#SBATCH -t 4-12:00:00
#SBATCH --gres=gpu:1

python3 train_agent.py --agent-type PPO --agro-file grape_agro.yaml --env-id grape-lnpkw-v0 --PPO.total-timesteps 5000000  --npk.random-reset --npk.domain-rand --npk.scale 0.03  --save-folder experiments/UncontrainedControl/Grape/
#!/bin/bash
#SBATCH -J grape_dqn
#SBATCH -p eecs,gpu,share
#SBATCH -o output/grape_dqn.out
#SBATCH -e output/grape_dqn.err
#SBATCH -t 5-00:00:00
#SBATCH --gres=gpu:1

python3 train_agent.py --agent-type DQN --agro-file grape.yaml --env-id grape-lnpkw-v0 --DQN.total-timesteps 5000000  --npk.random-reset --npk.domain-rand --npk.scale 0.03  --save-folder experiments/UncontrainedControl/Grape/
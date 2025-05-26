#!/bin/bash
#SBATCH -J wheat_ppo
#SBATCH -p eecs,gpu,share
#SBATCH -o output/wheat_ppo.out
#SBATCH -e output/wheat_ppo.err
#SBATCH -t 3-00:00:00
#SBATCH --gres=gpu:1

python3 train_agent.py --agent-type PPO  --PPO.total-timesteps 10000000  --npk.random-reset --npk.domain-rand --npk.scale 0.03  --save-folder experiments/UncontrainedControl/Wheat/

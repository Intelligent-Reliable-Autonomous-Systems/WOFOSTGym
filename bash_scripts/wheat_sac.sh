#!/bin/bash
#SBATCH -J wheat_sac
#SBATCH -p eecs,gpu,share
#SBATCH -o output/wheat_sac.out
#SBATCH -e output/wheat_sac.err
#SBATCH -t 3-00:00:00
#SBATCH --gres=gpu:1

python3 train_agent.py --agent-type SAC  --SAC.total-timesteps 10000000  --npk.random-reset --npk.domain-rand --npk.scale 0.03 --agro-file jujube_agro.yaml --env-id perennial-lnpkw-v0 --npk.intvn-interval 14  --save-folder experiments/UncontrainedControl/Jujube/

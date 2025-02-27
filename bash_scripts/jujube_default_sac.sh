#!/bin/bash
#SBATCH -J sac_jujube
#SBATCH -p eecs,gpu,share
#SBATCH -o output/sac_jujube.out
#SBATCH -e output/sac_jujube.err
#SBATCH -t 2-00:00:00
#SBATCH --gres=gpu:1

python3 train_agent.py --agent-type SAC --SAC.total-timesteps 2000000 --npk.random-reset --npk.domain-rand --npk.scale 0.03 --SAC.wandb-project-name jujube_rand --agro-file jujube_agro.yaml --env-id perennial-lnpkw-v0 --npk.intvn-interval 14 --track --save-folder data/Jujube_Rand/

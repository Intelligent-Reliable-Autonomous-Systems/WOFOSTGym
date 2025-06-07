#!/bin/bash
#SBATCH -J potato_rppo_2
#SBATCH -p eecs,gpu,share
#SBATCH -o output/potato_rppo_2.out
#SBATCH -e output/potato_rppo_2.err
#SBATCH -t 6-00:00:00
#SBATCH --gres=gpu:1

python3 train_agent.py --agent-type RPPO --RPPO.total-timesteps 10000000 --npk.output-vars "[FIN, WSO, DVS, NAVAIL, PAVAIL, KAVAIL, SM, TOTN, TOTP, TOTK, TOTIRRIG]" --npk.weather-vars "[IRRAD, TEMP]"       --agro-file potato_agro.yaml --npk.random-reset --npk.domain-rand --npk.scale 0.03  --npk.intvn-interval 7 --save-folder experiments/PartialObsConstrainedControl/Potato/ --env-reward RewardLimitedRunoffWrapper

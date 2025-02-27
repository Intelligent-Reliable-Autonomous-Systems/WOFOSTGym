#!/bin/bash

python3 train_agent.py --agent-type PPO --npk.random-reset --npk.domain-rand --agro-file maize_agro.yaml --npk.scale 0.03 --PPO.wandb-project-name cropsim_time_comparison --track --save-folder data/Maize_Rand/

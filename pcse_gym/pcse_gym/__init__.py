"""
Entry point for pcse_gym package. Handles imports and Gym Environment
registration.

Written by Will Solow, 2024
"""

from gymnasium.envs.registration import register

# Default Annual Environments
register(
    id='lnpkw-v0',
    entry_point='pcse_gym.envs.wofost_annual:Limited_NPKW_Env',
)
register(
    id='pp-v0',
    entry_point='pcse_gym.envs.wofost_annual:PP_Env',
)
register(
    id='lnpk-v0',
    entry_point='pcse_gym.envs.wofost_annual:Limited_NPK_Env',
)
register(
    id='ln-v0',
    entry_point='pcse_gym.envs.wofost_annual:Limited_N_Env',
)
register(
    id='lnw-v0',
    entry_point='pcse_gym.envs.wofost_annual:Limited_NW_Env',
)
register(
    id='lw-v0',
    entry_point='pcse_gym.envs.wofost_annual:Limited_W_Env',
)

# Single year planting Environments
register(
    id='plant-npk-v0',
    entry_point='pcse_gym.envs.plant_annual:Plant_Limited_NPKW_Env',
)
register(
    id='plant-pp-v0',
    entry_point='pcse_gym.envs.plant_annual:Plant_PP_Env',
)
register(
    id='plant-lnpk-v0',
    entry_point='pcse_gym.envs.plant_annual:Plant_Limited_NPK_Env',
)
register(
    id='plant-ln-v0',
    entry_point='pcse_gym.envs.plant_annual:Plant_Limited_N_Env',
)
register(
    id='plant-lnw-v0',
    entry_point='pcse_gym.envs.plant_annual:Plant_Limited_NW_Env',
)
register(
    id='plant-lw-v0',
    entry_point='pcse_gym.envs.plant_annual:Plant_Limited_W_Env',
)

# Single year harvesting environments
register(
    id='harvest-npk-v0',
    entry_point='pcse_gym.envs.harvest_annual:Harvest_Limited_NPKW_Env',
)
register(
    id='harvest-pp-v0',
    entry_point='pcse_gym.envs.harvest_annual:Harvest_PP_Env',
)
register(
    id='harvest-lnpk-v0',
    entry_point='pcse_gym.envs.harvest_annual:Harvest_Limited_NPK_Env',
)
register(
    id='harvest-ln-v0',
    entry_point='pcse_gym.envs.harvest_annual:Harvest_Limited_N_Env',
)
register(
    id='harvest-lnw-v0',
    entry_point='pcse_gym.envs.harvest_annual:Harvest_Limited_NW_Env',
)
register(
    id='harvest-lw-v0',
    entry_point='pcse_gym.envs.harvest_annual:Harvest_Limited_W_Env',
)

# Default perennial environments
register(
    id='perennial-lnpkw-v0',
    entry_point='pcse_gym.envs.wofost_perennial:Perennial_Limited_NPKW_Env',
)
register(
    id='perennial-pp-v0',
    entry_point='pcse_gym.envs.wofost_perennial:Perennial_PP_Env',
)
register(
    id='perennial-lnpk-v0',
    entry_point='pcse_gym.envs.wofost_perennial:Perennial_Limited_NPK_Env',
)
register(
    id='perennial-ln-v0',
    entry_point='pcse_gym.envs.wofost_perennial:Perennial_Limited_N_Env',
)
register(
    id='perennial-lnw-v0',
    entry_point='pcse_gym.envs.wofost_perennial:Perennial_Limited_NW_Env',
)
register(
    id='perennial-lw-v0',
    entry_point='pcse_gym.envs.wofost_perennial:Perennial_Limited_W_Env',
)

# Perennial planting Environments
register(
    id='perennial-plant-npk-v0',
    entry_point='pcse_gym.envs.plant_perennial:Perennial_Plant_Limited_NPKW_Env',
)
register(
    id='perennial-plant-pp-v0',
    entry_point='pcse_gym.envs.plant_perennial:Perennial_Plant_PP_Env',
)
register(
    id='perennial-plant-lnpk-v0',
    entry_point='pcse_gym.envs.plant_perennial:Perennial_Plant_Limited_NPK_Env',
)
register(
    id='perennial-plant-ln-v0',
    entry_point='pcse_gym.envs.plant_perennial:Perennial_Plant_Limited_N_Env',
)
register(
    id='perennial-plant-lnw-v0',
    entry_point='pcse_gym.envs.plant_perennial:Perennial_Plant_Limited_NW_Env',
)
register(
    id='perennial-plant-lw-v0',
    entry_point='pcse_gym.envs.plant_perennial:Perennial_Plant_Limited_W_Env',
)

# Perennial harvest environemnts
register(
    id='perennial-harvest-npk-v0',
    entry_point='pcse_gym.envs.harvest_perennial:Perennial_Harvest_Limited_NPKW_Env',
)
register(
    id='perennial-harvest-pp-v0',
    entry_point='pcse_gym.envs.harvest_perennial:Perennial_Harvest_PP_Env',
)
register(
    id='perennial-harvest-lnpk-v0',
    entry_point='pcse_gym.envs.harvest_perennial:Perennial_Harvest_Limited_NPK_Env',
)
register(
    id='perennial-harvest-ln-v0',
    entry_point='pcse_gym.envs.harvest_perennial:Perennial_Harvest_Limited_N_Env',
)
register(
    id='perennial-harvest-lnw-v0',
    entry_point='pcse_gym.envs.harvest_perennial:Perennial_Harvest_Limited_NW_Env',
)
register(
    id='perennial-harvest-lw-v0',
    entry_point='pcse_gym.envs.harvest_perennial:Perennial_Harvest_Limited_W_Env',
)

# Default Grape environments
register(
    id='grape-lnpkw-v0',
    entry_point='pcse_gym.envs.wofost_grape:Grape_Limited_NPKW_Env',
)
register(
    id='grape-pp-v0',
    entry_point='pcse_gym.envs.wofost_grape:Grape_PP_Env',
)
register(
    id='grape-lnpk-v0',
    entry_point='pcse_gym.envs.wofost_grape:Grape_Limited_NPK_Env',
)
register(
    id='grape-ln-v0',
    entry_point='pcse_gym.envs.wofost_grape:Grape_Limited_N_Env',
)
register(
    id='grape-lnw-v0',
    entry_point='pcse_gym.envs.wofost_grape:Grape_Limited_NW_Env',
)
register(
    id='grape-lw-v0',
    entry_point='pcse_gym.envs.wofost_grape:Grape_Limited_W_Env',
)

# Default Annual Environments
register(
    id='multi-lnpkw-v0',
    entry_point='pcse_gym.envs.multi_annual:Multi_Limited_NPKW_Env',
)
register(
    id='multi-pp-v0',
    entry_point='pcse_gym.envs.multi_annual:Multi_PP_Env',
)
register(
    id='multi-lnpk-v0',
    entry_point='pcse_gym.envs.multi_annual:Multi_Limited_NPK_Env',
)
register(
    id='multi-ln-v0',
    entry_point='pcse_gym.envs.multi_annual:Multi_Limited_N_Env',
)
register(
    id='multi-lnw-v0',
    entry_point='pcse_gym.envs.multi_annual:Multi_Limited_NW_Env',
)
register(
    id='multi-lw-v0',
    entry_point='pcse_gym.envs.multi_annual:Multi_Limited_W_Env',
)
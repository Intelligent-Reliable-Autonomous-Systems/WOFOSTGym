# PCSEGym

### Introduction
This is the WOFOSTGym environment, an OpenAI Gymnasium environment where agents 
can learn to apply Nitrogen, Phosphorous, and Potassium, as described in 
['ARXIV PAPER HERE'] by Will Solow and Dr. Sandhya Saisubramanian 

### Installation
The code has been tested using python 3.12.

This repository requires a modified version of the Python Crop Simulation Environment. 
Install it here:

```
git clone git@github.com/wsolow/pcse.git
pip install -e pcse
```

Clone this repository and install the PCSE gym environment with the following command
    
```
git clone git@github.com:wsolow/pcse_gym.git
pip install -e pcse_gym
```

### To Run

This package is not meant to be runnable as is, and is used in conjuction with the 
Wofost-Gym Environment. Please see https://github.com/Intelligent-Reliable-Autonomous-Systems/WOFOST-Gym
for the full package


### Overview
The PCSE Gym Environment provides one base environment, NPK_Env, which inherits
from the Gymnasium.Env class. It requires a valid filename to a config file located
in ../config/ (see WOFOST-Gym). This config file provides the information for 
the crop engine (WOFOST8) and soil manager (SoilWrapper_LNPKW). We have provided
48 possible configuration environments with the hope that these provide sufficient configurations 
that do not need to be modified. However, see the following section for how to create
a new environment if needed. 

For specifying which crop to grow at a given site, and creating a new crop please 
see the /../env_config/ folder and utils.py file. 

Upon intialization, the agromangement data, crop data, and site data are loaded from
the ../env_config/ folder. The Agromanagement file specifies the 
crop to grow, site and soil dynamics, and the location and year which control the 
weather. The intervention interval can be specified as daily, weekly, monthly, etc. 

The observation space contains the weather variables for the next intervention period
and the current state of the crop. Which variables are output can be configured
in the utils.py NPK_Args file or via command line. For more information on the 
possible outputs, see agaid_crop_simulator/env_config/

The action space is a gym.Box space of size of the states observed. At each
intervention, either nitrogen, phosphorous, potassium, or water can be applied to
the crop in varying amounts specified by the number of actions and the action amount
in the utils.py NPK_Args file. 

The step function takes the current state of the crop, the intervention interval
weather, and current action, and sends it to the crop model. The crop model proceeds
to run the simulation for the duration of the intervention interval. At the end of 
said interval, the output is returned as a pd.DataFrame and then processed to a 
Gym compatible output. 

On reset, the crop model is reset to its initial state as specified in the 
agromanagement file. If the --random-reset flag is true, the year will be reset
to a random year in [1984,2017] from the NASA Power weather database of historical
weather data. This is useful for training RL Agents as it adds some stochasticity
to the simulation. 

Most RL agents (PPO, DQN, SAC) only support Discrete Action Spaces. We have included
the NPKDiscreteWrapper in pcse_gym/wrappers which automatically converts an 
action tuple [x,y] into a single integer action for use in these RL algorithms.
If training a new RL agent, be sure to include the line 
env = pcse_gym.wrappers.NPKDiscreteWrapper(env) during the environment declaration

## Current environments
The base environment simulates crop growth in water and NPK limited conditions. 
However, sometimes other environments are desired to focus on only learning a 
policy for a given case. To support this, we provide 6 environments where some
nutrients/water are abundant. We accomplish this by creating multiple config files
in the /agaid_crop_simulator/pcse/conf/ folder which reference different soil wrappers
in the /agaid_crop_simulator/pcse/soil/ folder. For more information on how this 
is accomplished, see the following section. 

We also have the following environments:
1. wofost-v0: Default Environment simulating limited NPK and water availability
2. pp-v0: Potential Production environment with abundant NPK and water
3. limited_w-v0: Limited Water environment with abundant NPK but limited water
4. limited_npk-v0: Limited NPK environment with limited NPK but abundant water
5. limited_n-v0: Limited N environment with abundant P/K and water but limited N
6. limited_nw-v0: Limited N and Water environment with abundant P/K but limited Nitrogen and Water

## Current reward functions
For training RL agents, one of the most important features is the reward function.
Given that we provide multiple environments with various nutrient availabilities,
it is then the case that we need various reward functions to evaluate the performance
of different policies in these environments. To provide maximal customization and 
enable the user to create their own reward function, we have all reward functions
as gym.wrapper classes. The reward function used can be specified in the 
NPK_Args.env-reward in utils.py or via command line. 

By default, the reward function is the Weight of Storage Organs (WSO) minus
the total fertilizer applied and water applied, multiplied by their respective
cost coefficients. We provide the following two wrappers

1. RewardTotalGrowthWrapper: reward is only a function of WSO, meaning that there
is no associated cost with fertilization or irrigation actions. This reward is
useful for finding the maximimum growth possible with no constraints

2. RewardFertilizationCostWrapper: reward is a function of WSO minus the total 
fertilization applied times some coefficient. This coefficient can be specified
in NPK_Args. With a sufficiently high coefficient, a reward function can be found
that strikes the appropriate balance between fertilization and crop growth. 




# WOFOST-Gym

DISCLAIMER: This repository is still actively under development. Please email 
Will Solow (soloww@oregonstate.edu) with use-case questions and bug reports. 

This is the WOFOSTGym Crop Simulator for the joint [AgAid](https://agaid.org/) Project between Oregon State University (OSU) and Washington State University (WSU). 

See our documentation:

https://intelligent-reliable-autonomous-systems.github.io/WOFOSTGym-Docs/

See our website:

https://intelligent-reliable-autonomous-systems.github.io/WOFOSTGym-Site/

### Citing
```bibtex
@inproceedings{solow_wofostgym_2025,
  title={WOFOSTGym: A Crop Simulator for Learning Annual and Perennial Crop Management Strategies},
  author={Solow, William and Saisubramanian, Sandhya and Fern, Alan},
  booktitle={Reinforcement Learning Conference (RLC) 2025}, 
  year={2025}}
```

## Description

This package provides the following main features:
1. A crop simulation environment based off of the WOFOST8 crop simulation model
    which simulates the growth of various crops in N/P/K and water limited conditions. 
    The model has been modified to interface nicely with a Gymnasium environment
    and to provide support for perennial crops and multi-year simulations.
2. A Gymansium environment which contains the WOFOST8 crop simulation environment.
    This wrapper has support for various sized action spaces for the application
    of fertilizer and water, and various reward functions which can be specified 
    by the user. We provide easy support for multi-year simulations across various
    farms. 
3. We support the training of Deep RL agents with PPO, SAC, and DQN based on 
    [cleanRL](https://github.com/vwxyzjn/cleanrl) implementations. We provide
    various visualizations for different state features and to visualize the 
    training of RL agents.
4. The generation of historical data across years, farms and crops to support
    offline RL and off-policy evaluation methods. 

Our aim with this project is to support the AgAid community, and other researchers, 
by enabling easy evaluation of decision making systems in the agriculture environment.
Our goal is not to have the most high-fidelty simulator available, although the 
WOFOST8 model is robust, but rather to provide a realistic environment to test
RL algorithms in the agricultural setting that is easy to use and customize. 

## Getting Started

### Dependencies

* This project is entirely self contained and built to run with Python 3.12
* Install using miniconda3 

### Installing

Recommended Installation Method:

1. Navigate to desired installation directory
2. git clone git@github.com:Intelligent-Reliable-Autonomous-Systems/WOFOSTGym.git
3. conda create -n <conda env name> python=3.12
4. conda activate <conda env name>
5. pip install -e pcse -e pcse_gym
6. pip install -e pcse_gym
7. pip install tyro torch omegaconf wandb tensorboard

For Gail/BC experiments: 

8. pip install -e imitation -e stable-baselines3
9. pip install tqdm huggingface_sb3

These commands will install all the required packages into the conda environment
needed to run all scripts in the agaid_crop_simulator package

## Executing Programs

After following the above installation instructions: 
1. Navigate to the base directory ../WOFOSTGym/
2. Run the testing domain with: python3 test_wofost.py --save-folder test/ --data-file test. This will generate a sample output using default configurations 
3. This may take a few seconds initially to configure the weather directory

### Use Cases:

* To generate data for Offline RL, Off-Policy Evaluation Problems, or Transfer Learning Problems:
    1. To generate data with a specified policy from pcse_gym/policies.py:
        - `python3 gen_data.py --save-folder <Location> --data-file <Filename> --policy-name <Name of Policy>`
    2. To generate data with a trained RL Agent based policy:
        - `python3 gen_data.py --save-folder <Location> --data-file <Filename> --agent-type <PPO | DQN | etc> --agent-path <Location/agent_name.pt>`
    3. NOTE: Use `--config-fpath` <Relative Path to Config> to load an environment configuration from a config.yaml file. If `None`, the default configuration will be used.

* To train an RL Agent: 
    1. `python3 train_agent.py --save-folder <Location> --agent-type <PPO | DQN | etc>`
    2. Use `--<Agent_Type: PPO|DQN|etc>.<Agent_Specific_Args>` to specify algorithm specific arguments
    3. To track using Weights and Biases add `--<Agent_Type: PPO|DQN|etc>.track`
    3. NOTE: Use `--config-fpath` <Relative Path to Config> to load an environment configuration from a config.yaml file. If `None`, the default configuration will be used. This works for loading previous Agent Configurations as well

## Help

Initial configuration for the Gym Environment parameters (Note: NOT the actual crop simulation) 
can be modified in the utils.py file. 

* The default path is the current working directory. All other paths are relative based on this working directory. 
* The env_config/ folder contains all default .yaml files for configuring the Crop Simulator. For further information,
please see the following READMEs: 

    * env_config/README_agro.md - overview of how to configure a crop simulation.

    * env_config/soil_config/README_add_soil.md - overview of how to add a new soil
        with all required parameters.
    * env_config/soil_config/README_soil_paramters.md - an overview of all configurable soil 
        parameters
    * env_config/soil_config/README_soil_states.md - an overview of all soil state and rate
        variables available for output with corresponding units.

    * env_config/crop_config/README_add_crop.md - overview of how to add a new crop
        with all required parameters.
    * env_config/crop_config/README_crop_paramters.md - an overview of all configurable crop 
        parameters
    * env_config/crop_config/README_crop_states.md - an overview of all crop state and rate
        variables available for output with corresponding units.

    * pcse/README.md - an overview of the Python Crop Simulation Environment (PCSE) and
        available resources to learn more.

    * rl_algs/README.md - an overview of the available Reinforcement Learning agents
        available 

    * pcse_gym/README.md - an overview of the Gymnasium wrapper and available configurations

Email soloww@oregonstate.edu with any further questions

## Authors

Will Solow (soloww@oregonstate.edu) - Principle Developer

Dr. Sandhya Saisubramanian (sandhya.sai@oregonstate.edu) - Project Lead

Dr. Alan Fern (alan.fern@oregonstate.edu) - Project Lead

## Version History

* 1.0.0
    * Initial Release
* 1.1.0
    * Upgraded to Python 3.12, many small fixes in documentation

## License

This project is licensed under the MIT License - see the LICENSE.md file for details

## Acknowledgments

The Original PCSE codebase and WOFOST8 Crop Simulator can be found at:
* [PCSE](https://github.com/ajwdewit/pcse)

While we made substantial modifications to the PCSE codebase to suit our needs, 
a large portion of the working code in the PCSE directory is the property of
Dr. Allard de Wit and Wageningen-UR Group. Please see the following paper for an
overview of WOFOST:
* [WOFOST](https://bsssjournals.onlinelibrary.wiley.com/doi/10.1111/j.1475-2743.1989.tb00755.x)

The original inspiration for a crop simulator gym environment came from the paper:
* [CropGym](https://arxiv.org/pdf/2104.04326)

We have since extended their work to interface with multiple Reinforcement Learning Agents, 
have added support for perennial fruit tree crops, grapes, multi-year simulations, and different sowing
and harvesting actions. 

The Python Crop Simulation Environment (PCSE) is well documented. Resources can 
be found here:
* [PCSE Docs](https://pcse.readthedocs.io/en/stable/)

The WOFOST crop simulator is also well documented, and we use the WOFOST8 model
in our crop simulator. Documentation can be found here:
* [WOFOST Docs](https://wofost.readthedocs.io/en/latest/)
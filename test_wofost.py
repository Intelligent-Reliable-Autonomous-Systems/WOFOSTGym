"""
File for testing the installation and setup of the WOFOST Gym Environment
with a few simple plots for output 

Written by: Will Solow, 2024

To run: python3 test_wofost.py --save-folder <folder>
"""

import numpy as np
import tyro

import pcse_gym
import pcse_gym.policies as policies
from pcse_gym.envs.wofost_base import NPK_Env, Plant_NPK_Env, Harvest_NPK_Env
import utils
import vis_data
if __name__ == "__main__":
    args = tyro.cli(utils.Args)
    # Make the gym environment with wrappers
    env = utils.make_gym_env(args)
    env = utils.wrap_env_reward(env, args)
    env = pcse_gym.wrappers.NPKDictActionWrapper(env)
    env = pcse_gym.wrappers.NPKDictObservationWrapper(env)

    # Set default policy for use
    if isinstance(env.unwrapped, Harvest_NPK_Env):
        policy = policies.No_Action_Harvest(env)
    elif isinstance(env.unwrapped, Plant_NPK_Env):
        policy = policies.No_Action_Plant(env)
    else:
        policy = policies.Interval_NW(env,amount=2,interval=1)

    obs, _ = env.reset()

    term = False
    trunc = False
    obs_arr = []
    action_arr = []
    reward_arr = []
    next_obs_arr = []
    dones_arr = []

    # Run simulation and store data
    while not term:
        action = policy(obs)
        next_obs, rewards, term, trunc, _ = env.step(action)
        obs_arr.append(utils.obs_to_numpy(obs))
        action_arr.append(action)
        reward_arr.append(rewards)
        next_obs_arr.append(next_obs)
        dones_arr.append(term or trunc)

        obs = next_obs
        if term or trunc:
            obs, _ = env.reset()
            break

    env.close()

    # Cast to ndarray
    obs_arr = np.array(obs_arr)
    action_arr = np.array(action_arr)
    reward_arr = np.array(reward_arr)
    next_obs_arr = np.array(next_obs_arr)
    dones_arr = np.array(dones_arr)

    # Save and plot data
    utils.save_file_npz(args, obs_arr, action_arr, reward_arr, next_obs_arr, dones_arr, env.unwrapped.get_output_vars())
    vis_data.plot_output(args, output_vars=env.unwrapped.get_output_vars(), obs=obs_arr, rewards=reward_arr,save=True)
    
 
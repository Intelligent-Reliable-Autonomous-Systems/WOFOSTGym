"""
File for generating data in .npz or pandas.DataFrame formats
Allows for data to be generated with pre specified policies (specified in pcse_gym/policies)
or with PyTorch agent.pt files

Written by: Will Solow, 2024

To run: python3 gen_data.py --save-folder <Location to save folder> --data-file <Name of data file>

"""

import gymnasium as gym
import numpy as np
import pcse_gym
import pandas as pd
import torch
import os
import tyro
from dataclasses import dataclass
from typing import Optional

import utils
import pcse_gym.policies as policies
from rl_algs.rl_utils import make_env


@dataclass
class DataArgs(utils.Args):
    """File extension (.npz or .csv)"""
    """.npz files will have (obs, action, reward, next_obs, done, info) tuples"""
    """while .csv files will have daily observations"""
    file_type: Optional[str] = "npz"

    """Policy name if using a policy in the policies.py file"""
    policy_name: Optional[str] = None
    """Agent type, for generating data"""
    agent_type: Optional[str] = None
    """Agent path, for loading .pt agents"""
    agent_path: Optional[str] = None

    """Intervention Interval for Pre Specified policy"""
    interval: Optional[int] = 1
    """Amount of Fertilizer/irrigation for Pre Specified policy"""
    amount: Optional[int] = 1
    """Threshold for Fertilizer/Irrigation for Pre Specified Policy"""
    threshold: Optional[int] = 0

    """Parameters for generating data"""
    """Year range, incremented by 1"""
    year_low: int = 1984
    year_high: int = 2019
    """Latitude range, incremented by .5"""
    lat_low: float = 50
    lat_high: float = 50

    """Latitude range, incremented by .5"""
    lon_low: float = 5
    lon_high: float = 5

    """Cuda setting for RL agents"""
    cuda = True

def csv(env, args, pol):
    """
    Generate data from a policy and save to .csv format
    """
    assert isinstance(args.save_folder, str), f"Folder args.save_folder `{args.save_folder}` must be of type `str`"
    assert args.save_folder.endswith("/"), f"Folder args.save_folder `{args.save_folder}` must end with `/`"
    assert isinstance(args.data_file, str), f"File args.data_file `{args.data_file}` must be of type `str`"

    years = np.arange(start=args.year_low,stop=args.year_high+1,step=1)
    latitudes = np.arange(start=args.lat_low,stop=args.lat_high+.5,step=.5)
    longitudes = np.arange(start=args.lon_low,stop=args.lon_high+.5,step=.5)

    lat_long = [(i,j) for i in latitudes for j in longitudes]
    loc_yr = [[loc, yr] for yr in years for loc in lat_long]

    obs_arr = []
    _, _ = env.reset()
    for pair in loc_yr:
        obs, _ = env.reset(**{'year':pair[1], 'location':pair[0]})

        done = False
        while not done:
            if args.agent_type:
                obs = torch.from_numpy(obs).float()
            action = pol.get_action(obs)
            next_obs, reward, done, trunc, _ = env.step(action)

            obs_arr.append(utils.obs_to_numpy(obs))

            obs = next_obs
            if done:
                obs, _ = env.reset()
                break

    df = pd.DataFrame(data=obs_arr, columns=env.unwrapped.output_vars+env.unwrapped.weather_vars+["DAYS ELAPSED"])
    df.to_csv(f'{args.save_folder}{args.data_file}.csv', index=False)
    
    return df

def npz(env, args, pol):
    """
    Generate data and save in .npz format from environments
    """
    assert isinstance(args.save_folder, str), f"Folder args.save_folder `{args.save_folder}` must be of type `str`"
    assert args.save_folder.endswith("/"), f"Folder args.save_folder `{args.save_folder}` must end with `/`"
    assert isinstance(args.data_file, str), f"File args.data_file `{args.data_file}` must be of type `str`"

    years = np.arange(start=args.year_low,stop=args.year_high+1,step=1)
    latitudes = np.arange(start=args.lat_low,stop=args.lat_high+.5,step=.5)
    longitudes = np.arange(start=args.lon_low,stop=args.lon_high+.5,step=.5)

    lat_long = [(i,j) for i in latitudes for j in longitudes] 
    loc_yr = [[loc, yr] for yr in years for loc in lat_long]

    obs_arr = []
    next_obs_arr = []
    action_arr = []
    dones_arr = []
    rewards_arr = []
    info_arr = []

    for pair in loc_yr:
        obs, _ = env.reset(**{'year':pair[1], 'location':pair[0]})

        done = False
        while not done:
            if args.agent_type:
                obs = torch.from_numpy(obs).float().to('cuda')
            action = pol.get_action(obs)
            next_obs, reward, done, trunc, info = env.step(action)

            if args.agent_type:
                reward = env.unnormalize(reward)
                obs_arr.append(env.unnormalize_obs(utils.obs_to_numpy(obs)))
                next_obs_arr.append(env.unnormalize_obs(utils.obs_to_numpy(next_obs)))
            else:
                obs_arr.append(utils.obs_to_numpy(obs))
                next_obs_arr.append(utils.obs_to_numpy(next_obs))
            action_arr.append(utils.action_to_numpy(env, action))
            dones_arr.append(done)

            if isinstance(reward, torch.Tensor):
                reward.cpu().numpy().flatten()[0]
            elif isinstance(reward, np.ndarray):
                reward = reward.flatten()[0]

            rewards_arr.append(reward)
            info_arr.append(info)

            obs = next_obs
    
            if done:
                obs, _ = env.reset()
                break
    np.savez(f"{args.save_folder}{args.data_file}.npz", obs=np.array(obs_arr), next_obs=np.array(next_obs_arr), \
             actions=np.array(action_arr), rewards=np.array(rewards_arr), dones=np.array(dones_arr), infos=np.array(info_arr), 
             output_vars=np.array(env.unwrapped.get_output_vars()))

if __name__ == "__main__":
    """
    Runs the data collection
    """

    args = tyro.cli(DataArgs)
    env = utils.make_gym_env(args)
    env = utils.wrap_env_reward(env, args)
    if args.agent_type:
        env = pcse_gym.wrappers.NormalizeObservation(env)
        env = pcse_gym.wrappers.NormalizeReward(env)

    env.random_reset = False
    env.domain_rand = False
    if args.policy_name: # Pre specified policies
        env = pcse_gym.wrappers.NPKDictObservationWrapper(env)
        env = pcse_gym.wrappers.NPKDictActionWrapper(env)
        try:
            policy_constr = utils.get_classes(policies)[args.policy_name]
            kwargs = {"amount":args.amount, "interval":args.interval, "threshold":args.threshold}
            policy = policy_constr(env, **kwargs)
        except:
            msg = f'No policy {args.policy_name} found in policies.py'
            raise Exception(msg)

    else: # PyTorch Agents
        assert isinstance(args.agent_path, str), f" `--args.agent-path` is `{args.agent_path}` (incorrectly specified) and no Pre Specified Policy is provided"
        assert os.path.isfile(f"{os.getcwd()}/{args.agent_path}"), f"`{args.agent_path}` is not a valid file"
        assert args.agent_path.endswith(".pt"), f"`{args.agent_path}` must be a valid `.pt` file"

        envs = gym.vector.SyncVectorEnv([make_env(args) for i in range(1)],)
        
        try:
            ag_constr = utils.get_valid_agents()[args.agent_type]
            policy = ag_constr(envs)
        except:
            msg = "Error in getting agent. Check that `--args.agent-type` is a valid agent in rl_algs/"
            raise Exception(msg)

        device = torch.device("cuda" if torch.cuda.is_available() and args.cuda else "cpu")
        try:
            state_dict = torch.load(f"{args.agent_path}", map_location=device, weights_only=True)
            if args.agent_type in ["BC", "GAIL", "AIRL"]:
                state_dict = {f"policy.{k}": v for k, v in state_dict.items()}
            policy.load_state_dict(state_dict)
            policy.to(device)
        except:
            msg = "Error in loading state dict. Likely caused by loading an agent.pt file with incompatible `args.agent_type`"
            raise Exception(msg)
        
    try: 
        data_func = utils.get_functions(__import__(__name__))[args.file_type]
    except:
        msg = f"File Output type `{args.file_type}` not supported, please check `--args.file-type`"
        raise Exception(msg)

    data_func(env, args, policy)




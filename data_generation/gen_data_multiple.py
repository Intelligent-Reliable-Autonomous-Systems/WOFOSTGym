"""
Generates data in compatible format for multiple policies and farms
Allows for data to be generated with handcrafted policies (specified in pcse_gym/policies)
or with PyTorch agent.pt files

Written by: Will Solow, 2024

To run: python3 -m data_generation.gen_data_multiple --save-folder <Location to save folder> --data-file <Name of data file>

"""

import gymnasium as gym
import numpy as np
import pcse_gym
import torch

import tyro
from dataclasses import dataclass
from typing import Optional

import utils
import pcse_gym.policies as policies
from rl_algs.rl_utils import make_env_pass, Agent
from rl_algs.PPO import PPO
from rl_algs.DQN import DQN
from rl_algs.SAC import SAC
from rl_algs.BCQ import BCQ
from rl_algs.AIRL import AIRL
from rl_algs.BC import BC
from rl_algs.GAIL import GAIL


@dataclass
class DataArgs(utils.Args):
    """File extension (.npz or .csv)"""

    """.npz files will have (obs, action, reward, next_obs, done, info) tuples"""
    """while .csv files will have daily observations"""
    file_type: Optional[str] = None

    """Policy name if using a policy in the policies.py file"""
    policy_name: Optional[str] = None
    """Agent type, for generating data"""
    agent_type: Optional[str] = None
    """Agent path, for loading .pt agents"""
    agent_path: Optional[str] = None

    """Intervention Interval for Handcrafted policy"""
    interval: Optional[int] = 1
    """Amount of Fertilizer/irrigation for Handcrafted policy"""
    amount: Optional[int] = 1
    """Threshold for Fertilizer/Irrigation for Handcrafted Policy"""
    threshold: Optional[int] = 0

    """Parameters for generating data"""
    """Year range, incremented by 1"""
    year_low: int = 2000
    year_high: int = 2010
    """Latitude range, incremented by .5"""
    lat_low: float = 50
    lat_high: float = 50

    """Latitude range, incremented by .5"""
    lon_low: float = 5
    lon_high: float = 5


def npz_multiple(envs:gym.Env, args:DataArgs, pols:list[Agent], pols_kwargs:dict[str, str]) -> None:
    """
    Generate data and save in .npz format from environments
    """
    assert isinstance(args.save_folder, str), f"Folder args.save_folder `{args.save_folder}` must be of type `str`"
    assert args.save_folder.endswith("/"), f"Folder args.save_folder `{args.save_folder}` must end with `/`"
    assert isinstance(args.data_file, str), f"File args.data_file `{args.data_file}` must be of type `str`"
    assert len(pols) == len(pols_kwargs), f"Length of Policies and Policy kwargs do not match."

    years = np.arange(start=args.year_low, stop=args.year_high + 1, step=1)
    latitudes = np.arange(start=args.lat_low, stop=args.lat_high + 0.5, step=0.5)
    longitudes = np.arange(start=args.lon_low, stop=args.lon_high + 0.5, step=0.5)

    lat_long = [(i, j) for i in latitudes for j in longitudes]
    loc_yr = [[loc, yr] for yr in years for loc in lat_long]

    obs_arr = [[[] for _ in range(len(pols))] for _ in range(len(envs))]
    next_obs_arr = [[[] for _ in range(len(pols))] for _ in range(len(envs))]
    action_arr = [[[] for i in range(len(pols))] for _ in range(len(envs))]
    dones_arr = [[[] for _ in range(len(pols))] for _ in range(len(envs))]
    rewards_arr = [[[] for _ in range(len(pols))] for _ in range(len(envs))]

    for i, env in enumerate(envs):
        for j, pol_constr in enumerate(pols):

            if issubclass(pol_constr, pcse_gym.policies.Policy):
                base_env = env
                env = pcse_gym.wrappers.NPKDictObservationWrapper(env)
                env = pcse_gym.wrappers.NPKDictActionWrapper(env)
            elif issubclass(pol_constr, Agent):
                base_env = env
                env = gym.vector.SyncVectorEnv(
                    [make_env_pass(env) for _ in range(1)],
                )

            pol = pol_constr(env, **pols_kwargs[j])

            for pair in loc_yr:
                if isinstance(env, gym.vector.SyncVectorEnv):
                    ob_tens = []
                    for _, single_env in enumerate(env.envs):
                        ob, _ = single_env.reset(year=pair[1], location=pair[0])
                        ob_tens.append(ob)
                    obs = torch.Tensor(ob_tens)
                else:
                    obs, _ = env.reset(**{"year": pair[1], "location": pair[0]})

                done = False
                while not done:
                    if isinstance(pol, Agent) and isinstance(obs, np.ndarray):
                        obs = torch.from_numpy(obs).float()

                    action = pol.get_action(obs)
                    next_obs, reward, done, trunc, _ = env.step(action)

                    obs_arr[i][j].append(utils.obs_to_numpy(obs))
                    next_obs_arr[i][j].append(utils.obs_to_numpy(next_obs))
                    action_arr[i][j].append(utils.action_to_numpy(env, action))
                    dones_arr[i][j].append(np.squeeze(done))
                    rewards_arr[i][j].append(np.squeeze(reward))
                    obs = next_obs

                    if done:
                        obs, _ = env.reset()
                        break

            if isinstance(pol, pcse_gym.policies.Policy):
                env = base_env
            elif isinstance(pol, Agent):
                env = base_env

    np.savez(
        f"{args.save_folder}{args.data_file}.npz",
        obs=np.array(obs_arr),
        next_obs=np.array(next_obs_arr),
        actions=np.array(action_arr),
        rewards=np.array(rewards_arr),
        dones=np.array(dones_arr),
        output_vars=np.array(env.unwrapped.get_output_vars()),
    )


if __name__ == "__main__":

    """
    Runs the data collection
    """

    # Create environment
    args = tyro.cli(DataArgs)

    # Set the file paths to the configuration files that are to be loaded
    # Corresponds to the different farms
    config_fpaths = ["data/Jujube_Threshold_WK_Rand/config.yaml"]
    envs = utils.make_gym_envs(args, config_fpaths=config_fpaths)

    envs = [utils.wrap_env_reward(env, args) for env in envs]
    for env in envs:
        env.random_reset = False
        env.domain_rand = False
        env.train_reset = False
        env.crop_rand = False

    # Pass the constructor for the policy, either a pcse_gym.policies or rl_utils.Agent class
    pols = [PPO]

    # Specify the kwargs for the policies. If using a PyTorch policy from rl_algs, use
    # the kwargs: `{"state_fpath": <path-to-agent>}
    pols_kwargs = [
        {"state_fpath": "data/Jujube_Threshold_WK_Rand/PPO/perennial-lnpkw-v0__rl_utils__1__1738184893/agent.pt"}
    ]
    """pols_kwargs = [{"state_fpath":"data/Potato_Limited_WK_Rand/PPO/lnpkw-v0__rl_utils__1__1738213380/agent.pt"}, # All
                {"state_fpath":"data/Potato_Limited_WK_Rand/PPO/lnpkw-v0__rl_utils__1__1738213406/agent.pt"}, # No Rain
                {"state_fpath":"data/Potato_Limited_WK_Rand/PPO/lnpkw-v0__rl_utils__1__1738213411/agent.pt"}, # No total N/NAvail
                {"state_fpath":"data/Potato_Limited_WK_Rand/PPO/lnpkw-v0__rl_utils__1__1738213417/agent.pt"}, #No total N/Rain 
                ]"""

    npz_multiple(envs, args, pols, pols_kwargs)

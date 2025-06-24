"""File for utils functions. Importantly contains:
    - Args: Dataclass for configuring paths for the WOFOST Environment
    - get_gym_args: function for getting the required arguments for the gym
    environment from the Args dataclass

Written by: Will Solow, 2024
"""

from argparse import Namespace
import gymnasium as gym
import warnings
import numpy as np
import pandas as pd
import torch
from dataclasses import dataclass, is_dataclass, fields, is_dataclass
from typing import Optional
from omegaconf import OmegaConf
from omegaconf.dictconfig import DictConfig
from omegaconf.listconfig import ListConfig
import os
from typing import Optional, List
from pcse_gym.args import NPK_Args, WOFOST_Args, Agro_Args
import copy
import datetime
from inspect import getmembers, isclass, isfunction, getmodule


from pcse_gym.envs.wofost_base import Plant_NPK_Env, Harvest_NPK_Env, Multi_NPK_Env
import pcse_gym.wrappers.wrappers as wrappers

warnings.filterwarnings("ignore", category=UserWarning)


@dataclass
class Args:
    """
    Dataclass for configuration a Gym environment
    """

    """Parameters for the NPK Gym Environment"""
    npk: NPK_Args

    """Environment ID"""
    env_id: str = "lnpkw-v0"
    """Env Reward Function. Do not specify for default reward"""
    env_reward: Optional[str] = None
    """Rendering mode. `None` or `human`"""
    render_mode: Optional[str] = "None"

    """Relative location of run, either agent or data, where to save config file 
        and associated run (policies, .npz files, etc)"""
    save_folder: Optional[str] = None
    """Relative location of configuration file to load"""
    config_fpath: Optional[str] = None
    """Name of data file to save save in save_folder"""
    data_file: Optional[str] = None

    """Agromanagement file"""
    agro_file: str = "wheat_agro.yaml"

    """Reward Wrapper Arguments"""
    """Maximum N Threshold"""
    max_n: Optional[float] = None
    """Maximum Phosphorous Threshold"""
    max_p: Optional[float] = None
    """Maximum Potassium Threshold"""
    max_k: Optional[float] = None
    """Maximum Irrigation Threshold"""
    max_w: Optional[float] = None
    """Cost of fertilization """
    cost: Optional[float] = None

    """Path configuration, generally do not change these """
    """Base filepath"""
    base_fpath: str = f"{os.getcwd()}/"
    """Relative path to agromanagement configuration file"""
    agro_fpath: str = "env_config/agro/"
    """Relative path to crop configuration folder"""
    crop_fpath: str = "env_config/crop/"
    """Relative path to site configuration foloder"""
    site_fpath: str = "env_config/site/"
    """Relative path to the state units """
    unit_fpath: str = "env_config/state_units.yaml"
    """Relative path to the state names"""
    name_fpath: str = "env_config/state_names.yaml"
    """Relative path to the state ranges for normalization"""
    range_fpath: str = "env_config/state_ranges.yaml"


HATCHES = [
    ".",  # Small dots
    "",
    "+",  # Crossing diagonal lines
    "O",  # Large circles
    "o",  # Small circles
    "O",  # Large circles
    "/",  # Diagonal lines (forward slash)
    "\\",  # Diagonal lines (backslash)
    "|",  # Vertical lines
    "*",  # Stars
    "-",  # Horizontal lines
    "x",  # Crossing lines (horizontal and vertical)
]

COLORS = [
    "#ff0000",  # Red
    "#0000ff",  # Blue
    "#daa520",  # Goldenrod
    "#4B0082",  # Dark violet
    "#008000",  # Dark Green
    "#ff00ff",  # Magenta
    "#00ff00",  # Green
    "#00ffff",  # Cyan
    "#ff7700",  # Orange
    "#000000",  # Black
]


def wrap_env_reward(env: gym.Env, args: Namespace) -> function:
    """
    Function to wrap the environment with a given reward function
    Based on the reward functions created in the pcse_gym/wrappers/
    """
    # Default environment
    if not args.env_reward:
        return env
    # Reward wrapper
    try:
        reward_constr = get_reward_wrappers(wrappers)[args.env_reward]
        return reward_constr(env, args)
    # Incorrectly specified reward
    except:
        msg = f"Incorrectly specified RewardWrapper args.env_reward: `{args.env_reward}`"
        raise Exception(msg)


def make_gym_env(args: Namespace, run_name: str = None) -> gym.Env:
    """
    Make a gym environment. Ensures that OrderEnforcing and PassiveEnvChecker
    are not applied to environment
    """

    assert args.save_folder is not None, "Specify `save_folder` to save config file."
    assert isinstance(
        args.save_folder, str
    ), f"`args.save_folder` must be of type `str` but is of type `{type(args.save_folder)}`."
    assert args.save_folder.endswith("/"), f"Folder args.save_folder `{args.save_folder}` must end with `/`"

    # If valid config file, load env from that configuration
    if args.config_fpath:
        assert os.path.isfile(
            f"{os.getcwd()}/{args.config_fpath}"
        ), f"Configuration file `{args.config_fpath} does not exist"

        config = OmegaConf.load(f"{os.getcwd()}/{args.config_fpath}")

        valid_keys = {field.name for field in type(args).__dataclass_fields__.values()}
        filtered_fields = {k: v for k, v in correct_config_lists(config).items() if k in valid_keys}
        env_id, env_kwargs = get_gym_args(type(args)(**filtered_fields))
        env = gym.make(env_id, **env_kwargs).unwrapped
    else:
        env_id, env_kwargs = get_gym_args(args)
        env = gym.make(env_id, **env_kwargs).unwrapped

        config = OmegaConf.structured(args)

        if hasattr(args, "agent_type"):
            if args.agent_type:
                config = OmegaConf.create(
                    {
                        k: v
                        for k, v in config.items()
                        if k not in [a for a in list(get_valid_agents().keys()) if a != args.agent_type]
                    }
                )
        os.makedirs(args.save_folder, exist_ok=True)

        if isinstance(env, Multi_NPK_Env):
            for i in range(env.num_farms):
                wf_i = {**env._get_site_data(i), **env._get_crop_data(i)}
                ag_i = copy.deepcopy(env.agromanagement)

                # Reconcile and merge configurations
                agi_config = correct_config_flatten(Agro_Args, ag_i)
                wfi_config = correct_config_floats(WOFOST_Args, wf_i)

                config_i = OmegaConf.merge(config, {"npk": {"wf": wfi_config, "ag": agi_config}})

                if run_name is None:
                    save_file = f"{args.save_folder}config_farm_{i}.yaml"
                else:
                    save_file = f"{args.save_folder}/{run_name}/config_farm_{i}.yaml"
                with open(save_file, "w") as fp:
                    OmegaConf.save(config=config_i, f=fp.name)
        else:
            # Make configurations
            wf = {**env._get_site_data(), **env._get_crop_data()}
            ag = copy.deepcopy(env.agromanagement)

            # Reconcile and merge configurations
            agro_config = correct_config_flatten(Agro_Args, ag)
            wf_config = correct_config_floats(WOFOST_Args, wf)

            config = OmegaConf.merge(config, {"npk": {"wf": wf_config, "ag": agro_config}})

            if run_name is None:
                save_file = f"{args.save_folder}config.yaml"
            else:
                save_file = f"{args.save_folder}/{run_name}/config.yaml"
            with open(save_file, "w") as fp:
                OmegaConf.save(config=config, f=fp.name)
    return env


def make_gym_envs(args: Namespace, config_fpaths: list, run_name: str = None) -> list[gym.Env]:
    """
    Make multiple gym environments from a list of configurations
    """

    assert args.save_folder is not None, "Specify `save_folder` to save config file."
    assert isinstance(
        args.save_folder, str
    ), f"`args.save_folder` must be of type `str` but is of type `{type(args.save_folder)}`."
    assert args.save_folder.endswith("/"), f"Folder args.save_folder `{args.save_folder}` must end with `/`"
    assert isinstance(
        config_fpaths, list
    ), f"`config_fpaths` must be of type `list` but is of type `{type(config_fpaths)}`"

    envs = []
    for i, path in enumerate(config_fpaths):
        assert os.path.isfile(f"{os.getcwd()}/{path}"), f"Configuration file `{path} does not exist"

        config = OmegaConf.load(f"{os.getcwd()}/{path}")

        valid_keys = {field.name for field in type(args).__dataclass_fields__.values()}
        filtered_fields = {k: v for k, v in correct_config_lists(config).items() if k in valid_keys}

        env_id, env_kwargs = get_gym_args(type(args)(**filtered_fields))

        envs.append(gym.make(env_id, **env_kwargs).unwrapped)

        os.makedirs(args.save_folder, exist_ok=True)
        if run_name is None:
            save_file = f"{args.save_folder}config.yaml"
        else:
            save_file = f"{args.save_folder}/{run_name}/config.yaml"
        with open(save_file, "w") as fp:
            OmegaConf.save(config=config, f=fp.name)

    return envs


def get_gym_args(args: Args) -> tuple[str, dict]:
    """
    Returns the Environment ID and required arguments for the WOFOST Gym
    Environment

    Arguments:
        Args: Args dataclass
    """
    env_kwargs = {
        "args": correct_commandline_lists(args.npk),
        "base_fpath": args.base_fpath,
        "agro_fpath": f"{args.agro_fpath}{args.agro_file}",
        "site_fpath": args.site_fpath,
        "crop_fpath": args.crop_fpath,
        "unit_fpath": args.unit_fpath,
        "name_fpath": args.name_fpath,
        "range_fpath": args.range_fpath,
        "render_mode": args.render_mode,
    }

    return args.env_id, env_kwargs


def correct_config_flatten(args: Namespace, d: dict) -> DictConfig:
    """
    Flatten dictionaries and get all non-dictionary key-value pairs
    """

    def recurse_dict(d, flattened_dict={}):
        """
        Recurse through all sub dictionaries and make a flattened dictionary
        """
        for k, v in d.items():
            if isinstance(v, dict):
                recurse_dict(v, flattened_dict=flattened_dict)
            else:
                if isinstance(v, datetime.date):
                    v = v.strftime("%Y-%m-%d")
                flattened_dict[k] = v

    flat_dict = {}
    recurse_dict(d, flattened_dict=flat_dict)

    return OmegaConf.merge(OmegaConf.structured(args), flat_dict)


def correct_config_floats(args: Namespace, d: dict) -> DictConfig:
    """
    Correct configurations by casting float types to list
    """
    typedict = {field.name: field.type for field in fields(args)}
    for k, v in typedict.items():
        if v == Optional[List[float]] and not isinstance(d[k], list):
            d[k] = list([d[k]])

    return OmegaConf.merge(OmegaConf.structured(args), d)


def correct_config_lists(d: dict) -> dict:
    """
    Correct configuration for loading floats to list
    """

    def recurse_dict(d):
        """
        Recurse through all sub dictionaries and make a flattened dictionary
        """
        for k, v in d.items():
            if isinstance(v, dict | DictConfig):
                recurse_dict(v)
            else:
                if isinstance(v, list | ListConfig):
                    if len(v) == 1:
                        d[k] = v[0]

    recurse_dict(d)

    return d


def correct_commandline_lists(d: dict) -> dict:
    """
    Correct any lists passed by command line
    """

    def iterate_dataclass(obj, prefix=""):
        if not is_dataclass(obj):
            return

        for field in fields(obj):
            value = getattr(obj, field.name)
            full_key = f"{prefix}.{field.name}" if prefix else field.name

            if is_dataclass(value):  # If the value is another dataclass, recurse
                iterate_dataclass(value, prefix=full_key)
            else:
                if isinstance(value, list):
                    if len(value) != 0:
                        if isinstance(value[0], str) and len(value) == 1:
                            values = value[0].split(",")
                            for i, v in enumerate(values):
                                values[i] = v.strip("[], ")
                                try:
                                    values[i] = float(values[i])
                                except:
                                    pass
                            setattr(obj, field.name, values)
                        elif isinstance(value[0], str):
                            for i, v in enumerate(value):
                                value[i] = v.strip("[], ")
                                try:
                                    value[i] = float(value[i])
                                except:
                                    pass
                            setattr(obj, field.name, value)

    iterate_dataclass(d)
    return d


def save_file_npz(
    args: Args,
    obs: np.ndarray | list,
    actions: np.ndarray,
    rewards: np.ndarray,
    next_obs: np.ndarray,
    dones: np.ndarray,
    output_vars: np.darray,
) -> None:
    """
    Save observations and rewards as .npz file
    """
    assert isinstance(args.save_folder, str), f"Folder args.save_folder `{args.save_folder}` must be of type `str`"
    assert args.save_folder.endswith("/"), f"Folder args.save_folder `{args.save_folder}` must end with `/`"

    assert isinstance(
        args.data_file, str
    ), f"args.data_file must be of type `str` but is of type `{type(args.data_file)}`"

    np.savez(
        f"{args.save_folder}{args.data_file}.npz",
        obs=np.array(obs),
        next_obs=np.array(next_obs),
        actions=np.array(actions),
        rewards=np.array(rewards),
        dones=np.array(dones),
        output_vars=np.array(output_vars),
    )


def load_data_file(fname: str) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Load the data file and get the list of variables for graphing"""
    assert isinstance(fname, str), f"File (args.data_file) `{fname}` is not of type String"
    assert fname.endswith(".npz") or fname.endswith(
        ".csv"
    ), f"File `{fname}` does not end with `.npz` or `.csv`, cannot load."

    if fname.endswith(".npz"):
        data = np.load(fname, allow_pickle=True)

        try:
            obs = data["obs"]
            actions = data["actions"]
            rewards = data["rewards"]
            next_obs = data["next_obs"]
            dones = data["dones"]
            output_vars = data["output_vars"]
        except:
            msg = f"`{fname}` missing one of the following keys: `obs`, `actions`, `rewards`, `next_obs`, `dones`, `output_vars`. Cannot load data"
            raise Exception(msg)

        return obs, actions, rewards, next_obs, dones, output_vars
    elif fname.endswith(".csv"):
        data = pd.read_csv(fname)

        try:
            output_vars = data.columns
            obs = data.to_numpy()
            actions = None
            rewards = None
            next_obs = None
            dones = None
        except:
            msg = f"Error in reading data from DataFrame `fname`. Check the configuration .csv file"

        return obs, actions, rewards, next_obs, dones, output_vars


def get_valid_agents() -> dict[str, object]:
    """
    Get the valid agents in the rl_algs folder
    """
    path = f"{os.getcwd()}/rl_algs"

    modules = {}
    for x in [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]:
        name = f"rl_algs.{os.path.splitext(os.path.basename(x))[0]}"
        modules = dict(modules, **dict(getmembers(__import__(name))))

    modules = {k: v for k, v in modules.items() if isinstance(v, type(__import__("sys")))}

    constr = {}
    for m in modules.values():
        classes = {
            name: obj for name, obj in getmembers(m, isclass) if obj.__module__ == m.__name__ and not is_dataclass(obj)
        }
        constr = dict(constr, **classes)
    return constr


def get_valid_trainers() -> dict[str, object]:
    """
    Get the valid training functions for each agent
    """
    path = f"{os.getcwd()}/rl_algs"

    modules = {}
    for x in [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]:
        name = f"rl_algs.{os.path.splitext(os.path.basename(x))[0]}"
        modules = dict(modules, **dict(getmembers(__import__(name))))

    modules = {k: v for k, v in modules.items() if isinstance(v, type(__import__("sys")))}

    trainer = {}
    for m in modules.values():
        classes = {
            m.__name__.removeprefix("rl_algs."): obj for name, obj in getmembers(m, isfunction) if name == "train"
        }
        trainer = dict(trainer, **classes)
    return trainer


def get_functions(file: str) -> dict[str, function]:
    """
    Get the functions that correspond only to a specific file
    """
    functions = {name: obj for name, obj in getmembers(file, isfunction) if getmodule(obj) == file}
    return functions


def get_classes(file: str) -> dict[str, object]:
    """
    Get the classes that are declared in a specific file
    """
    classes = {name: obj for name, obj in getmembers(file, isclass) if getmodule(obj) == file}
    return classes


def get_reward_wrappers(file: str):
    """
    Get the classes that are declared in a specific file
    """
    classes = {
        name: obj
        for name, obj in getmembers(file, isclass)
        if getmodule(obj) == file and issubclass(obj, wrappers.RewardWrapper)
    }
    return classes


def normalize(arr: np.ndarray) -> np.ndarray:
    """
    Min-Max normalize array
    """
    return (arr - np.min(arr)) / (np.max(arr) - np.min(arr) + 1e-12)


def obs_to_numpy(obs: dict | torch.Tensor | np.ndarray) -> np.ndarray:
    """
    Convert observation to numpy.ndarray based on type
    """
    if isinstance(obs, dict):
        return np.squeeze(np.array(list(obs.values())))
    elif isinstance(obs, torch.Tensor):
        return np.squeeze(obs.cpu().numpy())
    else:
        return np.squeeze(obs)


def action_to_numpy(env: gym.Env, act: float | torch.Tensor | np.ndarray | dict) -> np.ndarray:
    """
    Converts the dicionary action to an integer to be pased to the base
    environment.

    Args:
        action
    """
    if isinstance(act, float):
        return np.array([act])
    elif isinstance(act, torch.Tensor):
        return act.cpu().numpy()
    elif isinstance(act, np.ndarray):
        return act
    elif isinstance(act, dict):
        act_vals = list(act.values())
        for v in act_vals:
            if not isinstance(v, int):
                msg = "Action value must be of type int"
                raise Exception(msg)
        if len(np.nonzero(act_vals)[0]) > 1:
            msg = "More than one non-zero action value for policy"
            raise Exception(msg)
        if len(np.nonzero(act_vals)[0]) == 0:
            return np.array([0])
    else:
        msg = f"Unsupported Action Type `{type(act)}`. See README for more information"
        raise Exception(msg)

    if not "n" in act.keys():
        msg = "Nitrogen action 'n' not included in action dictionary keys"
        raise Exception(msg)
    if not "p" in act.keys():
        msg = "Phosphorous action 'p' not included in action dictionary keys"
        raise Exception(msg)
    if not "k" in act.keys():
        msg = "Potassium action 'k' not included in action dictionary keys"
        raise Exception(msg)
    if not "irrig" in act.keys():
        msg = "Irrigation action 'irrig' not included in action dictionary keys"
        raise Exception(msg)

    # Planting Single Year environments
    if isinstance(env.unwrapped, Plant_NPK_Env):
        if not "plant" in act.keys():
            msg = "'plant' not included in action dictionary keys"
            raise Exception(msg)
        if not "harvest" in act.keys():
            msg = "'harvest' not included in action dictionary keys"
            raise Exception(msg)
        if len(act.keys()) != env.unwrapped.NUM_ACT:
            msg = "Incorrect action dictionary specification"
            raise Exception(msg)

        offsets = [
            1,
            1,
            env.unwrapped.num_fert,
            env.unwrapped.num_fert,
            env.unwrapped.num_fert,
            env.unwrapped.num_irrig,
        ]
        act_values = [act["plant"], act["harvest"], act["n"], act["p"], act["k"], act["irrig"]]
        offset_flags = np.zeros(env.unwrapped.NUM_ACT)
        offset_flags[: np.nonzero(act_values)[0][0]] = 1

    # Harvesting Single Year environments
    elif isinstance(env.unwrapped, Harvest_NPK_Env):
        if not "harvest" in act.keys():
            msg = "'harvest' not included in action dictionary keys"
            raise Exception(msg)
        if len(act.keys()) != env.unwrapped.NUM_ACT:
            msg = "Incorrect action dictionary specification"
            raise Exception(msg)

        offsets = [1, env.unwrapped.num_fert, env.unwrapped.num_fert, env.unwrapped.num_fert, env.unwrapped.num_irrig]
        act_values = [act["harvest"], act["n"], act["p"], act["k"], act["irrig"]]
        offset_flags = np.zeros(env.unwrapped.NUM_ACT)
        offset_flags[: np.nonzero(act_values)[0][0]] = 1

    # Default environments
    else:
        if len(act.keys()) != env.unwrapped.NUM_ACT:
            msg = "Incorrect action dictionary specification"
            raise Exception(msg)

        offsets = [env.unwrapped.num_fert, env.unwrapped.num_fert, env.unwrapped.num_fert, env.unwrapped.num_irrig]
        act_values = [act["n"], act["p"], act["k"], act["irrig"]]
        offset_flags = np.zeros(env.env.unwrapped.NUM_ACT)
        offset_flags[: np.nonzero(act_values)[0][0]] = 1

    # Cast action to numpy array based on offsets computed above
    return np.array([np.sum(offsets * offset_flags) + act_values[np.nonzero(act_values)[0][0]]])

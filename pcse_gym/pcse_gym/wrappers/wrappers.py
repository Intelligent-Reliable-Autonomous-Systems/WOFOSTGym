"""
Core API for environment wrappers for handcrafted policies and varying rewards

Written by Will Solow, 2024
"""

import numpy as np
import gymnasium as gym
from gymnasium.spaces import Dict, Discrete, Box
from abc import abstractmethod, ABC
import torch
from argparse import Namespace

from pcse_gym.envs.wofost_base import NPK_Env, Plant_NPK_Env, Harvest_NPK_Env, Multi_NPK_Env
from pcse_gym.envs.wofost_base import LNPKW, LNPK, PP, LNW, LN, LW
from pcse_gym import exceptions as exc


class NPKNaNToZeroWrapper(gym.ObservationWrapper):
    """Wraps the observation by converting nan's to zero. Good for use in some
    RL agents
    """

    def __init__(self, env: gym.Env) -> None:
        """Initialize the :class:`NPKNaNToZeroWrapper` wrapper with an environment.

        Casts all NaN's to zero

        Args:
            env: The environment to apply the wrapper
        """
        super().__init__(env)
        self.env = env

    def observation(self, obs: np.ndarray) -> np.ndarray:
        """Casts all NaNs in crop to zero

        Args:
            observation
        """
        return np.nan_to_num(obs, nan=0.0)

    def reset(self, **kwargs: dict) -> tuple[np.ndarray, dict]:
        """Reset the environment to the initial state specified by the
        agromanagement, crop, and soil files.

        Args:
            **kwargs:
                year: year to reset enviroment to for weather
                location: (latitude, longitude). Location to set environment to"""
        obs, info = self.env.reset(**kwargs)
        return self.observation(obs), info


class NPKDictObservationWrapper(gym.ObservationWrapper):
    """Wraps the observation in a dictionary for easy access to variables
    without relying on direct indexing
    """

    def __init__(self, env: gym.Env) -> None:
        """Initialize the :class:`NPKDictObservationWrapper` wrapper with an environment.

        Handles extended weather forecasts by appending an _i to all weather
        variables, where {i} is the day.

        Args:
            env: The environment to apply the wrapper
        """
        super().__init__(env)
        self.env = env
        if isinstance(self.env.unwrapped, Multi_NPK_Env):
            self.output_vars = []
            for i in range(self.env.unwrapped.num_farms):
                self.output_vars += [s + f"_{i}" for s in self.env.unwrapped.individual_vars]
            self.output_vars += self.env.unwrapped.shared_vars
        else:
            self.output_vars = self.env.unwrapped.output_vars
        self.forecast_vars = []

        self.weather_vars = self.env.unwrapped.weather_vars
        if self.env.unwrapped.forecast_length > 1:
            self.forecast_vars = []
            for i in range(1, self.env.unwrapped.forecast_length):
                self.forecast_vars += [s + f"_{i+1}" for s in self.weather_vars]
        self.forecast_vars += self.weather_vars
        if isinstance(self.env.unwrapped, Multi_NPK_Env):
            output_dict = [
                (f"{ov}_{i}", Box(low=-np.inf, high=np.inf, shape=(1,)))
                for ov in self.env.unwrapped.individual_vars
                for i in range(self.env.unwrapped.num_farms)
            ]
            [
                output_dict.append((ov, Box(low=-np.inf, high=np.inf, shape=(1,))))
                for ov in self.env.unwrapped.shared_vars
            ]
            weather_dict = [(wv, Box(low=-np.inf, high=np.inf, shape=(1,))) for wv in self.weather_vars]
        else:
            output_dict = [(ov, Box(low=-np.inf, high=np.inf, shape=(1,))) for ov in self.output_vars]
            weather_dict = [(wv, Box(low=-np.inf, high=np.inf, shape=(1,))) for wv in self.weather_vars]

        self.observation_space = Dict(
            dict(output_dict + weather_dict + [("DAYS", Box(low=-np.inf, high=np.inf, shape=(1,)))])
        )

    def observation(self, obs: np.ndarray) -> dict[str, float]:
        """Puts the outputted variables in a dictionary.

        Note that the dictionary must be in order of the variables. This will not
        be a problem if the output is taken directly from the environment which
        already enforces order.

        Args:
            observation
        """
        keys = self.output_vars + self.forecast_vars + ["DAYS"]
        return dict([(keys[i], obs[i]) for i in range(len(keys))])

    def reset(self, **kwargs: dict) -> tuple[np.ndarray, dict]:
        """Reset the environment to the initial state specified by the
        agromanagement, crop, and soil files.

        Args:
            **kwargs:
                year: year to reset enviroment to for weather
                location: (latitude, longitude). Location to set environment to"""

        obs, info = self.env.reset(**kwargs)
        return self.observation(obs), info


class NPKDictActionWrapper(gym.ActionWrapper):
    """Converts a wrapped action to an action interpretable by the simulator.

    This wrapper is necessary for all provided hand-crafted policies which return
    an action as a dictionary. See policies.py for more information.
    """

    def __init__(self, env: gym.Env) -> None:
        """Initialize the :class:`NPKDictActionWrapper` wrapper with an environment.

        Args:
            env: The environment to apply the wrapper
        """
        super().__init__(env)
        self.env = env
        self.num_fert = self.env.unwrapped.num_fert
        self.num_irrig = self.env.unwrapped.num_irrig

        # Harvesting environments
        if isinstance(self.env.unwrapped, Plant_NPK_Env):
            if isinstance(self.env.unwrapped, PP):
                self.action_space = gym.spaces.Dict({"null": Discrete(1), "plant": Discrete(1), "harvest": Discrete(1)})
            elif isinstance(self.env.unwrapped, LNPK):
                self.action_space = gym.spaces.Dict(
                    {
                        "null": Discrete(1),
                        "plant": Discrete(1),
                        "harvest": Discrete(1),
                        "n": Discrete(self.env.unwrapped.num_fert),
                        "p": Discrete(self.env.unwrapped.num_fert),
                        "k": Discrete(self.env.unwrapped.num_fert),
                    }
                )
            elif isinstance(self.env.unwrapped, LN):
                self.action_space = gym.spaces.Dict(
                    {
                        "null": Discrete(1),
                        "plant": Discrete(1),
                        "harvest": Discrete(1),
                        "n": Discrete(self.env.unwrapped.num_fert),
                    }
                )
            elif isinstance(self.env.unwrapped, LNW):
                self.action_space = gym.spaces.Dict(
                    {
                        "null": Discrete(1),
                        "plant": Discrete(1),
                        "harvest": Discrete(1),
                        "n": Discrete(self.env.unwrapped.num_fert),
                        "irrig": Discrete(self.env.unwrapped.num_irrig),
                    }
                )
            elif isinstance(self.env.unwrapped, LW):
                self.action_space = gym.spaces.Dict(
                    {
                        "null": Discrete(1),
                        "plant": Discrete(1),
                        "harvest": Discrete(1),
                        "irrig": Discrete(self.env.unwrapped.num_irrig),
                    }
                )
            elif isinstance(self.env.unwrapped, LNPKW):
                self.action_space = gym.spaces.Dict(
                    {
                        "null": Discrete(1),
                        "plant": Discrete(1),
                        "harvest": Discrete(1),
                        "n": Discrete(self.env.unwrapped.num_fert),
                        "p": Discrete(self.env.unwrapped.num_fert),
                        "k": Discrete(self.env.unwrapped.num_fert),
                        "irrig": Discrete(self.env.unwrapped.num_irrig),
                    }
                )

        elif isinstance(self.env.unwrapped, Harvest_NPK_Env):
            if isinstance(self.env.unwrapped, PP):
                self.action_space = gym.spaces.Dict({"null": Discrete(1), "plant": Discrete(1), "harvest": Discrete(1)})
            elif isinstance(self.env.unwrapped, LNPK):
                self.action_space = gym.spaces.Dict(
                    {
                        "null": Discrete(1),
                        "plant": Discrete(1),
                        "harvest": Discrete(1),
                        "n": Discrete(self.env.unwrapped.num_fert),
                        "p": Discrete(self.env.unwrapped.num_fert),
                        "k": Discrete(self.env.unwrapped.num_fert),
                    }
                )
            elif isinstance(self.env.unwrapped, LN):
                self.action_space = gym.spaces.Dict(
                    {
                        "null": Discrete(1),
                        "plant": Discrete(1),
                        "harvest": Discrete(1),
                        "n": Discrete(self.env.unwrapped.num_fert),
                    }
                )
            elif isinstance(self.env.unwrapped, LNW):
                self.action_space = gym.spaces.Dict(
                    {
                        "null": Discrete(1),
                        "plant": Discrete(1),
                        "harvest": Discrete(1),
                        "n": Discrete(self.env.unwrapped.num_fert),
                        "irrig": Discrete(self.env.unwrapped.num_irrig),
                    }
                )
            elif isinstance(self.env.unwrapped, LW):
                self.action_space = gym.spaces.Dict(
                    {
                        "null": Discrete(1),
                        "plant": Discrete(1),
                        "harvest": Discrete(1),
                        "irrig": Discrete(self.env.unwrapped.num_irrig),
                    }
                )
            elif isinstance(self.env.unwrapped, LNPKW):
                self.action_space = gym.spaces.Dict(
                    {
                        "null": Discrete(1),
                        "plant": Discrete(1),
                        "harvest": Discrete(1),
                        "n": Discrete(self.env.unwrapped.num_fert),
                        "p": Discrete(self.env.unwrapped.num_fert),
                        "k": Discrete(self.env.unwrapped.num_fert),
                        "irrig": Discrete(self.env.unwrapped.num_irrig),
                    }
                )
        # Default environments
        else:
            if isinstance(self.env.unwrapped, PP):
                self.action_space = gym.spaces.Dict({"null": Discrete(1), "n": Discrete(1)})
            elif isinstance(self.env.unwrapped, LNPK):
                self.action_space = gym.spaces.Dict(
                    {
                        "null": Discrete(1),
                        "n": Discrete(self.env.unwrapped.num_fert),
                        "p": Discrete(self.env.unwrapped.num_fert),
                        "k": Discrete(self.env.unwrapped.num_fert),
                    }
                )
            elif isinstance(self.env.unwrapped, LN):
                self.action_space = gym.spaces.Dict({"null": Discrete(1), "n": Discrete(self.env.unwrapped.num_fert)})
            elif isinstance(self.env.unwrapped, LNW):
                self.action_space = gym.spaces.Dict(
                    {
                        "null": Discrete(1),
                        "n": Discrete(self.env.unwrapped.num_fert),
                        "irrig": Discrete(self.env.unwrapped.num_irrig),
                    }
                )
            elif isinstance(self.env.unwrapped, LW):
                self.action_space = gym.spaces.Dict(
                    {"null": Discrete(1), "irrig": Discrete(self.env.unwrapped.num_irrig)}
                )
            elif isinstance(self.env.unwrapped, LNPKW):
                self.action_space = gym.spaces.Dict(
                    {
                        "null": Discrete(1),
                        "n": Discrete(self.env.unwrapped.num_fert),
                        "p": Discrete(self.env.unwrapped.num_fert),
                        "k": Discrete(self.env.unwrapped.num_fert),
                        "irrig": Discrete(self.env.unwrapped.num_irrig),
                    }
                )

    def action(self, act: dict) -> int:
        """
        Converts the dicionary action to an integer to be pased to the base
        environment.

        Args:
            action
        """
        if not isinstance(act, dict):
            msg = "Action must be of dictionary type. See README for more information"
            raise exc.ActionException(msg)
        else:
            act_vals = list(act.values())
            for v in act_vals:
                if not isinstance(v, int):
                    msg = "Action value must be of type int"
                    raise exc.ActionException(msg)
            if len(np.nonzero(act_vals)[0]) > 1:
                msg = "More than one non-zero action value for policy"
                raise exc.ActionException(msg)

            if len(np.nonzero(act_vals)[0]) == 0:
                return 0

        if not "n" in act.keys():
            msg = "Nitrogen action 'n' not included in action dictionary keys"
            raise exc.ActionException(msg)
        if not "p" in act.keys():
            msg = "Phosphorous action 'p' not included in action dictionary keys"
            raise exc.ActionException(msg)
        if not "k" in act.keys():
            msg = "Potassium action 'k' not included in action dictionary keys"
            raise exc.ActionException(msg)
        if not "irrig" in act.keys():
            msg = "Irrigation action 'irrig' not included in action dictionary keys"
            raise exc.ActionException(msg)

        # Planting Single Year environments
        if isinstance(self.env.unwrapped, Plant_NPK_Env):

            if not "plant" in act.keys():
                msg = "'plant' not included in action dictionary keys"
                raise exc.ActionException(msg)
            if not "harvest" in act.keys():
                msg = "'harvest' not included in action dictionary keys"
                raise exc.ActionException(msg)
            if len(act.keys()) != self.env.unwrapped.NUM_ACT:
                msg = "Incorrect action dictionary specification"
                raise exc.ActionException(msg)

            offsets = [1, 1, self.num_fert, self.num_fert, self.num_fert, self.num_irrig]
            act_values = [act["plant"], act["harvest"], act["n"], act["p"], act["k"], act["irrig"]]
            offset_flags = np.zeros(self.env.unwrapped.NUM_ACT)
            offset_flags[: np.nonzero(act_values)[0][0]] = 1

        # Harvesting Single Year environments
        elif isinstance(self.env.unwrapped, Harvest_NPK_Env):

            if not "harvest" in act.keys():
                msg = "'harvest' not included in action dictionary keys"
                raise exc.ActionException(msg)
            if len(act.keys()) != self.env.unwrapped.NUM_ACT:
                msg = "Incorrect action dictionary specification"
                raise exc.ActionException(msg)

            offsets = [1, self.num_fert, self.num_fert, self.num_fert, self.num_irrig]
            act_values = [act["harvest"], act["n"], act["p"], act["k"], act["irrig"]]
            offset_flags = np.zeros(self.env.unwrapped.NUM_ACT)
            offset_flags[: np.nonzero(act_values)[0][0]] = 1

        # Default environments
        else:
            if len(act.keys()) != self.env.unwrapped.NUM_ACT:
                msg = "Incorrect action dictionary specification"
                raise exc.ActionException(msg)

            offsets = [self.num_fert, self.num_fert, self.num_fert, self.num_irrig]
            act_values = [act["n"], act["p"], act["k"], act["irrig"]]
            offset_flags = np.zeros(self.env.unwrapped.NUM_ACT)
            offset_flags[: np.nonzero(act_values)[0][0]] = 1

        return np.sum(offsets * offset_flags) + act_values[np.nonzero(act_values)[0][0]]

    def reset(self, **kwargs: dict) -> tuple[np.ndarray, dict]:
        """
        Forward keyword environments to base env
        """
        return self.env.reset(**kwargs)


class RewardWrapper(gym.Wrapper, ABC):
    """Abstract class for all reward wrappers

    Given how the reward wrapper functions, it must be applied BEFORE any
    observation or action wrappers.

    This _validate() function ensures that is the case and will throw and error
    otherwise
    """

    def __init__(self, env: gym.Env) -> None:
        """Initialize the :class:`RewardWrapper` wrapper with an environment.

        Args:
            env: The environment to apply the wrapper
        """
        super().__init__(env)
        self._validate(env)
        self.env = env

    @abstractmethod
    def _get_reward(self, output: dict, act_tuple: tuple[int, int, int, int]) -> None:
        """
        The get reward function shaping the reward. Implement this.
        """
        pass

    def _validate(self, env: gym.Env):
        """Validates that the environment is not wrapped with an Observation or
        Action Wrapper

        Args:
            env: The environment to check
        """
        if isinstance(env, gym.ActionWrapper) or isinstance(env, gym.ObservationWrapper):
            msg = f"Cannot wrap a `{type(self)}` around `{type(env)}`. Wrap Env with `{type(self)}` before wrapping with `{type(env)}`."
            raise exc.WOFOSTGymError(msg)
        if isinstance(env, RewardWrapper):
            msg = "Cannot wrap environment with another reward wrapper."
            raise exc.WOFOSTGymError(msg)

    def step(self, action: int) -> tuple[np.ndarray, float, bool, bool, dict]:
        """Run one timestep of the environment's dynamics.

        Sends action to the WOFOST model and recieves the resulting observation
        which is then processed to the _get_reward() function and _process_output()
        function for a reward and observation

        Args:
            action: integer
        """
        if isinstance(action, dict):
            msg = f"Action must be of type `int` but is of type `dict`. Wrap environment in `pcse_gym.wrappers.NPKDictActionWrapper` before proceeding."
            raise Exception(msg)

        act_tuple = self.env.unwrapped._take_action(action)

        output = self.env.unwrapped._run_simulation()

        observation = self.env.unwrapped._process_output(output)

        reward = self._get_reward(output, act_tuple)

        # Terminate based on crop finishing
        if isinstance(self.env.unwrapped, Multi_NPK_Env):
            termination = np.prod(
                [
                    output[i][-1]["FIN"] == 1.0 or output[i][-1]["FIN"] is None
                    for i in range(self.env.unwrapped.num_farms)
                ]
            )
            if np.any([output[i][-1]["FIN"] is None for i in range(self.env.unwrapped.num_farms)]):
                observation = np.nan_to_num(observation)
        else:
            termination = output[-1]["FIN"] == 1.0 or output[-1]["FIN"] is None
            if output[-1]["FIN"] is None:
                observation = np.nan_to_num(observation)

        # Truncate based on soil end date
        truncation = self.env.unwrapped.date >= self.env.unwrapped.soil_end_date

        if isinstance(self.env.unwrapped, Multi_NPK_Env):
            self.env.unwrapped._log(
                [output[i][-1]["WSO"] for i in range(self.env.unwrapped.num_farms)], act_tuple, reward
            )
        else:
            self.env.unwrapped._log(output[-1]["WSO"], act_tuple, reward)

        return observation, reward, termination, truncation, self.env.unwrapped.log

    def reset(self, **kwargs: dict) -> tuple[np.ndarray, dict]:
        """
        Forward keyword environments to base env
        """
        return self.env.reset(**kwargs)


class RewardFertilizationCostWrapper(RewardWrapper):
    """Modifies the reward to be a function of how much fertilization and irrigation
    is applied
    """

    def __init__(self, env: gym.Env, args: Namespace) -> None:
        """Initialize the :class:`RewardFertilizationCostWrapper` wrapper with an environment.

        Args:
            env: The environment to apply the wrapper
            cost: The cost scaler to be used to scale the reward penalty
        """
        assert isinstance(
            args.cost, float
        ), f"Must specify `--cost` as type float when using `RewardFertilizationCostWrapper`"

        super().__init__(env)
        self.env = env

        self.cost = args.cost

    def _get_reward(self, output: dict, act_tuple: tuple[float, float, float, float]) -> float:
        """Gets the reward as a penalty based on the amount of NPK/Water applied

        Args:
            output: dict     - output from model
            act_tuple: tuple -  NPK/Water amounts"""
        act_tuple = tuple(float(x) for x in act_tuple)
        if isinstance(self.env.unwrapped, Multi_NPK_Env):
            reward = 0
            act_tuple
            for i in range(self.env.unwrapped.num_farms):
                reward += (
                    output[i][-1]["WSO"] - (np.sum(self.cost * np.array([act_tuple[:-1]])))
                    if output[i][-1]["WSO"] is not None
                    else -np.sum(self.cost * np.array([act_tuple[2:]]))
                )
        else:
            if self.env.unwrapped.NUM_ACT == 6:
                reward = (
                    output[-1]["WSO"] - (np.sum(self.cost * np.array([act_tuple[:-1]])))
                    if output[-1]["WSO"] is not None
                    else -np.sum(self.cost * np.array([act_tuple[2:]]))
                )
            elif self.env.unwrapped.NUM_ACT == 4:
                reward = (
                    output[-1]["WSO"] - (np.sum(self.cost * np.array([act_tuple[:-1]])))
                    if output[-1]["WSO"] is not None
                    else -np.sum(self.cost * np.array([act_tuple[2:]]))
                )
        return reward


class RewardFertilizationThresholdWrapper(RewardWrapper):
    """Modifies the reward to be a function with high penalties for if a
    threshold is crossed during fertilization or irrigation
    """

    def __init__(self, env: gym.Env, args: Namespace) -> None:
        """Initialize the :class:`RewardFertilizationThresholdWrapper` wrapper with an environment.

        Args:
            env: The environment to apply the wrapper
            max_n: Nitrogen threshold
            max_p: Phosphorous threshold
            max_k: Potassium threshold
            max_w: Irrigation threshold
        """
        assert isinstance(
            args.max_n, float
        ), f"Must specify `--max_n` as type float when using `RewardFertilizationThresholdWrapper`. Use `inf` for no threshold."
        assert isinstance(
            args.max_p, float
        ), f"Must specify `--max_p` as type float when using `RewardFertilizationThresholdWrapper`. Use `inf` for no threshold."
        assert isinstance(
            args.max_k, float
        ), f"Must specify `--max_k` as type float when using `RewardFertilizationThresholdWrapper`. Use `inf` for no threshold."
        assert isinstance(
            args.max_w, float
        ), f"Must specify `--max_w` as type float when using `RewardFertilizationThresholdWrapper`. Use `inf` for no threshold."
        super().__init__(env)
        self.env = env

        # Thresholds for nutrient application
        self.max_n = args.max_n
        self.max_p = args.max_p
        self.max_k = args.max_k
        self.max_w = args.max_w

        # Set the reward range in case of normalization
        self.reward_range = [4 * -1e4, 10000]

    def _get_reward(self, output: dict, act_tuple: tuple[float, float, float, float]) -> float:
        """Convert the reward by applying a high penalty if a fertilization
        threshold is crossed

        Args:
            output     - of the simulator
            act_tuple  - amount of NPK/Water applied
        """

        if output[-1]["TOTN"] > self.max_n and act_tuple[self.env.unwrapped.N] > 0:
            return -1e4 * act_tuple[self.env.unwrapped.N]
        if output[-1]["TOTP"] > self.max_p and act_tuple[self.env.unwrapped.P] > 0:
            return -1e4 * act_tuple[self.env.unwrapped.P]
        if output[-1]["TOTK"] > self.max_k and act_tuple[self.env.unwrapped.K] > 0:
            return -1e4 * act_tuple[self.env.unwrapped.K]
        if output[-1]["TOTIRRIG"] > self.max_w and act_tuple[self.env.unwrapped.I] > 0:
            return -1e4 * act_tuple[self.env.unwrapped.I]
        if isinstance(self.env.unwrapped, Multi_NPK_Env):
            rew = 0
            for i in range(self.env.unwrapped.num_farms):
                rew += output[i][-1]["WSO"] if output[i][-1]["WSO"] is not None else 0
            return rew
        else:
            return output[-1]["WSO"] if output[-1]["WSO"] is not None else 0


class RewardLimitedRunoffWrapper(RewardWrapper):
    """Modifies the reward to be a function with high penalties for if Nitrogen Runoff Occurs"""

    def __init__(self, env: gym.Env, args: Namespace) -> None:
        """Initialize the :class:`RewardFertilizationThresholdWrapper` wrapper with an environment.

        Args:
            env: The environment to apply the wrapper
        """
        super().__init__(env)
        self.env = env

        # Thresholds for nutrient application

        # Set the reward range in case of normalization
        self.reward_range = [4 * -1e5, 10000]

    def _get_reward(self, output: dict, act_tuple: tuple[float, float, float, float]) -> float:
        """Convert the reward by applying a high penalty if a fertilization
        threshold is crossed

        Args:
            output     - of the simulator
            act_tuple  - amount of NPK/Water applied
        """
        if output[-1]["RRUNOFF_N"] > 0:
            return -1e5 * output[-1]["RRUNOFF_N"]
        return output[-1]["WSO"] if output[-1]["WSO"] is not None else 0


class NormalizeObservation(gym.Wrapper):

    def __init__(self, env: gym.Env) -> None:
        """
        Initialize normalization wrapper
        """
        super().__init__(env)

        try:
            self.num_envs = self.get_wrapper_attr("num_envs")
            self.is_vector_env = self.get_wrapper_attr("is_vector_env")
        except AttributeError:
            self.num_envs = 1
            self.is_vector_env = False

        self.env = env
        self.output_vars = self.env.unwrapped.output_vars
        self.weather_vars = self.env.unwrapped.weather_vars

        if isinstance(self.env.unwrapped, Multi_NPK_Env):
            self.all_vars = self.env.unwrapped.crop_vars + self.weather_vars + ["DAYS"]
        else:
            self.all_vars = self.output_vars + self.weather_vars + ["DAYS"]

        self.ploader = self.env.unwrapped.ploader

        self.ranges = np.stack([self.ploader.get_range(k) for k in self.all_vars], dtype=np.float64)

        if hasattr(env, "reward_range"):
            self.reward_range = env.reward_range
        else:
            self.reward_range = [0, 10000]

    def normalize(self, obs: np.ndarray) -> np.ndarray:
        """
        Normalize the observation
        """

        obs = (obs - self.ranges[:, 0]) / (self.ranges[:, 1] - self.ranges[:, 0] + 1e-12)

        return obs

    def unnormalize(self, obs: np.ndarray) -> np.ndarray:
        """
        Normalize the observation
        """
        obs = obs * (self.ranges[:, 1] - self.reward_range[:, 0] + 1e-12) + self.ranges[:, 0]

        return obs

    def step(self, action: int) -> tuple[np.ndarray, float, bool, bool, dict]:
        """Steps through the environment and normalizes the observation."""
        obs, rews, terminateds, truncateds, infos = self.env.step(action)
        if self.is_vector_env:
            obs = self.normalize(obs)
        else:
            obs = self.normalize(np.array([obs]))[0]
        return obs, rews, terminateds, truncateds, infos

    def reset(self, **kwargs: dict) -> tuple[np.ndarray, dict]:
        """Resets the environment and normalizes the observation."""
        obs, info = self.env.reset(**kwargs)

        if self.is_vector_env:
            return self.normalize(obs), info
        else:
            return self.normalize(np.array([obs]))[0], info


class NormalizeReward(gym.Wrapper):

    def __init__(self, env: gym.Env) -> None:
        """
        Initialize normalization wrapper for rwards
        """
        super().__init__(env)

        try:
            self.num_envs = self.get_wrapper_attr("num_envs")
            self.is_vector_env = self.get_wrapper_attr("is_vector_env")
        except AttributeError:
            self.num_envs = 1
            self.is_vector_env = False

        if hasattr(env, "reward_range"):
            self.reward_range = env.reward_range
            if self.reward_range == (float("-inf"), float("inf")):
                self.reward_range = [0, 10000]
        else:
            self.reward_range = [0, 10000]

        if hasattr(env, "ranges"):
            self.ranges = env.ranges

    def unnormalize_obs(self, obs: np.ndarray) -> np.ndarray:
        """
        Normalize the observation
        """
        obs = obs * (self.ranges[:, 1] - self.ranges[:, 0] + 1e-12) + self.ranges[:, 0]

        return obs

    def step(self, action: int) -> tuple[np.ndarray, float, bool, bool, dict]:
        """Steps through the environment and normalizes the observation."""
        obs, rews, terminateds, truncateds, infos = self.env.step(action)
        if isinstance(rews, torch.Tensor):
            rews = rews.cpu()
        if self.is_vector_env:
            rews = self.normalize(rews)
        else:
            rews = self.normalize(np.array([rews]))[0]
        return obs, rews, terminateds, truncateds, infos

    def reset(self, **kwargs: dict) -> tuple[np.ndarray, dict]:
        """Resets the environment and normalizes the observation."""
        obs, info = self.env.reset(**kwargs)

        return obs, info

    def normalize(self, rews: float) -> float:
        """
        Normalize the observation
        """
        rews = (rews - self.reward_range[0]) / (self.reward_range[1] - self.reward_range[0] + 1e-12)

        return rews

    def unnormalize(self, rews: float) -> float:
        """
        Unnormalize the reward
        """
        rews = rews * (self.reward_range[1] - self.reward_range[0] + 1e-12) + self.reward_range[0]

        return rews

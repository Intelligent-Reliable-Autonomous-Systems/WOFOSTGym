import numpy as np
import gymnasium as gym
from stable_baselines3 import PPO
from stable_baselines3.common.evaluation import evaluate_policy
from stable_baselines3.ppo import MlpPolicy

from imitation.algorithms.adversarial.gail import GAIL as GAIL_ALG
from imitation.data import rollout
from imitation.data.wrappers import RolloutInfoWrapper
from imitation.policies.serialize import load_policy
from imitation.rewards.reward_nets import BasicRewardNet
from imitation.util.networks import RunningNorm
from imitation.util.util import make_vec_env

from .rl_utils import RL_Args, Agent, setup, eval_policy, make_demonstrations
from typing import Optional
from dataclasses import dataclass
import utils
import torch
import torch.nn as nn
import time

@dataclass
class Args(RL_Args):
    """GAIL demo batch size"""
    demo_batch_size : Optional[int] = 1024
    """ Replay buffer capacity"""
    gen_replay_buffer_capacity: Optional[int] = 512
    """Number of discriminator updates per round"""
    n_disc_updates_per_round: Optional[int] = 8
    """Training steps"""
    train_steps: Optional[int] = 50000
    """the learning rate of the optimizer"""
    num_envs: int = 1
    """Number of demonstrations"""
    num_demos: int = 100
    """Demo agent path"""
    demo_agent_path: Optional[str] = None
    """Demo agent type"""
    demo_agent_type: Optional[str] = None

class GAIL(nn.Module):

    def __init__(self, envs, state_fpath:str=None, **kwargs):
        super().__init__()
        self.env = envs

        
        self.agent  = PPO(
            env=envs,
            policy=MlpPolicy,
            batch_size=64,
            ent_coef=0.0,
            learning_rate=0.0004,
            gamma=0.95,
            n_epochs=5,
            seed=0,
        )
        
        try:
            demo_batch_size=kwargs["demo_batch_size"]
            gen_replay_buffer_capacity=kwargs["gen_replay_buffer_capacity"]
            n_disc_updates_per_round=kwargs["n_disc_updates_per_round"]
            reward_net = kwargs["reward_net"]
        except:
            demo_batch_size=1024
            gen_replay_buffer_capacity=512
            n_disc_updates_per_round=8
            reward_net = BasicRewardNet(
                observation_space=envs.observation_space,
                action_space=envs.action_space,
                normalize_input_layer=RunningNorm,
                )
        self.gail_trainer = GAIL_ALG(
            demonstrations=None,
            demo_batch_size=demo_batch_size,
            gen_replay_buffer_capacity=gen_replay_buffer_capacity,
            n_disc_updates_per_round=n_disc_updates_per_round,
            venv=envs,
            gen_algo=self.agent,
            reward_net=reward_net,
        )

        self.policy = self.gail_trainer.gen_algo.policy

        if state_fpath is not None:
            assert isinstance(state_fpath, str), f"`state_fpath` must be of type `str` but is of type `{type(state_fpath)}`"
            try:
                self.policy = torch.load(state_fpath, weights_only=True)
            except:
                msg = f"Error loading state dictionary from {state_fpath}"
                raise Exception(msg)
        
    
    def train(self, train_steps:int):
        """
        Train the agent
        """
        self.gail_trainer.train(train_steps)  # Train for 800_000 steps to match expert.
        self.policy = self.gail_trainer.gen_algo.policy

    def get_action(self, x):
        """
        Helper function to get action for compatibility with generating data
        """
        if isinstance(x, np.ndarray):
            x = torch.tensor(x, dtype=torch.float32).to('cuda')
        return self.policy(x)[0]


def train(kwargs):

    args = kwargs.GAIL
    run_name = f"GAIL/{kwargs.env_id}__{args.exp_name}__{args.seed}__{int(time.time())}"
    
    writer, device, envs = setup(kwargs, args, run_name)

    reward_net = BasicRewardNet(
            observation_space=envs.observation_space,
            action_space=envs.action_space,
            normalize_input_layer=RunningNorm,
            )

    agent = GAIL(envs, reward_net=reward_net, demo_batch_size=args.demo_batch_size, gen_replay_buffer_capacity=args.gen_replay_buffer_capacity, n_disc_updates_per_round=args.n_disc_updates_per_round)
    # Initialize demonstration agent
    # Get the agent constructor from RL_Algs
    try:
        ag_constr = utils.get_valid_agents()[args.demo_agent_type]
        policy = ag_constr(envs)
    except:
        msg = "Error in getting agent. Check that `--args.agent-type` is a valid agent in rl_algs/"
        raise Exception(msg)

    device = torch.device("cuda" if torch.cuda.is_available() and args.cuda else "cpu")

    try:
        policy.load_state_dict(torch.load(f"{args.demo_agent_path}", map_location=device, weights_only=True))
    except:
        msg = "Error in loading state dict. Likely caused by loading an agent.pt file with incompatible `args.agent_type`"
        raise Exception(msg)
    policy.to(device)

    transitions = make_demonstrations(policy, envs, args.num_demos)

    agent.gail_trainer.set_demonstrations(transitions)

    agent.train(args.train_steps)
    
    torch.save(agent.gail_trainer.gen_algo.policy.state_dict(), f"{kwargs.save_folder}{run_name}/agent.pt")

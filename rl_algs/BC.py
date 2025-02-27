import numpy as np
import gymnasium as gym
import torch.nn as nn
import torch
from stable_baselines3.common.evaluation import evaluate_policy

from imitation.algorithms import bc
from typing import Optional
from dataclasses import dataclass
import time
import utils

from .rl_utils import RL_Args, Agent, setup, eval_policy, make_demonstrations



@dataclass
class Args(RL_Args):
    """Number of Epochs"""
    n_epochs: Optional[int] = 50
    """Number of Batches"""
    n_batches: Optional[int] = None
    """Log interval"""
    log_interval: int = 500
    """Number of rollouts to use when computing stats"""
    log_rollouts_n_episodes: int = 5
    """Show BC progress bar"""
    progress_bar: bool = False
    """Reset tensorboard"""
    reset_tensorboard: bool = True
    """the learning rate of the optimizer"""
    num_envs: int = 1
    """Number of demonstrations"""
    num_demos: int = 100
    """Demo agent path"""
    demo_agent_path: Optional[str] = None
    """Demo agent type"""
    demo_agent_type: Optional[str] = None


class BC(nn.Module):

    def __init__(self, envs, state_fpath:str=None, **kwargs):
        super().__init__()
        self.env = envs

        self.bc_trainer = bc.BC(
                observation_space=envs.envs[0].observation_space,
                action_space=envs.envs[0].action_space,
                rng = np.random.default_rng(0)
                )
        
        self.policy = self.bc_trainer.policy

        if state_fpath is not None:
            assert isinstance(state_fpath, str), f"`state_fpath` must be of type `str` but is of type `{type(state_fpath)}`"
            try:
                self.policy = torch.load(state_fpath, weights_only=True)
            except:
                msg = f"Error loading state dictionary from {state_fpath}"
                raise Exception(msg)
        
    
    def train(self, n_epochs:int, n_batches:int, log_interval:int, log_rollouts_n_episodes:int, progress_bar:bool, reset_tensorboard:bool):
        """
        Train the agent
        """
        self.bc_trainer.train(n_epochs=n_epochs, n_batches=n_batches, log_interval=log_interval, \
                              log_rollouts_n_episodes=log_rollouts_n_episodes, progress_bar=progress_bar, reset_tensorboard=reset_tensorboard)
        self.policy = self.bc_trainer.policy

    def get_action(self, x):
        """
        Helper function to get action for compatibility with generating data
        """
        if isinstance(x, np.ndarray):
            x = torch.tensor(x, dtype=torch.float32).to('cuda')
        return self.policy(x)[0]

def train(kwargs):

    args = kwargs.BC
    run_name = f"BC/{kwargs.env_id}__{args.exp_name}__{args.seed}__{int(time.time())}"
    
    writer, device, envs = setup(kwargs, args, run_name)

    agent = BC(envs).to(device)


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
    agent.bc_trainer.set_demonstrations(transitions)
    agent.train(n_epochs=args.n_epochs, n_batches=args.n_batches, log_interval=args.log_interval, log_rollouts_n_episodes=args.log_rollouts_n_episodes, progress_bar=args.progress_bar, reset_tensorboard=args.reset_tensorboard)


    torch.save(agent.policy.state_dict(), f"{kwargs.save_folder}{run_name}/agent.pt")


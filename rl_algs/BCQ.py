"""
Code to train a BCQ Agent
Docs: https://github.com/sfujim/BCQ
Modified to fit CleanRL format, Will Solow, 2024
"""

from argparse import Namespace
import numpy as np
import gymnasium as gym
import time
from dataclasses import dataclass
import torch
import wandb
import torch.nn as nn
from stable_baselines3.common.buffers import ReplayBuffer
import torch.optim as optim
import torch.nn.functional as F

from rl_algs.rl_utils import load_data_to_buffer, RL_Args, Agent, setup


@dataclass
class Args(RL_Args):

    # Algorithm specific arguments
    start_timesteps: int = 100
    """Starting time steps"""
    max_timesteps: int = 1000000
    """Maximum episodes"""
    num_envs: int = 1
    """the number of parallel game environments"""
    bcq_threshold: float = 0.3
    """Threshold parameter for BCQ"""
    initial_eps: float = 0.1
    """Initial eps"""
    end_eps: float = 0.1
    """Ending eps"""
    eps_decay_period: float = 1
    """Period over which eps decays"""
    eval_eps: int = 0
    """Evalutation of EPS"""
    gamma: float = 0.99
    """Gamma discount factor"""
    buffer_size: int = 10000
    """the replay memory buffer size"""
    batch_size: int = 64
    """Batch size"""
    learning_rate: float = 3e-4
    """Learning rate"""
    polyak_target_update: bool = True
    """Target updating"""
    target_update_freq: int = 1
    """Target updating frequency"""
    tau: float = 0.005
    """Tau value"""
    checkpoint_frequency: int = 50
    """How often to save the agent during training"""
    eval_freq: int = 5000
    """How often to evaluate the policy"""


class BCQ(nn.Module, Agent):
    def __init__(self, env: gym.Env, state_fpath: str = None, **kwargs: dict) -> None:
        super(BCQ, self).__init__()
        self.env = env
        self.q1 = nn.Linear(np.array(env.single_observation_space.shape).prod(), 256)
        self.q2 = nn.Linear(256, 256)
        self.q3 = nn.Linear(256, env.single_action_space.n)

        self.i1 = nn.Linear(np.array(env.single_observation_space.shape).prod(), 256)
        self.i2 = nn.Linear(256, 256)
        self.i3 = nn.Linear(256, env.single_action_space.n)

        if state_fpath is not None:
            assert isinstance(
                state_fpath, str
            ), f"`state_fpath` must be of type `str` but is of type `{type(state_fpath)}`"
            try:
                self.load_state_dict(torch.load(state_fpath, weights_only=True))
            except:
                msg = f"Error loading state dictionary from {state_fpath}"
                raise Exception(msg)

    def forward(self, state: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        q = F.relu(self.q1(state))
        q = F.relu(self.q2(q))

        i = F.relu(self.i1(state))
        i = F.relu(self.i2(i))
        i = self.i3(i)
        return self.q3(q), F.log_softmax(i, dim=-1), i

    def get_action(self, state: torch.Tensor) -> int:
        """
        Get best action deterministically. Compatibility function for generating data
        """
        q, imt, i = self.forward(state)
        imt = imt.exp()
        imt = (imt / imt.max(-1, keepdim=True)[0] > 0.3).float()

        return int((imt * q + (1.0 - imt) * -1e8).argmax(-1))

    def select_action(self, args: Namespace, device: torch.device, state: torch.Tensor) -> int:
        """
        Select action according to policy with probability (1-eps)
        otherwise, select random action
        """
        if np.random.uniform(0, 1) > args.eval_eps:
            with torch.no_grad():
                state = torch.FloatTensor(state).reshape((-1, *self.env.single_observation_space.shape)).to(device)
                q, imt, i = self.forward(state)
                imt = imt.exp()
                imt = (imt / imt.max(1, keepdim=True)[0] > args.bcq_threshold).float()

                return int((imt * q + (1.0 - imt) * -1e8).argmax(1))
        else:
            return np.random.randint(self.env.single_action_space.n)


def eval_policy(
    policy: Agent, eval_env: gym.Env, args: Namespace, device: torch.device, eval_episodes: int = 10
) -> float:
    """
    Runs policy x times on evaluation environment
    """
    avg_reward = 0.0
    for _ in range(eval_episodes):

        state, _, term, trunc = *eval_env.reset(), False, False

        while not (term or trunc):
            action = policy.select_action(args, device, np.array(state))
            state, reward, term, trunc, _ = eval_env.step(action)
            avg_reward += reward

    avg_reward /= eval_episodes

    return avg_reward


def train(kwargs: Namespace) -> None:
    """
    BCQ Training function
    """
    args = kwargs.alg

    assert args.num_envs == 1, "vectorized envs are not supported at the moment"
    run_name = f"BCQ/{kwargs.env_id}__{args.exp_name}__{args.seed}__{int(time.time())}"

    writer, device, envs = setup(kwargs, args, run_name)

    q_network = BCQ(envs).to(device)
    optimizer = optim.Adam(q_network.parameters(), lr=args.learning_rate)
    target_network = BCQ(envs).to(device)
    target_network.load_state_dict(q_network.state_dict())

    rb = ReplayBuffer(
        args.buffer_size,
        envs.single_observation_space,
        envs.single_action_space,
        device,
        handle_timeout_termination=False,
    )
    rb = load_data_to_buffer(envs.envs[0], kwargs.data_file, rb)

    start_time = time.time()

    for global_step in range(args.max_timesteps):

        if global_step % args.checkpoint_frequency == 0:
            torch.save(q_network.state_dict(), f"{kwargs.save_folder}{run_name}/agent.pt")
            if kwargs.track:
                wandb.save(f"{wandb.run.dir}/agent.pt", policy="now")

        data = rb.sample(args.batch_size)

        with torch.no_grad():
            q, imt, i = q_network(data.next_observations)
            imt = imt.exp()
            imt = (imt / imt.max(1, keepdim=True)[0] > args.bcq_threshold).float()

            next_action = (imt * q + (1 - imt) * -1e8).argmax(1, keepdim=True)

            q, imt, i = target_network(data.next_observations)
            target_Q = data.rewards + data.dones * args.gamma * q.gather(1, next_action).reshape(-1, 1)

        current_Q, imt, i = q_network(data.observations)
        current_Q = current_Q.gather(1, data.actions)

        q_loss = F.smooth_l1_loss(current_Q, target_Q)
        i_loss = F.nll_loss(imt, data.actions.reshape(-1))

        Q_loss = q_loss + i_loss + 1e-2 * i.pow(2).mean()

        optimizer.zero_grad()
        Q_loss.backward()
        optimizer.step()

        if args.polyak_target_update:
            for param, target_param in zip(q_network.parameters(), target_network.parameters()):
                target_param.data.copy_(args.tau * param.data + (1 - args.tau) * target_param.data)
        else:
            if global_step % args.target_update_frequency == 0:
                target_network.load_state_dict(q_network.state_dict())

        if global_step % args.eval_freq == 0:
            writer.add_scalar("losses/q_loss", q_loss, global_step)
            writer.add_scalar("losses/i_loss", i_loss, global_step)
            writer.add_scalar("losses/Q_loss", Q_loss, global_step)
            writer.add_scalar("charts/SPS", int(global_step / (time.time() - start_time)), global_step)
            writer.add_scalar("charts/average_return", eval_policy(q_network, envs.envs[0], args, device), global_step)

    envs.close()
    writer.close()

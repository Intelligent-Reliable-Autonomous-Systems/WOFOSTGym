"""File for training a Deep RL Agent
Agents Supported:
 - PPO
 - RPPO
 - SAC
 - DQN
 - BCQ
 - AIRL
 - GAIL
 - BC

Written by: Will Solow, 2024

To run: python3 train_agent.py --agent-type <Agent Type> --save-folder <logs>
"""

import tyro
from dataclasses import dataclass

import utils
from typing import Optional

@dataclass
class AlgArgs:
    pass

@dataclass
class AgentArgs(utils.Args):
    # Agent Args configurations
    alg: object = AlgArgs
    """Agent Type: RPPO | PPO | DQN | SAC| BCQ | etc"""
    agent_type: Optional[str] = None

    """Tracking Flag, if True will Track using Weights and Biases"""
    track: bool = False

    """Render mode, default to None for no rendering"""
    render_mode: Optional[str] = None


if __name__ == "__main__":

    args = tyro.cli(AgentArgs)

    try:
        ag_trainer, alg_args = utils.get_valid_trainers()
        ag_trainer = ag_trainer[args.agent_type]
        alg_args = alg_args[args.agent_type]
    except:
        msg = "Error in getting agent trainer. Check that `--args.agent-type` is a valid agent in rl_algs/ and that <agent-type.py> contains valid train() function."
        raise Exception(msg)
    
    args.alg = alg_args()
    ag_trainer(args)

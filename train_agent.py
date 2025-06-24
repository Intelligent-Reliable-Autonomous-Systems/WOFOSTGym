"""File for training a Deep RL Agent
Agents Supported:
 - PPO
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
from dataclasses import dataclass, field

from rl_algs.RPPO import Args as RPPO_Args
from rl_algs.PPO import Args as PPO_Args
from rl_algs.SAC import Args as SAC_Args
from rl_algs.DQN import Args as DQN_Args
from rl_algs.BCQ import Args as BCQ_Args
from rl_algs.BC import Args as BC_Args
from rl_algs.GAIL import Args as GAIL_Args
from rl_algs.AIRL import Args as AIRL_Args
import utils
from typing import Optional


@dataclass
class AgentArgs(utils.Args):
    # Agent Args configurations
    """Algorithm Parameters for PPO"""
    PPO: PPO_Args = field(default_factory=PPO_Args)
    """Algorithm Parameters for Recurrent-PPO"""
    RPPO: RPPO_Args = field(default_factory=RPPO_Args)
    """Algorithm Parameters for DQN"""
    DQN: DQN_Args = field(default_factory=DQN_Args)
    """Algorithm Parameters for SAC"""
    SAC: SAC_Args = field(default_factory=SAC_Args)
    """Algorithm Parameters for BCQ"""
    BCQ: BCQ_Args = field(default_factory=BCQ_Args)
    """Algorithm parameters for BC"""
    BC: BC_Args = field(default_factory=BC_Args)
    """Algorithm parameters for GAIL"""
    GAIL: GAIL_Args = field(default_factory=GAIL_Args)
    """Algorithm parameters for AIRL"""
    AIRL: AIRL_Args = field(default_factory=AIRL_Args)
    """Agent Type: RPPO | PPO | DQN | SAC| BCQ | etc"""
    agent_type: Optional[str] = None

    """Tracking Flag, if True will Track using Weights and Biases"""
    track: bool = False

    """Render mode, default to None for no rendering"""
    render_mode: Optional[str] = None


if __name__ == "__main__":

    args = tyro.cli(AgentArgs)

    try:
        ag_trainer = utils.get_valid_trainers()[args.agent_type]
    except:
        msg = "Error in getting agent trainer. Check that `--args.agent-type` is a valid agent in rl_algs/ and that <agent-type.py> contains valid train() function."
        raise Exception(msg)

    ag_trainer(args)

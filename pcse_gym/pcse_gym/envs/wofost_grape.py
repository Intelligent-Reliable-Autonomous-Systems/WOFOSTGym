"""Main API for default WOFOST Gym environments with actions for NPK and water
application.

Used for Grape crop simulations.

Written by Will Solow, 2024
"""

import gymnasium as gym

from pcse_gym.args import NPK_Args
from pcse_gym import utils
from pcse_gym.envs.wofost_base import NPK_Env
from pcse_gym.envs.wofost_base import LNPKW, LNPK, PP, LNW, LN, LW

import pcse
from pcse.soil.soil_wrappers import SoilModuleWrapper_LNPKW
from pcse.soil.soil_wrappers import SoilModuleWrapper_LN
from pcse.soil.soil_wrappers import SoilModuleWrapper_LNPK
from pcse.soil.soil_wrappers import SoilModuleWrapper_PP
from pcse.soil.soil_wrappers import SoilModuleWrapper_LW
from pcse.soil.soil_wrappers import SoilModuleWrapper_LNW

from pcse.soil.soil_wrappers import LayeredSoilModuleWrapper_LNPKW
from pcse.soil.soil_wrappers import LayeredSoilModuleWrapper_LN
from pcse.soil.soil_wrappers import LayeredSoilModuleWrapper_LNPK
from pcse.soil.soil_wrappers import LayeredSoilModuleWrapper_PP
from pcse.soil.soil_wrappers import LayeredSoilModuleWrapper_LW
from pcse.soil.soil_wrappers import LayeredSoilModuleWrapper_LNW

from pcse.crop.wofost8 import Wofost80Grape
from pcse.agromanager import AgroManagerPerennial


class Grape_Limited_NPKW_Env(NPK_Env, LNPKW):
    """Simulates crop growth under NPK and water limited conditions"""

    config = utils.make_config(soil=SoilModuleWrapper_LNPKW, crop=Wofost80Grape, agro=AgroManagerPerennial)

    def __init__(
        self,
        args: NPK_Args,
        base_fpath: str,
        agro_fpath: str,
        site_fpath: str,
        crop_fpath: str,
        name_fpath: str,
        unit_fpath: str,
        range_fpath: str,
        render_mode: str = None,
        config: dict = None,
    ):
        """Initialize the :class:`Limited_NPKW_Env`.

        Args:
            NPK_Args: The environment parameterization
        """
        self.perennial_env = True
        self.grape_env = True
        super().__init__(
            args,
            base_fpath,
            agro_fpath,
            site_fpath,
            crop_fpath,
            name_fpath,
            unit_fpath,
            range_fpath,
            render_mode,
            config=self.config,
        )

        self.action_space = gym.spaces.Discrete(1 + 3 * self.num_fert + self.num_irrig)

    def _take_action(self, action: int):
        """Controls sending fertilization and irrigation signals to the model.
        Converts the integer action to a signal and amount of NPK/Water to be applied.

        Args:
            action
        """
        n_amount = 0
        p_amount = 0
        k_amount = 0
        i_amount = 0

        # Null action
        if action == 0:
            return (n_amount, p_amount, k_amount, i_amount)

        # Irrigation action
        if action >= 3 * self.num_fert + 1:
            i_amount = action - (3 * self.num_fert)
            i_amount = i_amount * self.irrig_amount
            self.model._send_signal(signal=pcse.signals.irrigate, amount=i_amount, efficiency=self.irrig_effec)
            return (n_amount, p_amount, k_amount, i_amount)

        # Fertilizaiton action, correct for null action
        if (action - 1) // self.num_fert == 0:
            n_amount = self.fert_amount * (((action - 1) % self.num_fert) + 1)
            self.model._send_signal(signal=pcse.signals.apply_npk, N_amount=n_amount, N_recovery=self.n_recovery)
        elif (action - 1) // self.num_fert == 1:
            p_amount = self.fert_amount * (((action - 1) % self.num_fert) + 1)
            self.model._send_signal(signal=pcse.signals.apply_npk, P_amount=p_amount, P_recovery=self.p_recovery)
        elif (action - 1) // self.num_fert == 2:
            k_amount = self.fert_amount * (((action - 1) % self.num_fert) + 1)
            self.model._send_signal(signal=pcse.signals.apply_npk, K_amount=k_amount, K_recovery=self.k_recovery)

        return (n_amount, p_amount, k_amount, i_amount)


class Grape_PP_Env(NPK_Env, PP):
    """Simulates Potential Production. That is how much the crop would grow
    with abundant NPK/Water
    """

    config = utils.make_config(soil=SoilModuleWrapper_PP, crop=Wofost80Grape, agro=AgroManagerPerennial)

    def __init__(
        self,
        args: NPK_Args,
        base_fpath: str,
        agro_fpath: str,
        site_fpath: str,
        crop_fpath: str,
        name_fpath: str,
        unit_fpath: str,
        range_fpath: str,
        render_mode: str = None,
        config: dict = None,
    ):
        """Initialize the :class:`PP_Env`.

        Args:
            NPK_Args: The environment parameterization
        """
        self.perennial_env = True
        self.grape_env = True
        super().__init__(
            args,
            base_fpath,
            agro_fpath,
            site_fpath,
            crop_fpath,
            name_fpath,
            unit_fpath,
            range_fpath,
            render_mode,
            config=self.config,
        )

        self.action_space = gym.spaces.Discrete(1)

    def _take_action(self, action: int):
        """Controls sending fertilization and irrigation signals to the model.
        Converts the integer action to a signal and amount of NPK/Water to be applied.

        No actions available in this Potential Production Env

        Args:
            action
        """
        return (0, 0, 0, 0)


class Grape_Limited_NPK_Env(NPK_Env, LNPK):
    """Simulates crop growth under NPK Limited Production"""

    config = utils.make_config(soil=SoilModuleWrapper_LNPK, crop=Wofost80Grape, agro=AgroManagerPerennial)

    def __init__(
        self,
        args: NPK_Args,
        base_fpath: str,
        agro_fpath: str,
        site_fpath: str,
        crop_fpath: str,
        name_fpath: str,
        unit_fpath: str,
        range_fpath: str,
        render_mode: str = None,
        config: dict = None,
    ):
        """Initialize the :class:`Limited_NPK_Env`.

        Args:
            NPK_Args: The environment parameterization
        """
        self.perennial_env = True
        self.grape_env = True
        super().__init__(
            args,
            base_fpath,
            agro_fpath,
            site_fpath,
            crop_fpath,
            name_fpath,
            unit_fpath,
            range_fpath,
            render_mode,
            config=self.config,
        )

        self.action_space = gym.spaces.Discrete(1 + 3 * self.num_fert)

    def _take_action(self, action: int):
        """Controls sending fertilization and irrigation signals to the model.
        Converts the integer action to a signal and amount of NPK/Water to be applied.

        Args:
            action
        """
        n_amount = 0
        p_amount = 0
        k_amount = 0

        # Null action
        if action == 0:
            return (n_amount, p_amount, k_amount, 0)

        # Fertilizaiton action, correct for null action
        if (action - 1) // self.num_fert == 0:
            n_amount = self.fert_amount * (((action - 1) % self.num_fert) + 1)
            self.model._send_signal(signal=pcse.signals.apply_npk, N_amount=n_amount, N_recovery=self.n_recovery)
        elif (action - 1) // self.num_fert == 1:
            p_amount = self.fert_amount * (((action - 1) % self.num_fert) + 1)
            self.model._send_signal(signal=pcse.signals.apply_npk, P_amount=p_amount, P_recovery=self.p_recovery)
        elif (action - 1) // self.num_fert == 2:
            k_amount = self.fert_amount * (((action - 1) % self.num_fert) + 1)
            self.model._send_signal(signal=pcse.signals.apply_npk, K_amount=k_amount, K_recovery=self.k_recovery)

        return (n_amount, p_amount, k_amount, 0)


class Grape_Limited_N_Env(NPK_Env, LN):
    """Simulates crop growth under Nitrogen Limited Production"""

    config = utils.make_config(soil=SoilModuleWrapper_LN, crop=Wofost80Grape, agro=AgroManagerPerennial)

    def __init__(
        self,
        args: NPK_Args,
        base_fpath: str,
        agro_fpath: str,
        site_fpath: str,
        crop_fpath: str,
        name_fpath: str,
        unit_fpath: str,
        range_fpath: str,
        render_mode: str = None,
        config: dict = None,
    ):
        """Initialize the :class:`Limited_N_Env`.

        Args:
            NPK_Args: The environment parameterization
        """
        self.perennial_env = True
        self.grape_env = True
        super().__init__(
            args,
            base_fpath,
            agro_fpath,
            site_fpath,
            crop_fpath,
            name_fpath,
            unit_fpath,
            range_fpath,
            render_mode,
            config=self.config,
        )

        self.action_space = gym.spaces.Discrete(1 + self.num_fert)

    def _take_action(self, action: int):
        """Controls sending fertilization and irrigation signals to the model.
        Converts the integer action to a signal and amount of NPK/Water to be applied.

        Args:
            action
        """
        n_amount = 0

        # Null action
        if action == 0:
            return (n_amount, 0, 0, 0)

        # Fertilizaiton action, correct for null action
        if (action - 1) // self.num_fert == 0:
            n_amount = self.fert_amount * (((action - 1) % self.num_fert) + 1)
            self.model._send_signal(signal=pcse.signals.apply_npk, N_amount=n_amount, N_recovery=self.n_recovery)

        return (n_amount, 0, 0, 0)


class Grape_Limited_NW_Env(NPK_Env, LNW):
    """Simulates crop growth under Nitrogen and Water Limited Production"""

    config = utils.make_config(soil=SoilModuleWrapper_LNW, crop=Wofost80Grape, agro=AgroManagerPerennial)

    def __init__(
        self,
        args: NPK_Args,
        base_fpath: str,
        agro_fpath: str,
        site_fpath: str,
        crop_fpath: str,
        name_fpath: str,
        unit_fpath: str,
        range_fpath: str,
        render_mode: str = None,
        config: dict = None,
    ):
        """Initialize the :class:`Limited_NW_Env`.

        Args:
            NPK_Args: The environment parameterization
        """
        self.perennial_env = True
        self.grape_env = True
        super().__init__(
            args,
            base_fpath,
            agro_fpath,
            site_fpath,
            crop_fpath,
            name_fpath,
            unit_fpath,
            range_fpath,
            render_mode,
            config=self.config,
        )

        self.action_space = gym.spaces.Discrete(1 + self.num_fert + self.num_irrig)

    def _take_action(self, action: int):
        """Controls sending fertilization and irrigation signals to the model.
        Converts the integer action to a signal and amount of NPK/Water to be applied.

        Args:
            action
        """
        n_amount = 0
        i_amount = 0

        # Null action
        if action == 0:
            return (n_amount, 0, 0, i_amount)

        # Irrigation action
        if action >= self.num_fert + 1:
            i_amount = action - (self.num_fert)
            i_amount = i_amount * self.irrig_amount
            self.model._send_signal(signal=pcse.signals.irrigate, amount=i_amount, efficiency=self.irrig_effec)
            return (n_amount, 0, 0, i_amount)

        # Fertilizaiton action, correct for null action
        if (action - 1) // self.num_fert == 0:
            n_amount = self.fert_amount * (((action - 1) % self.num_fert) + 1)
            self.model._send_signal(signal=pcse.signals.apply_npk, N_amount=n_amount, N_recovery=self.n_recovery)

        return (n_amount, 0, 0, i_amount)


class Grape_Limited_W_Env(NPK_Env, LW):
    """Simulates crop growth under Water Limited Production"""

    config = utils.make_config(soil=SoilModuleWrapper_LW, crop=Wofost80Grape, agro=AgroManagerPerennial)

    def __init__(
        self,
        args: NPK_Args,
        base_fpath: str,
        agro_fpath: str,
        site_fpath: str,
        crop_fpath: str,
        name_fpath: str,
        unit_fpath: str,
        range_fpath: str,
        render_mode: str = None,
        config: dict = None,
    ):
        """Initialize the :class:`Limited_W_Env`.

        Args:
            NPK_Args: The environment parameterization
        """
        self.perennial_env = True
        self.grape_env = True
        super().__init__(
            args,
            base_fpath,
            agro_fpath,
            site_fpath,
            crop_fpath,
            name_fpath,
            unit_fpath,
            range_fpath,
            render_mode,
            config=self.config,
        )

        self.action_space = gym.spaces.Discrete(1 + self.num_irrig)

    def _take_action(self, action: int):
        """Controls sending fertilization and irrigation signals to the model.
        Converts the integer action to a signal and amount of NPK/Water to be applied.

        Args:
            action
        """
        irrig_amount = action
        # Null action
        if action == 0:
            return (0, 0, 0, i_amount)

        # Irrigation action
        if action >= 0 * self.num_fert + 1:
            i_amount = action - (0 * self.num_fert)
            i_amount = i_amount * self.irrig_amount
            self.model._send_signal(signal=pcse.signals.irrigate, amount=i_amount, efficiency=self.irrig_effec)

        return (0, 0, 0, i_amount)


class Grape_Limited_Layered_NPKW_Env(NPK_Env, LNPKW):
    """Simulates crop growth under NPK and water limited conditions with layerd water balance"""

    config = utils.make_config(soil=LayeredSoilModuleWrapper_LNPKW, crop=Wofost80Grape, agro=AgroManagerPerennial)

    def __init__(
        self,
        args: NPK_Args,
        base_fpath: str,
        agro_fpath: str,
        site_fpath: str,
        crop_fpath: str,
        name_fpath: str,
        unit_fpath: str,
        range_fpath: str,
        render_mode: str = None,
        config: dict = None,
    ):
        """Initialize the :class:`Limited_NPKW_Env`.

        Args:
            NPK_Args: The environment parameterization
        """
        self.perennial_env = True
        self.grape_env = True
        super().__init__(
            args,
            base_fpath,
            agro_fpath,
            site_fpath,
            crop_fpath,
            name_fpath,
            unit_fpath,
            range_fpath,
            render_mode,
            config=self.config,
        )

        self.action_space = gym.spaces.Discrete(1 + 3 * self.num_fert + self.num_irrig)

    def _take_action(self, action: int):
        """Controls sending fertilization and irrigation signals to the model.
        Converts the integer action to a signal and amount of NPK/Water to be applied.

        Args:
            action
        """
        n_amount = 0
        p_amount = 0
        k_amount = 0
        i_amount = 0

        # Null action
        if action == 0:
            return (n_amount, p_amount, k_amount, i_amount)

        # Irrigation action
        if action >= 3 * self.num_fert + 1:
            i_amount = action - (3 * self.num_fert)
            i_amount = i_amount * self.irrig_amount
            self.model._send_signal(signal=pcse.signals.irrigate, amount=i_amount, efficiency=self.irrig_effec)
            return (n_amount, p_amount, k_amount, i_amount)

        # Fertilizaiton action, correct for null action
        if (action - 1) // self.num_fert == 0:
            n_amount = self.fert_amount * (((action - 1) % self.num_fert) + 1)
            self.model._send_signal(signal=pcse.signals.apply_npk, N_amount=n_amount, N_recovery=self.n_recovery)
        elif (action - 1) // self.num_fert == 1:
            p_amount = self.fert_amount * (((action - 1) % self.num_fert) + 1)
            self.model._send_signal(signal=pcse.signals.apply_npk, P_amount=p_amount, P_recovery=self.p_recovery)
        elif (action - 1) // self.num_fert == 2:
            k_amount = self.fert_amount * (((action - 1) % self.num_fert) + 1)
            self.model._send_signal(signal=pcse.signals.apply_npk, K_amount=k_amount, K_recovery=self.k_recovery)

        return (n_amount, p_amount, k_amount, i_amount)


class Grape_Layered_PP_Env(NPK_Env, PP):
    """Simulates Potential Production. That is how much the crop would grow
    with abundant NPK/Water with layered water balance
    """

    config = utils.make_config(soil=LayeredSoilModuleWrapper_PP, crop=Wofost80Grape, agro=AgroManagerPerennial)

    def __init__(
        self,
        args: NPK_Args,
        base_fpath: str,
        agro_fpath: str,
        site_fpath: str,
        crop_fpath: str,
        name_fpath: str,
        unit_fpath: str,
        range_fpath: str,
        render_mode: str = None,
        config: dict = None,
    ):
        """Initialize the :class:`PP_Env`.

        Args:
            NPK_Args: The environment parameterization
        """
        self.perennial_env = True
        self.grape_env = True
        super().__init__(
            args,
            base_fpath,
            agro_fpath,
            site_fpath,
            crop_fpath,
            name_fpath,
            unit_fpath,
            range_fpath,
            render_mode,
            config=self.config,
        )

        self.action_space = gym.spaces.Discrete(1)

    def _take_action(self, action: int):
        """Controls sending fertilization and irrigation signals to the model.
        Converts the integer action to a signal and amount of NPK/Water to be applied.

        No actions available in this Potential Production Env

        Args:
            action
        """
        return (0, 0, 0, 0)


class Grape_Limited_Layered_NPK_Env(NPK_Env, LNPK):
    """Simulates crop growth under NPK Limited Production with layered water balance"""

    config = utils.make_config(soil=LayeredSoilModuleWrapper_LNPK, crop=Wofost80Grape, agro=AgroManagerPerennial)

    def __init__(
        self,
        args: NPK_Args,
        base_fpath: str,
        agro_fpath: str,
        site_fpath: str,
        crop_fpath: str,
        name_fpath: str,
        unit_fpath: str,
        range_fpath: str,
        render_mode: str = None,
        config: dict = None,
    ):
        """Initialize the :class:`Limited_NPK_Env`.

        Args:
            NPK_Args: The environment parameterization
        """
        self.perennial_env = True
        self.grape_env = True
        super().__init__(
            args,
            base_fpath,
            agro_fpath,
            site_fpath,
            crop_fpath,
            name_fpath,
            unit_fpath,
            range_fpath,
            render_mode,
            config=self.config,
        )

        self.action_space = gym.spaces.Discrete(1 + 3 * self.num_fert)

    def _take_action(self, action: int):
        """Controls sending fertilization and irrigation signals to the model.
        Converts the integer action to a signal and amount of NPK/Water to be applied.

        Args:
            action
        """
        n_amount = 0
        p_amount = 0
        k_amount = 0

        # Null action
        if action == 0:
            return (n_amount, p_amount, k_amount, 0)

        # Fertilizaiton action, correct for null action
        if (action - 1) // self.num_fert == 0:
            n_amount = self.fert_amount * (((action - 1) % self.num_fert) + 1)
            self.model._send_signal(signal=pcse.signals.apply_npk, N_amount=n_amount, N_recovery=self.n_recovery)
        elif (action - 1) // self.num_fert == 1:
            p_amount = self.fert_amount * (((action - 1) % self.num_fert) + 1)
            self.model._send_signal(signal=pcse.signals.apply_npk, P_amount=p_amount, P_recovery=self.p_recovery)
        elif (action - 1) // self.num_fert == 2:
            k_amount = self.fert_amount * (((action - 1) % self.num_fert) + 1)
            self.model._send_signal(signal=pcse.signals.apply_npk, K_amount=k_amount, K_recovery=self.k_recovery)

        return (n_amount, p_amount, k_amount, 0)


class Grape_Limited_Layered_N_Env(NPK_Env, LN):
    """Simulates crop growth under Nitrogen Limited Production with layered water balance"""

    config = utils.make_config(soil=LayeredSoilModuleWrapper_LN, crop=Wofost80Grape, agro=AgroManagerPerennial)

    def __init__(
        self,
        args: NPK_Args,
        base_fpath: str,
        agro_fpath: str,
        site_fpath: str,
        crop_fpath: str,
        name_fpath: str,
        unit_fpath: str,
        range_fpath: str,
        render_mode: str = None,
        config: dict = None,
    ):
        """Initialize the :class:`Limited_N_Env`.

        Args:
            NPK_Args: The environment parameterization
        """
        self.perennial_env = True
        self.grape_env = True
        super().__init__(
            args,
            base_fpath,
            agro_fpath,
            site_fpath,
            crop_fpath,
            name_fpath,
            unit_fpath,
            range_fpath,
            render_mode,
            config=self.config,
        )

        self.action_space = gym.spaces.Discrete(1 + self.num_fert)

    def _take_action(self, action: int):
        """Controls sending fertilization and irrigation signals to the model.
        Converts the integer action to a signal and amount of NPK/Water to be applied.

        Args:
            action
        """
        n_amount = 0

        # Null action
        if action == 0:
            return (n_amount, 0, 0, 0)

        # Fertilizaiton action, correct for null action
        if (action - 1) // self.num_fert == 0:
            n_amount = self.fert_amount * (((action - 1) % self.num_fert) + 1)
            self.model._send_signal(signal=pcse.signals.apply_npk, N_amount=n_amount, N_recovery=self.n_recovery)

        return (n_amount, 0, 0, 0)


class Grape_Limited_Layered_NW_Env(NPK_Env, LNW):
    """Simulates crop growth under Nitrogen and Water Limited Production with layered water balance"""

    config = utils.make_config(soil=LayeredSoilModuleWrapper_LNW, crop=Wofost80Grape, agro=AgroManagerPerennial)

    def __init__(
        self,
        args: NPK_Args,
        base_fpath: str,
        agro_fpath: str,
        site_fpath: str,
        crop_fpath: str,
        name_fpath: str,
        unit_fpath: str,
        range_fpath: str,
        render_mode: str = None,
        config: dict = None,
    ):
        """Initialize the :class:`Limited_NW_Env`.

        Args:
            NPK_Args: The environment parameterization
        """
        self.perennial_env = True
        self.grape_env = True
        super().__init__(
            args,
            base_fpath,
            agro_fpath,
            site_fpath,
            crop_fpath,
            name_fpath,
            unit_fpath,
            range_fpath,
            render_mode,
            config=self.config,
        )

        self.action_space = gym.spaces.Discrete(1 + self.num_fert + self.num_irrig)

    def _take_action(self, action: int):
        """Controls sending fertilization and irrigation signals to the model.
        Converts the integer action to a signal and amount of NPK/Water to be applied.

        Args:
            action
        """
        n_amount = 0
        i_amount = 0

        # Null action
        if action == 0:
            return (n_amount, 0, 0, i_amount)

        # Irrigation action
        if action >= self.num_fert + 1:
            i_amount = action - (self.num_fert)
            i_amount = i_amount * self.irrig_amount
            self.model._send_signal(signal=pcse.signals.irrigate, amount=i_amount, efficiency=self.irrig_effec)
            return (n_amount, 0, 0, i_amount)

        # Fertilizaiton action, correct for null action
        if (action - 1) // self.num_fert == 0:
            n_amount = self.fert_amount * (((action - 1) % self.num_fert) + 1)
            self.model._send_signal(signal=pcse.signals.apply_npk, N_amount=n_amount, N_recovery=self.n_recovery)

        return (n_amount, 0, 0, i_amount)


class Grape_Limited_Layered_W_Env(NPK_Env, LW):
    """Simulates crop growth under Water Limited Production with layerd water balance"""

    config = utils.make_config(soil=LayeredSoilModuleWrapper_LW, crop=Wofost80Grape, agro=AgroManagerPerennial)

    def __init__(
        self,
        args: NPK_Args,
        base_fpath: str,
        agro_fpath: str,
        site_fpath: str,
        crop_fpath: str,
        name_fpath: str,
        unit_fpath: str,
        range_fpath: str,
        render_mode: str = None,
        config: dict = None,
    ):
        """Initialize the :class:`Limited_W_Env`.

        Args:
            NPK_Args: The environment parameterization
        """
        self.perennial_env = True
        self.grape_env = True
        super().__init__(
            args,
            base_fpath,
            agro_fpath,
            site_fpath,
            crop_fpath,
            name_fpath,
            unit_fpath,
            range_fpath,
            render_mode,
            config=self.config,
        )

        self.action_space = gym.spaces.Discrete(1 + self.num_irrig)

    def _take_action(self, action: int):
        """Controls sending fertilization and irrigation signals to the model.
        Converts the integer action to a signal and amount of NPK/Water to be applied.

        Args:
            action
        """
        irrig_amount = action
        # Null action
        if action == 0:
            return (0, 0, 0, i_amount)

        # Irrigation action
        if action >= 0 * self.num_fert + 1:
            i_amount = action - (0 * self.num_fert)
            i_amount = i_amount * self.irrig_amount
            self.model._send_signal(signal=pcse.signals.irrigate, amount=i_amount, efficiency=self.irrig_effec)

        return (0, 0, 0, i_amount)

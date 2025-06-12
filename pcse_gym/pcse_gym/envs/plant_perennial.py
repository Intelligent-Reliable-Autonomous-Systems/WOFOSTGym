"""Main API for simulating crop growth NPK fertilization and irrigation actions
and the inclusion of planting and harvesting of the crop.

Used for single year planting perennial crop simulations.

Written by Will Solow, 2024
"""

import gymnasium as gym

from pcse_gym import utils
from pcse_gym.args import NPK_Args
from pcse_gym.envs.wofost_base import Plant_NPK_Env
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

from pcse.crop.wofost8 import Wofost80Perennial
from pcse.agromanager import AgroManagerPlantPerennial


class Perennial_Plant_Limited_NPKW_Env(Plant_NPK_Env, LNPKW):
    """Simulates crop growth under NPK and Water Limited Production
    with actions for planting and harvesting
    """

    config = utils.make_config(soil=SoilModuleWrapper_LNPKW, crop=Wofost80Perennial, agro=AgroManagerPlantPerennial)

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
    ) -> None:
        """Initialize the :class:`Plant_Limited_NPKW_Env`.

        Args:
            NPK_Args: The environment parameterization
        """
        self.perennial_env = True
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

        self.action_space = gym.spaces.Discrete(3 + 3 * args.num_fert + args.num_irrig)

    def _take_action(self, action: int) -> tuple[float, float, float, float]:
        """Controls sending fertilization and irrigation signals to the model.
        Includes actions for planting and harvesting.
        Converts the integer action to a signal and amount of NPK/Water to be applied.

        Args:
            action
        """
        p_act = 0
        h_act = 0
        n_amount = 0
        p_amount = 0
        k_amount = 0
        i_amount = 0

        # Null Action
        if action == 0:
            return (p_act, h_act, n_amount, p_amount, k_amount, i_amount)

        # Planting action
        elif action == 1:
            if not self.active_crop_flag:
                self.model._send_signal(
                    signal=pcse.signals.crop_start,
                    crop_name=self.crop_name,
                    crop_variety=self.crop_variety,
                    crop_start_type=self.crop_start_type,
                    crop_end_type=self.crop_end_type,
                    day=self.date,
                )
                self.active_crop_flag = True
            p_act = 1
            return (p_act, h_act, n_amount, p_amount, k_amount, i_amount)

        # Harvesting Action
        elif action == 2:
            if self.active_crop_flag:
                self.model._send_signal(signal=pcse.signals.crop_harvest, day=self.date, effiency=self.Plant_effec)
            h_act = 1
            return (p_act, h_act, n_amount, p_amount, k_amount, i_amount)

        # Irrigation action
        if action >= 3 * self.num_fert + 3:
            i_amount = action - (3 * self.num_fert) - 2
            i_amount = i_amount * self.irrig_amount
            self.model._send_signal(signal=pcse.signals.irrigate, amount=i_amount, efficiency=self.irrig_effec)
            return (p_act, h_act, n_amount, p_amount, k_amount, i_amount)

        # Fertilizaiton action, correct for 2 crop specific actions (harvest/plant) and null action
        if action >= 3:
            action -= 3

            if action // self.num_fert == 0:
                n_amount = self.fert_amount * ((action % self.num_fert) + 1)
                self.model._send_signal(signal=pcse.signals.apply_npk, N_amount=n_amount, N_recovery=self.n_recovery)
            elif action // self.num_fert == 1:
                p_amount = self.fert_amount * ((action % self.num_fert) + 1)
                self.model._send_signal(signal=pcse.signals.apply_npk, P_amount=p_amount, P_recovery=self.p_recovery)
            elif action // self.num_fert == 2:
                k_amount = self.fert_amount * ((action % self.num_fert) + 1)
                self.model._send_signal(signal=pcse.signals.apply_npk, K_amount=k_amount, K_recovery=self.k_recovery)

        return (p_act, h_act, n_amount, p_amount, k_amount, i_amount)


class Perennial_Plant_PP_Env(Plant_NPK_Env, PP):
    """Simulates crop growth under abundant NPK and water
    with actions for planting and harvesting
    """

    config = utils.make_config(soil=SoilModuleWrapper_PP, crop=Wofost80Perennial, agro=AgroManagerPlantPerennial)

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
    ) -> None:
        """Initialize the :class:`Plant_PP_Env`.

        Args:
            NPK_Args: The environment parameterization
        """
        self.perennial_env = True
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

        self.action_space = gym.spaces.Discrete(3)

    def _take_action(self, action: int) -> tuple[float, float, float, float]:
        """Controls sending fertilization and irrigation signals to the model.
        Includes actions for planting and harvesting.
        Converts the integer action to a signal and amount of NPK/Water to be applied.

        Args:
            action
        """
        p_act = 0
        h_act = 0

        # Null Action
        if action == 0:
            return (p_act, h_act, 0, 0, 0, 0)

        # Planting action
        elif action == 1:
            if not self.active_crop_flag:
                self.model._send_signal(
                    signal=pcse.signals.crop_start,
                    crop_name=self.crop_name,
                    crop_variety=self.crop_variety,
                    crop_start_type=self.crop_start_type,
                    crop_end_type=self.crop_end_type,
                    day=self.date,
                )
                self.active_crop_flag = True
            p_act = 1
            return (p_act, h_act, 0, 0, 0, 0)

        # Harvesting Action
        elif action == 2:
            if self.active_crop_flag:
                self.model._send_signal(signal=pcse.signals.crop_harvest, day=self.date, effiency=self.Plant_effec)
            h_act = 1
            return (p_act, h_act, 0, 0, 0, 0)


class Perennial_Plant_Limited_NPK_Env(Plant_NPK_Env, LNPK):
    """Simulates crop growth under NPK Limited Production
    with actions for planting and harvesting
    """

    config = utils.make_config(soil=SoilModuleWrapper_LNPK, crop=Wofost80Perennial, agro=AgroManagerPlantPerennial)

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
    ) -> None:
        """Initialize the :class:`Plant_Limited_NPK_Env`.

        Args:
            NPK_Args: The environment parameterization
        """
        self.perennial_env = True
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

        self.action_space = gym.spaces.Discrete(3 + 3 * self.num_fert)

    def _take_action(self, action: int) -> tuple[float, float, float, float]:
        """Controls sending fertilization and irrigation signals to the model.
        Includes actions for planting and harvesting.
        Converts the integer action to a signal and amount of NPK/Water to be applied.

        Args:
            action
        """
        p_act = 0
        h_act = 0
        n_amount = 0
        p_amount = 0
        k_amount = 0

        # Null Action
        if action == 0:
            return (p_act, h_act, n_amount, p_amount, k_amount, 0)

        # Planting action
        elif action == 1:
            if not self.active_crop_flag:
                self.model._send_signal(
                    signal=pcse.signals.crop_start,
                    crop_name=self.crop_name,
                    crop_variety=self.crop_variety,
                    crop_start_type=self.crop_start_type,
                    crop_end_type=self.crop_end_type,
                    day=self.date,
                )
                self.active_crop_flag = True
            p_act = 1
            return (p_act, h_act, n_amount, p_amount, k_amount, 0)

        # Harvesting Action
        elif action == 2:
            if self.active_crop_flag:
                self.model._send_signal(signal=pcse.signals.crop_harvest, day=self.date, effiency=self.Plant_effec)
            h_act = 1
            return (p_act, h_act, n_amount, p_amount, k_amount, 0)

        # Fertilizaiton action, correct for 2 crop specific actions (harvest/plant) and null action
        if action >= 3:
            action -= 3
            if action // self.num_fert == 0:
                n_amount = self.fert_amount * ((action % self.num_fert) + 1)
                self.model._send_signal(signal=pcse.signals.apply_npk, N_amount=n_amount, N_recovery=self.n_recovery)
            elif action // self.num_fert == 1:
                p_amount = self.fert_amount * ((action % self.num_fert) + 1)
                self.model._send_signal(signal=pcse.signals.apply_npk, P_amount=p_amount, P_recovery=self.p_recovery)
            elif action // self.num_fert == 2:
                k_amount = self.fert_amount * ((action % self.num_fert) + 1)
                self.model._send_signal(signal=pcse.signals.apply_npk, K_amount=k_amount, K_recovery=self.k_recovery)

        return (p_act, h_act, n_amount, p_amount, k_amount, 0)


class Perennial_Plant_Limited_N_Env(Plant_NPK_Env, LN):
    """Simulates crop growth under Nitrogen Limited Production
    with actions for planting and harvesting
    """

    config = utils.make_config(soil=SoilModuleWrapper_LN, crop=Wofost80Perennial, agro=AgroManagerPlantPerennial)

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
    ) -> None:
        """Initialize the :class:`Plant_Limited_N_Env`.

        Args:
            NPK_Args: The environment parameterization
        """
        self.perennial_env = True
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
        self.action_space = gym.spaces.Discrete(3 + self.num_fert)

    def _take_action(self, action: int) -> tuple[float, float, float, float]:
        """Controls sending fertilization and irrigation signals to the model.
        Includes actions for planting and harvesting.
        Converts the integer action to a signal and amount of NPK/Water to be applied.

        Args:
            action
        """
        p_act = 0
        h_act = 0
        n_amount = 0

        # Null Action
        if action == 0:
            return (p_act, h_act, n_amount, 0, 0, 0)

        # Planting action
        elif action == 1:
            if not self.active_crop_flag:
                self.model._send_signal(
                    signal=pcse.signals.crop_start,
                    crop_name=self.crop_name,
                    crop_variety=self.crop_variety,
                    crop_start_type=self.crop_start_type,
                    crop_end_type=self.crop_end_type,
                    day=self.date,
                )
                self.active_crop_flag = True
            p_act = 1
            return (p_act, h_act, n_amount, 0, 0, 0)

        # Harvesting Action
        elif action == 2:
            if self.active_crop_flag:
                self.model._send_signal(signal=pcse.signals.crop_harvest, day=self.date, effiency=self.Plant_effec)
            h_act = 1
            return (p_act, h_act, n_amount, 0, 0, 0)

        # Fertilizaiton action, correct for 2 crop specific actions (harvest/plant) and null action
        if action >= 3:
            action -= 3
            if action // self.num_fert == 0:
                n_amount = self.fert_amount * ((action % self.num_fert) + 1)
                self.model._send_signal(signal=pcse.signals.apply_npk, N_amount=n_amount, N_recovery=self.n_recovery)

        return (p_act, h_act, n_amount, 0, 0, 0)


class Perennial_Plant_Limited_NW_Env(Plant_NPK_Env, LNW):
    """Simulates crop growth under Nitrogen and Water Limited Production
    with actions for planting and harvesting
    """

    config = utils.make_config(soil=SoilModuleWrapper_LNW, crop=Wofost80Perennial, agro=AgroManagerPlantPerennial)

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
    ) -> None:
        """Initialize the :class:`Plant_Limited_NW_Env`.

        Args:
            NPK_Args: The environment parameterization
        """
        self.perennial_env = True
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
        self.action_space = gym.spaces.Discrete(3 + self.num_fert + self.num_irrig)

    def _take_action(self, action: int) -> tuple[float, float, float, float]:
        """Controls sending fertilization and irrigation signals to the model.
        Includes actions for planting and harvesting.
        Converts the integer action to a signal and amount of NPK/Water to be applied.

        Args:
            action
        """
        p_act = 0
        h_act = 0
        n_amount = 0
        i_amount = 0

        # Null Action
        if action == 0:
            return (p_act, h_act, n_amount, 0, 0, i_amount)

        # Planting action
        elif action == 1:
            if not self.active_crop_flag:
                self.model._send_signal(
                    signal=pcse.signals.crop_start,
                    crop_name=self.crop_name,
                    crop_variety=self.crop_variety,
                    crop_start_type=self.crop_start_type,
                    crop_end_type=self.crop_end_type,
                    day=self.date,
                )
                self.active_crop_flag = True
            p_act = 1
            return (p_act, h_act, n_amount, 0, 0, i_amount)

        # Harvesting Action
        elif action == 2:
            if self.active_crop_flag:
                self.model._send_signal(signal=pcse.signals.crop_harvest, day=self.date, effiency=self.Plant_effec)
            h_act = 1
            return (p_act, h_act, n_amount, 0, 0, i_amount)

        # Irrigation action
        if action >= 1 * self.num_fert + 3:
            i_amount = action - (1 * self.num_fert) - 2
            i_amount = i_amount * self.irrig_amount
            self.model._send_signal(signal=pcse.signals.irrigate, amount=i_amount, efficiency=self.irrig_effec)
            return (p_act, h_act, n_amount, 0, 0, i_amount)

        # Fertilizaiton action, correct for 2 crop specific actions (harvest/plant) and null action
        if action >= 3:
            action -= 3
            if action // self.num_fert == 0:
                n_amount = self.fert_amount * ((action % self.num_fert) + 1)
                self.model._send_signal(signal=pcse.signals.apply_npk, N_amount=n_amount, N_recovery=self.n_recovery)

        return (p_act, h_act, n_amount, 0, 0, i_amount)


class Perennial_Plant_Limited_W_Env(Plant_NPK_Env, LW):
    """Simulates crop growth under Water Limited Production
    with actions for planting and harvesting
    """

    config = utils.make_config(soil=SoilModuleWrapper_LW, crop=Wofost80Perennial, agro=AgroManagerPlantPerennial)

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
    ) -> None:
        """Initialize the :class:`Plant_Limited_W_Env`.

        Args:
            NPK_Args: The environment parameterization
        """
        self.perennial_env = True
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

        self.action_space = gym.spaces.Discrete(2 + self.num_irrig)

    def _take_action(self, action: int) -> tuple[float, float, float, float]:
        """Controls sending fertilization and irrigation signals to the model.
        Includes actions for planting and harvesting.
        Converts the integer action to a signal and amount of NPK/Water to be applied.

        Args:
            action
        """
        p_act = 0
        h_act = 0
        i_amount = 0

        # Null Action
        if action == 0:
            return (p_act, h_act, 0, 0, 0, i_amount)

        # Planting action
        elif action == 1:
            if not self.active_crop_flag:
                self.model._send_signal(
                    signal=pcse.signals.crop_start,
                    crop_name=self.crop_name,
                    crop_variety=self.crop_variety,
                    crop_start_type=self.crop_start_type,
                    crop_end_type=self.crop_end_type,
                    day=self.date,
                )
                self.active_crop_flag = True
            p_act = 1
            return (p_act, h_act, 0, 0, 0, i_amount)

        # Harvesting Action
        elif action == 2:
            if self.active_crop_flag:
                self.model._send_signal(signal=pcse.signals.crop_harvest, day=self.date, effiency=self.Plant_effec)
            h_act = 1
            return (p_act, h_act, 0, 0, 0, i_amount)

        # Irrigation action
        if action >= 0 * self.num_fert + 3:
            i_amount = action - (0 * self.num_fert) - 2
            i_amount = i_amount * self.irrig_amount
            self.model._send_signal(signal=pcse.signals.irrigate, amount=i_amount, efficiency=self.irrig_effec)
            return (p_act, h_act, 0, 0, 0, i_amount)

        return (p_act, h_act, 0, 0, 0, i_amount)


class Perennial_Plant_Limited_Layered_NPKW_Env(Plant_NPK_Env, LNPKW):
    """Simulates crop growth under NPK and Water Limited Production
    with actions for planting and harvesting with layered water balance
    """

    config = utils.make_config(
        soil=LayeredSoilModuleWrapper_LNPKW, crop=Wofost80Perennial, agro=AgroManagerPlantPerennial
    )

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
    ) -> None:
        """Initialize the :class:`Plant_Limited_NPKW_Env`.

        Args:
            NPK_Args: The environment parameterization
        """
        self.perennial_env = True
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

        self.action_space = gym.spaces.Discrete(3 + 3 * args.num_fert + args.num_irrig)

    def _take_action(self, action: int) -> tuple[float, float, float, float]:
        """Controls sending fertilization and irrigation signals to the model.
        Includes actions for planting and harvesting.
        Converts the integer action to a signal and amount of NPK/Water to be applied.

        Args:
            action
        """
        p_act = 0
        h_act = 0
        n_amount = 0
        p_amount = 0
        k_amount = 0
        i_amount = 0

        # Null Action
        if action == 0:
            return (p_act, h_act, n_amount, p_amount, k_amount, i_amount)

        # Planting action
        elif action == 1:
            if not self.active_crop_flag:
                self.model._send_signal(
                    signal=pcse.signals.crop_start,
                    crop_name=self.crop_name,
                    crop_variety=self.crop_variety,
                    crop_start_type=self.crop_start_type,
                    crop_end_type=self.crop_end_type,
                    day=self.date,
                )
                self.active_crop_flag = True
            p_act = 1
            return (p_act, h_act, n_amount, p_amount, k_amount, i_amount)

        # Harvesting Action
        elif action == 2:
            if self.active_crop_flag:
                self.model._send_signal(signal=pcse.signals.crop_harvest, day=self.date, effiency=self.Plant_effec)
            h_act = 1
            return (p_act, h_act, n_amount, p_amount, k_amount, i_amount)

        # Irrigation action
        if action >= 3 * self.num_fert + 3:
            i_amount = action - (3 * self.num_fert) - 2
            i_amount = i_amount * self.irrig_amount
            self.model._send_signal(signal=pcse.signals.irrigate, amount=i_amount, efficiency=self.irrig_effec)
            return (p_act, h_act, n_amount, p_amount, k_amount, i_amount)

        # Fertilizaiton action, correct for 2 crop specific actions (harvest/plant) and null action
        if action >= 3:
            action -= 3

            if action // self.num_fert == 0:
                n_amount = self.fert_amount * ((action % self.num_fert) + 1)
                self.model._send_signal(signal=pcse.signals.apply_npk, N_amount=n_amount, N_recovery=self.n_recovery)
            elif action // self.num_fert == 1:
                p_amount = self.fert_amount * ((action % self.num_fert) + 1)
                self.model._send_signal(signal=pcse.signals.apply_npk, P_amount=p_amount, P_recovery=self.p_recovery)
            elif action // self.num_fert == 2:
                k_amount = self.fert_amount * ((action % self.num_fert) + 1)
                self.model._send_signal(signal=pcse.signals.apply_npk, K_amount=k_amount, K_recovery=self.k_recovery)

        return (p_act, h_act, n_amount, p_amount, k_amount, i_amount)


class Perennial_Plant_Layered_PP_Env(Plant_NPK_Env, PP):
    """Simulates crop growth under abundant NPK and water
    with actions for planting and harvesting with layered water balance
    """

    config = utils.make_config(soil=LayeredSoilModuleWrapper_PP, crop=Wofost80Perennial, agro=AgroManagerPlantPerennial)

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
    ) -> None:
        """Initialize the :class:`Plant_PP_Env`.

        Args:
            NPK_Args: The environment parameterization
        """
        self.perennial_env = True
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

        self.action_space = gym.spaces.Discrete(3)

    def _take_action(self, action: int) -> tuple[float, float, float, float]:
        """Controls sending fertilization and irrigation signals to the model.
        Includes actions for planting and harvesting.
        Converts the integer action to a signal and amount of NPK/Water to be applied.

        Args:
            action
        """
        p_act = 0
        h_act = 0

        # Null Action
        if action == 0:
            return (p_act, h_act, 0, 0, 0, 0)

        # Planting action
        elif action == 1:
            if not self.active_crop_flag:
                self.model._send_signal(
                    signal=pcse.signals.crop_start,
                    crop_name=self.crop_name,
                    crop_variety=self.crop_variety,
                    crop_start_type=self.crop_start_type,
                    crop_end_type=self.crop_end_type,
                    day=self.date,
                )
                self.active_crop_flag = True
            p_act = 1
            return (p_act, h_act, 0, 0, 0, 0)

        # Harvesting Action
        elif action == 2:
            if self.active_crop_flag:
                self.model._send_signal(signal=pcse.signals.crop_harvest, day=self.date, effiency=self.Plant_effec)
            h_act = 1
            return (p_act, h_act, 0, 0, 0, 0)


class Perennial_Plant_Limited_Layered_NPK_Env(Plant_NPK_Env, LNPK):
    """Simulates crop growth under NPK Limited Production
    with actions for planting and harvesting with layered water balance
    """

    config = utils.make_config(
        soil=LayeredSoilModuleWrapper_LNPK, crop=Wofost80Perennial, agro=AgroManagerPlantPerennial
    )

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
    ) -> None:
        """Initialize the :class:`Plant_Limited_NPK_Env`.

        Args:
            NPK_Args: The environment parameterization
        """
        self.perennial_env = True
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

        self.action_space = gym.spaces.Discrete(3 + 3 * self.num_fert)

    def _take_action(self, action: int) -> tuple[float, float, float, float]:
        """Controls sending fertilization and irrigation signals to the model.
        Includes actions for planting and harvesting.
        Converts the integer action to a signal and amount of NPK/Water to be applied.

        Args:
            action
        """
        p_act = 0
        h_act = 0
        n_amount = 0
        p_amount = 0
        k_amount = 0

        # Null Action
        if action == 0:
            return (p_act, h_act, n_amount, p_amount, k_amount, 0)

        # Planting action
        elif action == 1:
            if not self.active_crop_flag:
                self.model._send_signal(
                    signal=pcse.signals.crop_start,
                    crop_name=self.crop_name,
                    crop_variety=self.crop_variety,
                    crop_start_type=self.crop_start_type,
                    crop_end_type=self.crop_end_type,
                    day=self.date,
                )
                self.active_crop_flag = True
            p_act = 1
            return (p_act, h_act, n_amount, p_amount, k_amount, 0)

        # Harvesting Action
        elif action == 2:
            if self.active_crop_flag:
                self.model._send_signal(signal=pcse.signals.crop_harvest, day=self.date, effiency=self.Plant_effec)
            h_act = 1
            return (p_act, h_act, n_amount, p_amount, k_amount, 0)

        # Fertilizaiton action, correct for 2 crop specific actions (harvest/plant) and null action
        if action >= 3:
            action -= 3
            if action // self.num_fert == 0:
                n_amount = self.fert_amount * ((action % self.num_fert) + 1)
                self.model._send_signal(signal=pcse.signals.apply_npk, N_amount=n_amount, N_recovery=self.n_recovery)
            elif action // self.num_fert == 1:
                p_amount = self.fert_amount * ((action % self.num_fert) + 1)
                self.model._send_signal(signal=pcse.signals.apply_npk, P_amount=p_amount, P_recovery=self.p_recovery)
            elif action // self.num_fert == 2:
                k_amount = self.fert_amount * ((action % self.num_fert) + 1)
                self.model._send_signal(signal=pcse.signals.apply_npk, K_amount=k_amount, K_recovery=self.k_recovery)

        return (p_act, h_act, n_amount, p_amount, k_amount, 0)


class Perennial_Plant_Limited_Layered_N_Env(Plant_NPK_Env, LN):
    """Simulates crop growth under Nitrogen Limited Production
    with actions for planting and harvesting with layered water balance
    """

    config = utils.make_config(soil=LayeredSoilModuleWrapper_LN, crop=Wofost80Perennial, agro=AgroManagerPlantPerennial)

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
    ) -> None:
        """Initialize the :class:`Plant_Limited_N_Env`.

        Args:
            NPK_Args: The environment parameterization
        """
        self.perennial_env = True
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
        self.action_space = gym.spaces.Discrete(3 + self.num_fert)

    def _take_action(self, action: int) -> tuple[float, float, float, float]:
        """Controls sending fertilization and irrigation signals to the model.
        Includes actions for planting and harvesting.
        Converts the integer action to a signal and amount of NPK/Water to be applied.

        Args:
            action
        """
        p_act = 0
        h_act = 0
        n_amount = 0

        # Null Action
        if action == 0:
            return (p_act, h_act, n_amount, 0, 0, 0)

        # Planting action
        elif action == 1:
            if not self.active_crop_flag:
                self.model._send_signal(
                    signal=pcse.signals.crop_start,
                    crop_name=self.crop_name,
                    crop_variety=self.crop_variety,
                    crop_start_type=self.crop_start_type,
                    crop_end_type=self.crop_end_type,
                    day=self.date,
                )
                self.active_crop_flag = True
            p_act = 1
            return (p_act, h_act, n_amount, 0, 0, 0)

        # Harvesting Action
        elif action == 2:
            if self.active_crop_flag:
                self.model._send_signal(signal=pcse.signals.crop_harvest, day=self.date, effiency=self.Plant_effec)
            h_act = 1
            return (p_act, h_act, n_amount, 0, 0, 0)

        # Fertilizaiton action, correct for 2 crop specific actions (harvest/plant) and null action
        if action >= 3:
            action -= 3
            if action // self.num_fert == 0:
                n_amount = self.fert_amount * ((action % self.num_fert) + 1)
                self.model._send_signal(signal=pcse.signals.apply_npk, N_amount=n_amount, N_recovery=self.n_recovery)

        return (p_act, h_act, n_amount, 0, 0, 0)


class Perennial_Plant_Limited_Layered_NW_Env(Plant_NPK_Env, LNW):
    """Simulates crop growth under Nitrogen and Water Limited Production
    with actions for planting and harvesting with layered water balance
    """

    config = utils.make_config(
        soil=LayeredSoilModuleWrapper_LNW, crop=Wofost80Perennial, agro=AgroManagerPlantPerennial
    )

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
    ) -> None:
        """Initialize the :class:`Plant_Limited_NW_Env`.

        Args:
            NPK_Args: The environment parameterization
        """
        self.perennial_env = True
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
        self.action_space = gym.spaces.Discrete(3 + self.num_fert + self.num_irrig)

    def _take_action(self, action: int) -> tuple[float, float, float, float]:
        """Controls sending fertilization and irrigation signals to the model.
        Includes actions for planting and harvesting.
        Converts the integer action to a signal and amount of NPK/Water to be applied.

        Args:
            action
        """
        p_act = 0
        h_act = 0
        n_amount = 0
        i_amount = 0

        # Null Action
        if action == 0:
            return (p_act, h_act, n_amount, 0, 0, i_amount)

        # Planting action
        elif action == 1:
            if not self.active_crop_flag:
                self.model._send_signal(
                    signal=pcse.signals.crop_start,
                    crop_name=self.crop_name,
                    crop_variety=self.crop_variety,
                    crop_start_type=self.crop_start_type,
                    crop_end_type=self.crop_end_type,
                    day=self.date,
                )
                self.active_crop_flag = True
            p_act = 1
            return (p_act, h_act, n_amount, 0, 0, i_amount)

        # Harvesting Action
        elif action == 2:
            if self.active_crop_flag:
                self.model._send_signal(signal=pcse.signals.crop_harvest, day=self.date, effiency=self.Plant_effec)
            h_act = 1
            return (p_act, h_act, n_amount, 0, 0, i_amount)

        # Irrigation action
        if action >= 1 * self.num_fert + 3:
            i_amount = action - (1 * self.num_fert) - 2
            i_amount = i_amount * self.irrig_amount
            self.model._send_signal(signal=pcse.signals.irrigate, amount=i_amount, efficiency=self.irrig_effec)
            return (p_act, h_act, n_amount, 0, 0, i_amount)

        # Fertilizaiton action, correct for 2 crop specific actions (harvest/plant) and null action
        if action >= 3:
            action -= 3
            if action // self.num_fert == 0:
                n_amount = self.fert_amount * ((action % self.num_fert) + 1)
                self.model._send_signal(signal=pcse.signals.apply_npk, N_amount=n_amount, N_recovery=self.n_recovery)

        return (p_act, h_act, n_amount, 0, 0, i_amount)


class Perennial_Plant_Limited_Layered_W_Env(Plant_NPK_Env, LW):
    """Simulates crop growth under Water Limited Production
    with actions for planting and harvesting with layered water balance
    """

    config = utils.make_config(soil=LayeredSoilModuleWrapper_LW, crop=Wofost80Perennial, agro=AgroManagerPlantPerennial)

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
    ) -> None:
        """Initialize the :class:`Plant_Limited_W_Env`.

        Args:
            NPK_Args: The environment parameterization
        """
        self.perennial_env = True
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

        self.action_space = gym.spaces.Discrete(2 + self.num_irrig)

    def _take_action(self, action: int) -> tuple[float, float, float, float]:
        """Controls sending fertilization and irrigation signals to the model.
        Includes actions for planting and harvesting.
        Converts the integer action to a signal and amount of NPK/Water to be applied.

        Args:
            action
        """
        p_act = 0
        h_act = 0
        i_amount = 0

        # Null Action
        if action == 0:
            return (p_act, h_act, 0, 0, 0, i_amount)

        # Planting action
        elif action == 1:
            if not self.active_crop_flag:
                self.model._send_signal(
                    signal=pcse.signals.crop_start,
                    crop_name=self.crop_name,
                    crop_variety=self.crop_variety,
                    crop_start_type=self.crop_start_type,
                    crop_end_type=self.crop_end_type,
                    day=self.date,
                )
                self.active_crop_flag = True
            p_act = 1
            return (p_act, h_act, 0, 0, 0, i_amount)

        # Harvesting Action
        elif action == 2:
            if self.active_crop_flag:
                self.model._send_signal(signal=pcse.signals.crop_harvest, day=self.date, effiency=self.Plant_effec)
            h_act = 1
            return (p_act, h_act, 0, 0, 0, i_amount)

        # Irrigation action
        if action >= 0 * self.num_fert + 3:
            i_amount = action - (0 * self.num_fert) - 2
            i_amount = i_amount * self.irrig_amount
            self.model._send_signal(signal=pcse.signals.irrigate, amount=i_amount, efficiency=self.irrig_effec)
            return (p_act, h_act, 0, 0, 0, i_amount)

        return (p_act, h_act, 0, 0, 0, i_amount)

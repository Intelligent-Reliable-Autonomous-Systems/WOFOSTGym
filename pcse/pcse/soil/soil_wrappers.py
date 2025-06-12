"""This module wraps the soil components for water and nutrients so that they
run jointly within the same model.
Allard de Wit (allard.dewit@wur.nl), September 2020
Modified by Will Solow, 2024
"""

from datetime import date

from pcse.utils.traitlets import Instance
from pcse.nasapower import WeatherDataContainer
from pcse.base import SimulationObject, VariableKiosk

from pcse.soil.classic_waterbalance import WaterbalanceFD
from pcse.soil.classic_waterbalance import WaterbalancePP

from pcse.soil.multilayer_waterbalance import WaterBalanceLayered
from pcse.soil.multilayer_waterbalance import WaterBalanceLayered_PP

from pcse.soil.npk_soil_dynamics import NPK_Soil_Dynamics
from pcse.soil.npk_soil_dynamics import NPK_Soil_Dynamics_PP
from pcse.soil.npk_soil_dynamics import NPK_Soil_Dynamics_LN


class BaseSoilModuleWrapper(SimulationObject):
    """Base Soil Module Wrapper"""

    WaterbalanceFD = Instance(SimulationObject)
    NPK_Soil_Dynamics = Instance(SimulationObject)

    def initialize(self, day: date, kiosk: VariableKiosk, parvalues: dict) -> None:
        msg = "`initialize` method not yet implemented on %s" % self.__class__.__name__
        raise NotImplementedError(msg)

    def calc_rates(self, day: date, drv: WeatherDataContainer) -> None:
        """Calculate state rates"""
        self.WaterbalanceFD.calc_rates(day, drv)
        self.NPK_Soil_Dynamics.calc_rates(day, drv)

    def integrate(self, day: date, delt: float = 1.0) -> None:
        """Integrate state rates"""
        self.WaterbalanceFD.integrate(day, delt)
        self.NPK_Soil_Dynamics.integrate(day, delt)


class SoilModuleWrapper_LNPKW(BaseSoilModuleWrapper):
    """This wraps the soil water balance for free drainage conditions and NPK balance
    for production conditions limited by both soil water and NPK.
    """

    def initialize(self, day: date, kiosk: VariableKiosk, parvalues: dict) -> None:
        """
        :param day: start date of the simulation
        :param kiosk: variable kiosk of this PCSE instance
        :param parvalues: dictionary with parameter key/value pairs
        """
        self.WaterbalanceFD = WaterbalanceFD(day, kiosk, parvalues)
        self.NPK_Soil_Dynamics = NPK_Soil_Dynamics(day, kiosk, parvalues)


class SoilModuleWrapper_PP(BaseSoilModuleWrapper):
    """This wraps the soil water balance for free drainage conditions and NPK balance
    for potential production with unlimited water and NPK.
    """

    WaterbalanceFD = Instance(SimulationObject)
    NPK_Soil_Dynamics = Instance(SimulationObject)

    def initialize(self, day: date, kiosk: VariableKiosk, parvalues: dict) -> None:
        """
        :param day: start date of the simulation
        :param kiosk: variable kiosk of this PCSE instance
        :param parvalues: dictionary with parameter key/value pairs
        """
        self.WaterbalanceFD = WaterbalancePP(day, kiosk, parvalues)
        self.NPK_Soil_Dynamics = NPK_Soil_Dynamics_PP(day, kiosk, parvalues)


class SoilModuleWrapper_LW(BaseSoilModuleWrapper):
    """This wraps the soil water balance for free drainage conditions and NPK balance
    for production conditions limited by soil water.
    """

    WaterbalanceFD = Instance(SimulationObject)
    NPK_Soil_Dynamics = Instance(SimulationObject)

    def initialize(self, day: date, kiosk: VariableKiosk, parvalues: dict) -> None:
        """
        :param day: start date of the simulation
        :param kiosk: variable kiosk of this PCSE instance
        :param parvalues: dictionary with parameter key/value pairs
        """
        self.WaterbalanceFD = WaterbalanceFD(day, kiosk, parvalues)
        self.NPK_Soil_Dynamics = NPK_Soil_Dynamics_PP(day, kiosk, parvalues)


class SoilModuleWrapper_LNW(BaseSoilModuleWrapper):
    """This wraps the soil water balance for free drainage conditions and NPK balance
    for production conditions limited by both soil water and N, but assumes abundance
    of P/K.
    """

    WaterbalanceFD = Instance(SimulationObject)
    NPK_Soil_Dynamics = Instance(SimulationObject)

    def initialize(self, day: date, kiosk: VariableKiosk, parvalues: dict) -> None:
        """
        :param day: start date of the simulation
        :param kiosk: variable kiosk of this PCSE instance
        :param parvalues: dictionary with parameter key/value pairs
        """
        self.WaterbalanceFD = WaterbalanceFD(day, kiosk, parvalues)
        self.NPK_Soil_Dynamics = NPK_Soil_Dynamics_LN(day, kiosk, parvalues)


class SoilModuleWrapper_LNPK(BaseSoilModuleWrapper):
    """This wraps the soil water balance for free drainage conditions and NPK balance
    for production conditions limited by NPK but assumes abundant water.
    """

    WaterbalanceFD = Instance(SimulationObject)
    NPK_Soil_Dynamics = Instance(SimulationObject)

    def initialize(self, day: date, kiosk: VariableKiosk, parvalues: dict) -> None:
        """
        :param day: start date of the simulation
        :param kiosk: variable kiosk of this PCSE instance
        :param parvalues: dictionary with parameter key/value pairs
        """
        self.WaterbalanceFD = WaterbalancePP(day, kiosk, parvalues)
        self.NPK_Soil_Dynamics = NPK_Soil_Dynamics(day, kiosk, parvalues)


class SoilModuleWrapper_LN(BaseSoilModuleWrapper):
    """This wraps the soil water balance for free drainage conditions and NPK balance
    for production conditions limited by Nitrogen, but assumes abundance of P/K
    and water.
    """

    WaterbalanceFD = Instance(SimulationObject)
    NPK_Soil_Dynamics = Instance(SimulationObject)

    def initialize(self, day: date, kiosk: VariableKiosk, parvalues: dict) -> None:
        """
        :param day: start date of the simulation
        :param kiosk: variable kiosk of this PCSE instance
        :param parvalues: dictionary with parameter key/value pairs
        """
        self.WaterbalanceFD = WaterbalancePP(day, kiosk, parvalues)
        self.NPK_Soil_Dynamics = NPK_Soil_Dynamics_LN(day, kiosk, parvalues)


class LayeredSoilModuleWrapper_LNPKW(BaseSoilModuleWrapper):
    """This wraps the layered soil water balance for free drainage conditions and NPK balance
    for production conditions limited by both soil water and NPK.
    """

    def initialize(self, day: date, kiosk: VariableKiosk, parvalues: dict) -> None:
        """
        :param day: start date of the simulation
        :param kiosk: variable kiosk of this PCSE instance
        :param parvalues: dictionary with parameter key/value pairs
        """
        self.WaterbalanceFD = WaterBalanceLayered(day, kiosk, parvalues)
        self.NPK_Soil_Dynamics = NPK_Soil_Dynamics(day, kiosk, parvalues)


class LayeredSoilModuleWrapper_PP(BaseSoilModuleWrapper):
    """This wraps the layered soil water balance for free drainage conditions and NPK balance
    for potential production with unlimited water and NPK.
    """

    WaterbalanceFD = Instance(SimulationObject)
    NPK_Soil_Dynamics = Instance(SimulationObject)

    def initialize(self, day: date, kiosk: VariableKiosk, parvalues: dict) -> None:
        """
        :param day: start date of the simulation
        :param kiosk: variable kiosk of this PCSE instance
        :param parvalues: dictionary with parameter key/value pairs
        """
        self.WaterbalanceFD = WaterBalanceLayered_PP(day, kiosk, parvalues)
        self.NPK_Soil_Dynamics = NPK_Soil_Dynamics_PP(day, kiosk, parvalues)


class LayeredSoilModuleWrapper_LW(BaseSoilModuleWrapper):
    """This wraps the layered soil water balance for free drainage conditions and NPK balance
    for production conditions limited by soil water.
    """

    WaterbalanceFD = Instance(SimulationObject)
    NPK_Soil_Dynamics = Instance(SimulationObject)

    def initialize(self, day: date, kiosk: VariableKiosk, parvalues: dict) -> None:
        """
        :param day: start date of the simulation
        :param kiosk: variable kiosk of this PCSE instance
        :param parvalues: dictionary with parameter key/value pairs
        """
        self.WaterbalanceFD = WaterBalanceLayered(day, kiosk, parvalues)
        self.NPK_Soil_Dynamics = NPK_Soil_Dynamics_PP(day, kiosk, parvalues)


class LayeredSoilModuleWrapper_LNW(BaseSoilModuleWrapper):
    """This wraps the layered soil water balance for free drainage conditions and NPK balance
    for production conditions limited by both soil water and N, but assumes abundance
    of P/K.
    """

    WaterbalanceFD = Instance(SimulationObject)
    NPK_Soil_Dynamics = Instance(SimulationObject)

    def initialize(self, day: date, kiosk: VariableKiosk, parvalues: dict) -> None:
        """
        :param day: start date of the simulation
        :param kiosk: variable kiosk of this PCSE instance
        :param parvalues: dictionary with parameter key/value pairs
        """
        self.WaterbalanceFD = WaterBalanceLayered(day, kiosk, parvalues)
        self.NPK_Soil_Dynamics = NPK_Soil_Dynamics_LN(day, kiosk, parvalues)


class LayeredSoilModuleWrapper_LNPK(BaseSoilModuleWrapper):
    """This wraps the layered soil water balance for free drainage conditions and NPK balance
    for production conditions limited by NPK but assumes abundant water.
    """

    WaterbalanceFD = Instance(SimulationObject)
    NPK_Soil_Dynamics = Instance(SimulationObject)

    def initialize(self, day: date, kiosk: VariableKiosk, parvalues: dict) -> None:
        """
        :param day: start date of the simulation
        :param kiosk: variable kiosk of this PCSE instance
        :param parvalues: dictionary with parameter key/value pairs
        """
        self.WaterbalanceFD = WaterBalanceLayered(day, kiosk, parvalues)
        self.NPK_Soil_Dynamics = NPK_Soil_Dynamics(day, kiosk, parvalues)


class LayeredSoilModuleWrapper_LN(BaseSoilModuleWrapper):
    """This wraps the layered soil water balance for free drainage conditions and NPK balance
    for production conditions limited by Nitrogen, but assumes abundance of P/K
    and water.
    """

    WaterbalanceFD = Instance(SimulationObject)
    NPK_Soil_Dynamics = Instance(SimulationObject)

    def initialize(self, day: date, kiosk: VariableKiosk, parvalues: dict) -> None:
        """
        :param day: start date of the simulation
        :param kiosk: variable kiosk of this PCSE instance
        :param parvalues: dictionary with parameter key/value pairs
        """
        self.WaterbalanceFD = WaterBalanceLayered_PP(day, kiosk, parvalues)
        self.NPK_Soil_Dynamics = NPK_Soil_Dynamics_LN(day, kiosk, parvalues)

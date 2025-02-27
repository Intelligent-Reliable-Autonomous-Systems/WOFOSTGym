"""This module wraps the soil components for water and nutrients so that they 
run jointly within the same model.
Allard de Wit (allard.dewit@wur.nl), September 2020
Modified by Will Solow, 2024
"""
from datetime import date 

from ..utils.traitlets import Instance
from ..nasapower import WeatherDataProvider
from ..base import SimulationObject, VariableKiosk
from .classic_waterbalance import WaterbalanceFD
from .classic_waterbalance import WaterbalancePP
from .npk_soil_dynamics import NPK_Soil_Dynamics
from .npk_soil_dynamics import NPK_Soil_Dynamics_PP
from .npk_soil_dynamics import NPK_Soil_Dynamics_LN


class BaseSoilModuleWrapper(SimulationObject):
    """Base Soil Module Wrapper
    """
    WaterbalanceFD = Instance(SimulationObject)
    NPK_Soil_Dynamics = Instance(SimulationObject)

    def initialize(self, day:date , kiosk:VariableKiosk, parvalues:dict):
        msg = "`initialize` method not yet implemented on %s" % self.__class__.__name__
        raise NotImplementedError(msg)
    
    def calc_rates(self, day:date, drv:WeatherDataProvider):
        """Calculate state rates
        """
        self.WaterbalanceFD.calc_rates(day, drv)
        self.NPK_Soil_Dynamics.calc_rates(day, drv)

    def integrate(self, day:date, delt:float=1.0):
        """Integrate state rates
        """
        self.WaterbalanceFD.integrate(day, delt)
        self.NPK_Soil_Dynamics.integrate(day, delt)

class SoilModuleWrapper_LNPKW(BaseSoilModuleWrapper):
    """This wraps the soil water balance for free drainage conditions and NPK balance
    for production conditions limited by both soil water and NPK.
    """

    def initialize(self, day:date, kiosk:VariableKiosk, parvalues:dict):
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

    def initialize(self, day:date, kiosk:VariableKiosk, parvalues:dict):
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

    def initialize(self, day:date, kiosk:VariableKiosk, parvalues:dict):
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

    def initialize(self, day:date, kiosk:VariableKiosk, parvalues:dict):
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

    def initialize(self, day:date, kiosk:VariableKiosk, parvalues:dict):
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

    def initialize(self, day:date, kiosk:VariableKiosk, parvalues:dict):
        """
        :param day: start date of the simulation
        :param kiosk: variable kiosk of this PCSE instance
        :param parvalues: dictionary with parameter key/value pairs
        """
        self.WaterbalanceFD = WaterbalancePP(day, kiosk, parvalues)
        self.NPK_Soil_Dynamics = NPK_Soil_Dynamics_LN(day, kiosk, parvalues)








        
"""Simulation object for computing evaporation and transpiration based on CO2 effects

Written by: Allard de Wit (allard.dewit@wur.nl), April 2014
Modified by Will Solow, 2024
"""
from math import exp
from datetime import date

from ..utils.traitlets import Float, Int, Bool
from ..utils.decorators import prepare_rates, prepare_states
from ..base import ParamTemplate, StatesTemplate, RatesTemplate, \
                         SimulationObject, VariableKiosk
from ..util import limit, AfgenTrait
from ..nasapower import WeatherDataProvider


def SWEAF(ET0, DEPNR):
    """Calculates the Soil Water Easily Available Fraction (SWEAF).

    :param ET0: The evapotranpiration from a reference crop.
    :param DEPNR: The crop dependency number.
    
    The fraction of easily available soil water between field capacity and
    wilting point is a function of the potential evapotranspiration rate
    (for a closed canopy) in cm/day, ET0, and the crop group number, DEPNR
    (from 1 (=drought-sensitive) to 5 (=drought-resistent)). The function
    SWEAF describes this relationship given in tabular form by Doorenbos &
    Kassam (1979) and by Van Keulen & Wolf (1986; p.108, table 20)
    http://edepot.wur.nl/168025.
    """
    A = 0.76
    B = 1.5
    # curve for CGNR 5, and other curves at fixed distance below it
    sweaf = 1./(A+B*ET0) - (5.-DEPNR)*0.10

    # Correction for lower curves (CGNR less than 3)
    if (DEPNR < 3.):
        sweaf += (ET0-0.6)/(DEPNR*(DEPNR+3.))

    return limit(0.10, 0.95, sweaf)

class EvapotranspirationCO2(SimulationObject):
    """Calculation of evaporation (water and soil) and transpiration rates
    taking into account the CO2 effect on crop transpiration.

    *Simulation parameters* (To be provided in cropdata dictionary):

    ======== ============================================= =======  ============
     Name     Description                                   Type     Unit
    ======== ============================================= =======  ============
    CFET     Correction factor for potential transpiration   S       -
             rate.
    DEPNR    Dependency number for crop sensitivity to       S       -
             soil moisture stress.
    KDIFTB   Extinction coefficient for diffuse visible      T       -
             as function of DVS.
    IOX      Switch oxygen stress on (1) or off (0)          S       -
    IAIRDU   Switch airducts on (1) or off (0)               S       -
    CRAIRC   Critical air content for root aeration          S       -
    SM0      Soil porosity                                   S       -
    SMW      Volumetric soil moisture content at wilting     S       -
             point
    SMFCF    Volumetric soil moisture content at field       S       -
             capacity
    SM0      Soil porosity                                   S       -
    CO2      Atmospheric CO2 concentration                   S       ppm
    CO2TRATB Reduction factor for TRAMX as function of
             atmospheric CO2 concentration                   T       -
    ======== ============================================= =======  ============


    *State variables*

    Note that these state variables are only assigned after finalize() has been
    run.

    =======  ================================================= ==== ============
     Name     Description                                      Pbl      Unit
    =======  ================================================= ==== ============
    IDWST     Nr of days with water stress.                      N    -
    IDOST     Nr of days with oxygen stress.                     N    -
    =======  ================================================= ==== ============


    *Rate variables*

    =======  ================================================= ==== ============
     Name     Description                                      Pbl      Unit
    =======  ================================================= ==== ============
    EVWMX    Maximum evaporation rate from an open water        Y    |cm day-1|
             surface.
    EVSMX    Maximum evaporation rate from a wet soil surface.  Y    |cm day-1|
    TRAMX    Maximum transpiration rate from the plant canopy   Y    |cm day-1|
    TRA      Actual transpiration rate from the plant canopy    Y    |cm day-1|
    IDOS     Indicates water stress on this day (True|False)    N    -
    IDWS     Indicates oxygen stress on this day (True|False)   N    -
    RFWS     Reducation factor for water stress                 Y     -
    RFOS     Reducation factor for oxygen stress                Y     -
    RFTRA    Reduction factor for transpiration (wat & ox)      Y     -
    =======  ================================================= ==== ============

    *Signals send or handled*

    None

    *External dependencies:*

    =======  =================================== =================  ============
     Name     Description                         Provided by         Unit
    =======  =================================== =================  ============
    DVS      Crop development stage              DVS_Phenology       -
    LAI      Leaf area index                     Leaf_dynamics       -
    SM       Volumetric soil moisture content    Waterbalance        -
    =======  =================================== =================  ============
    """

    # helper variable for counting total days with water and oxygen
    # stress (IDWST, IDOST)
    _IDWST = Int(0)
    _IDOST = Int(0)

    class Parameters(ParamTemplate):
        CFET    = Float(-99.)
        DEPNR   = Float(-99.)
        KDIFTB  = AfgenTrait()
        IAIRDU  = Float(-99.)
        IOX     = Float(-99.)
        CRAIRC  = Float(-99.)
        SM0     = Float(-99.)
        SMW     = Float(-99.)
        SMFCF   = Float(-99.)
        CO2     = Float(-99.)
        CO2TRATB = AfgenTrait()

    class RateVariables(RatesTemplate):
        EVWMX = Float(-99.)
        EVSMX = Float(-99.)
        TRAMX = Float(-99.)
        TRA   = Float(-99.)
        IDOS  = Bool(False)
        IDWS  = Bool(False)
        RFWS = Float(-99.)
        RFOS = Float(-99.)
        RFTRA = Float(-99.)

    class StateVariables(StatesTemplate):
        IDOST  = Int(-99)
        IDWST  = Int(-99)

    def initialize(self, day:date, kiosk:VariableKiosk, parvalues:dict):
        """
        :param day: start date of the simulation
        :param kiosk: variable kiosk of this PCSE instance
        """

        self.kiosk = kiosk
        self.params = self.Parameters(parvalues)
    
        self.states = self.StateVariables(kiosk,
                    publish=["IDOST", "IDWST"], IDOST=-999, IDWST=-999)

        self.rates = self.RateVariables(kiosk, 
                    publish=["EVWMX", "EVSMX", "TRAMX", "TRA", "IDOS", 
                             "IDWS", "RFWS", "RFOS", "RFTRA"])

    @prepare_rates
    def __call__(self, day:date, drv:WeatherDataProvider):
        """Calls the Evapotranspiration object to compute value to be returned to 
        model
        """
        p = self.params
        r = self.rates
        k = self.kiosk

        # reduction factor for CO2 on TRAMX
        RF_TRAMX_CO2 = p.CO2TRATB(p.CO2)

        # crop specific correction on potential transpiration rate
        ET0_CROP = max(0., p.CFET * drv.ET0)

        # maximum evaporation and transpiration rates
        KGLOB = 0.75*p.KDIFTB(k.DVS)
        EKL = exp(-KGLOB * k.LAI)
        r.EVWMX = drv.E0 * EKL
        r.EVSMX = max(0., drv.ES0 * EKL)
        r.TRAMX = ET0_CROP * (1.-EKL) * RF_TRAMX_CO2

        # Critical soil moisture
        SWDEP = SWEAF(ET0_CROP, p.DEPNR)

        SMCR = (1.-SWDEP)*(p.SMFCF-p.SMW) + p.SMW

        # Reduction factor for transpiration in case of water shortage (RFWS)
        r.RFWS = limit(0., 1., (k.SM-p.SMW)/(SMCR-p.SMW))

        # reduction in transpiration in case of oxygen shortage (RFOS)
        # for non-rice crops, and possibly deficient land drainage
        r.RFOS = 1.
        if p.IAIRDU == 0 and p.IOX == 1:
            RFOSMX = limit(0., 1., (p.SM0 - k.SM)/p.CRAIRC)
            # maximum reduction reached after 4 days
            r.RFOS = RFOSMX + (1. - min(k.DSOS, 4)/4.)*(1.-RFOSMX)

        # Transpiration rate multiplied with reduction factors for oxygen and water
        r.RFTRA = r.RFOS * r.RFWS
        r.TRA = r.TRAMX * r.RFTRA

        # Counting stress days
        if r.RFWS < 1.:
            r.IDWS = True
            self._IDWST += 1
        if r.RFOS < 1.:
            r.IDOS = True
            self._IDOST += 1

        return r.TRA, r.TRAMX

    @prepare_states
    def finalize(self, day:date):
        """Finalize states at end of simulation
        """

        self.states.IDWST = self._IDWST
        self.states.IDOST = self._IDOST

        SimulationObject.finalize(self, day)

    def reset(self):
        """Reset states and rates
        """
        s = self.states
        r = self.rates
        s.IDOST=-999
        s.IDWST=-999

        r.EVWMX = r.EVSMX = r.TRAMX = r.TRA = r.RFWS = r.RFOS = r.RFTRA = 0
        r.IDOS = r.IDWS = False

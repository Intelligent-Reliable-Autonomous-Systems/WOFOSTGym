"""Handles stem biomass dynamics for crop model

Written by: Allard de Wit (allard.dewit@wur.nl), April 2014
Modified by Will Solow, 2024
"""

from datetime import date 

from ..nasapower import WeatherDataProvider
from ..utils.traitlets import Float
from ..utils.decorators import prepare_rates, prepare_states
from ..util import AfgenTrait
from ..base import ParamTemplate, StatesTemplate, RatesTemplate, \
    SimulationObject, VariableKiosk

class Base_WOFOST_Stem_Dynamics(SimulationObject):
    """Implementation of stem biomass dynamics.
    
    Stem biomass increase results from the assimilates partitioned to
    the stem system. Stem death is defined as the current stem biomass
    multiplied by a relative death rate (`RDRSTB`). The latter as a function
    of the development stage (`DVS`).
    
    Stems are green elements of the plant canopy and can as such contribute
    to the total photosynthetic active area. This is expressed as the Stem
    Area Index which is obtained by multiplying stem biomass with the
    Specific Stem Area (SSATB), which is a function of DVS.

    **Simulation parameters**:
    
    =======  ============================================= =======  ============
     Name     Description                                   Type     Unit
    =======  ============================================= =======  ============
    TDWI     Initial total crop dry weight                  SCr       |kg ha-1|
    RDRSTB   Relative death rate of stems as a function     TCr       -
             of development stage
    SSATB    Specific Stem Area as a function of            TCr       |ha kg-1|
             development stage
    =======  ============================================= =======  ============
    

    **State variables**

    =======  ================================================= ==== ============
     Name     Description                                      Pbl      Unit
    =======  ================================================= ==== ============
    SAI      Stem Area Index                                    Y     -
    WST      Weight of living stems                             Y     |kg ha-1|
    DWST     Weight of dead stems                               N     |kg ha-1|
    TWST     Total weight of stems                              Y     |kg ha-1|
    =======  ================================================= ==== ============

    **Rate variables**

    =======  ================================================= ==== ============
     Name     Description                                      Pbl      Unit
    =======  ================================================= ==== ============
    GRST     Growth rate stem biomass                           N   |kg ha-1 d-1|
    DRST     Death rate stem biomass                            N   |kg ha-1 d-1|
    GWST     Net change in stem biomass                         N   |kg ha-1 d-1|
    =======  ================================================= ==== ============
    
    **Signals send or handled**
    
    None
    
    **External dependencies:**
    
    =======  =================================== =================  ============
     Name     Description                         Provided by         Unit
    =======  =================================== =================  ============
    DVS      Crop development stage              DVS_Phenology       -
    ADMI     Above-ground dry matter             CropSimulation     |kg ha-1 d-1|
             increase
    FR       Fraction biomass to roots           DVS_Partitioning    - 
    FS       Fraction biomass to stems           DVS_Partitioning    - 
    =======  =================================== =================  ============
    """

    class Parameters(ParamTemplate):      
        RDRSTB = AfgenTrait()
        SSATB  = AfgenTrait()
        TDWI   = Float(-99.)

    class StateVariables(StatesTemplate):
        WST  = Float(-99.)
        DWST = Float(-99.)
        TWST = Float(-99.)
        SAI  = Float(-99.) # Stem Area Index

    class RateVariables(RatesTemplate):
        GRST = Float(-99.)
        DRST = Float(-99.)
        GWST = Float(-99.)
        
    def initialize(self, day:date, kiosk:VariableKiosk, parvalues:dict):
        """
        :param day: start date of the simulation
        :param kiosk: variable kiosk of this PCSE  instance
        :param parvalues: `ParameterProvider` object providing parameters as
                key/value pairs
        """
        
        msg = "Initialize() should be implemented by subclass"
        raise NotImplementedError(msg)

    @prepare_rates
    def calc_rates(self, day:date, drv:WeatherDataProvider):
        """Compute state rates before integration
        """
        rates  = self.rates
        states = self.states
        params = self.params
        
        DVS = self.kiosk["DVS"]
        FS = self.kiosk["FS"]
        ADMI = self.kiosk["ADMI"]

        # Growth/death rate stems
        rates.GRST = ADMI * FS
        rates.DRST = params.RDRSTB(DVS) * states.WST
        rates.GWST = rates.GRST - rates.DRST

    @prepare_states
    def integrate(self, day:date, delt:float=1.0):
        """Integrate state rates
        """
        params = self.params
        rates = self.rates
        states = self.states

        # Stem biomass (living, dead, total)
        states.WST += rates.GWST
        states.DWST += rates.DRST
        states.TWST = states.WST + states.DWST

        # Calculate Stem Area Index (SAI)
        DVS = self.kiosk["DVS"]
        states.SAI = states.WST * params.SSATB(DVS)

    def publish_states(self):
        params = self.params
        rates = self.rates
        states = self.states

        # Stem biomass (living, dead, total)
        states.WST += rates.GWST
        states.DWST += rates.DRST
        states.TWST = states.WST + states.DWST

        # Calculate Stem Area Index (SAI)
        DVS = self.kiosk["DVS"]
        states.SAI = states.WST * params.SSATB(DVS)

    def reset(self):
        """Reset states and rates
        """
        # INITIAL STATES
        params = self.params
        s = self.states
        r = self.rates
        # Set initial stem biomass
        FS = self.kiosk["FS"]
        FR = self.kiosk["FR"]
        WST  = (params.TDWI * (1-FR)) * FS
        DWST = 0.
        TWST = WST + DWST
        # Initial Stem Area Index
        DVS = self.kiosk["DVS"]
        SAI = WST * params.SSATB(DVS)

        s.WST=WST
        s.DWST=DWST
        s.TWST=TWST
        s.SAI=SAI

        r.GRST = r.DRST = r.GWST = 0


class Annual_WOFOST_Stem_Dynamics(Base_WOFOST_Stem_Dynamics):
    """Class for Stem Dynamics of annual crops
    """

    def initialize(self, day:date, kiosk:VariableKiosk, parvalues:dict):
        """
        :param day: start date of the simulation
        :param kiosk: variable kiosk of this PCSE  instance
        :param parvalues: `ParameterProvider` object providing parameters as
                key/value pairs
        """
        
        self.params = self.Parameters(parvalues)
        self.kiosk  = kiosk

        # INITIAL STATES
        params = self.params
        # Set initial stem biomass
        FS = self.kiosk["FS"]
        FR = self.kiosk["FR"]
        WST  = (params.TDWI * (1-FR)) * FS
        DWST = 0.
        TWST = WST + DWST
        # Initial Stem Area Index
        DVS = self.kiosk["DVS"]
        SAI = WST * params.SSATB(DVS)

        self.states = self.StateVariables(kiosk, publish=["WST", "DWST", "TWST", "SAI"],
                                          WST=WST, DWST=DWST, TWST=TWST, SAI=SAI)
        self.rates  = self.RateVariables(kiosk, publish=["GRST", "DRST", "GWST"])

class Perennial_WOFOST_Stem_Dynamics(Base_WOFOST_Stem_Dynamics):
    """Class for Stem Dynamics of annual crops
    """

    class Parameters(ParamTemplate):      
        RDRSTB = AfgenTrait()
        SSATB  = AfgenTrait()
        TDWI   = AfgenTrait()
    
    def initialize(self, day:date, kiosk:VariableKiosk, parvalues:dict):
        """
        :param day: start date of the simulation
        :param kiosk: variable kiosk of this PCSE  instance
        :param parvalues: `ParameterProvider` object providing parameters as
                key/value pairs
        """
        
        self.params = self.Parameters(parvalues)
        self.kiosk  = kiosk

        # INITIAL STATES
        params = self.params
        # Set initial stem biomass
        FS = self.kiosk["FS"]
        FR = self.kiosk["FR"]
        AGE = self.kiosk["AGE"]

        WST  = (params.TDWI(AGE) * (1-FR)) * FS
        DWST = 0.
        TWST = WST + DWST
        # Initial Stem Area Index
        DVS = self.kiosk["DVS"]
        SAI = WST * params.SSATB(DVS)

        self.states = self.StateVariables(kiosk, publish=["WST", "DWST", "TWST", "SAI"],
                                          WST=WST, DWST=DWST, TWST=TWST, SAI=SAI)
        self.rates  = self.RateVariables(kiosk, publish=["GRST", "DRST", "GWST"])

    def reset(self):
        """Reset states and rates
        """
        # INITIAL STATES
        params = self.params
        s = self.states
        r = self.rates
        # Set initial stem biomass
        FS = self.kiosk["FS"]
        FR = self.kiosk["FR"]
        WST  = (params.TDWI(self.kiosk["AGE"]) * (1-FR)) * FS
        DWST = 0.
        TWST = WST + DWST
        # Initial Stem Area Index
        DVS = self.kiosk["DVS"]
        SAI = WST * params.SSATB(DVS)

        s.WST=WST
        s.DWST=DWST
        s.TWST=TWST
        s.SAI=SAI

        r.GRST = r.DRST = r.GWST = 0
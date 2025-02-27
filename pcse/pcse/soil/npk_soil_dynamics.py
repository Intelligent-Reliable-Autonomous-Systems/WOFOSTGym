"""Implementations of the WOFOST waterbalance modules for simulation
of potential production (`NPK_Soil_Dynamics_PP`) and NPK-limited production
(`NPK_Soil_Dynamics`) and N-limited production (`NPK_Soil_Dynamics_N`)

Written by: Allard de Wit (allard.dewit@wur.nl), April 2014
Modified by Will Solow, 2024
"""
from datetime import date

from ..util import AfgenTrait
from ..utils.traitlets import Float
from ..utils.decorators import prepare_rates, prepare_states
from ..base import ParamTemplate, StatesTemplate, RatesTemplate, \
    SimulationObject
from ..utils import signals
from ..base import VariableKiosk
from ..nasapower import WeatherDataProvider

class NPK_Soil_Dynamics(SimulationObject):
    """A simple module for soil N/P/K dynamics.

    This modules represents the soil as a bucket for available N/P/K consisting
    of two components: 1) a native soil supply which consists of an initial
    amount of N/P/K which will become available with a fixed fraction every day
    and 2) an external supply which is computed as an amount of N/P/K supplied
    and multiplied by a recovery fraction in order to have an effective amount of
    N/P/K that is available for crop growth.

    This module does not simulate any soil physiological processes and is only
    a book-keeping approach for N/P/K availability. On the other hand, it
    requires no detailed soil parameters. Only an initial soil amount, the
    fertilizer inputs, a recovery fraction and a background supply.

    **Simulation parameters**

    ============  ============================================= =======  ==============
     Name          Description                                   Type     Unit
    ============  ============================================= =======  ==============
    NSOILBASE     Base soil supply of N available through        SSi      |kg ha-1|
                  mineralisation
    NSOILBASE_FR  Fraction of base soil N that comes available   SSi        -
                  every day
    PSOILBASE     Base soil supply of N available through        SSi      |kg ha-1|
                  mineralisation
    PSOILBASE_FR  Fraction of base soil N that comes available             -
                  every day
    KSOILBASE     Base soil supply of N available through        SSi      |kg ha-1|
                  mineralisation
    KSOILBASE_FR  Fraction of base soil N that comes available   SSi        -
                  every day
    NAVAILI       Initial N available in the N pool              SSi      |kg ha-1|
    PAVAILI       Initial P available in the P pool              SSi      |kg ha-1|
    KAVAILI       Initial K available in the K pool              SSi      |kg ha-1|
    NMAX          Maximum N available in the N pool              SSi      |kg ha-1|
    PMAX          Maximum P available in the N pool              SSi      |kg ha-1|
    KMAX          Maximum K available in the N pool              SSi      |kg ha-1|
    BG_N_SUPPLY   Background supply of N through atmospheric     SSi      |kg ha-1 d-1|
                  deposition.
    BG_P_SUPPLY   Background supply of P through atmospheric     SSi      |kg ha-1 d-1|
                  deposition.
    BG_K_SUPPLY   Background supply of K through atmospheric     SSi      |kg ha-1 d-1|
                  deposition.
    RNSOILMAX     Maximum rate of surface N to subsoil           SSi      |kg ha-1 d-1|
    RPSOILMAX     Maximum rate of surface P to subsoil           SSi      |kg ha-1 d-1|
    RKSOILMAX     Maximum rate of surface K to subsoil           SSi      |kg ha-1 d-1|

    RNABSORPTION  Relative rate of N absorption from surface     SSi      |kg ha-1 d-1|
                  to subsoil
    RPABSORPTION  Relative rate of P absorption from surface     SSi      |kg ha-1 d-1|
                  to subsoil
    RKABSORPTION  Relative rate of K absorption from surface     SSi      |kg ha-1 d-1|
                  to subsoil
    RNPKRUNOFF    Relative rate of NPK runoff as a function of   SSi      -
                  surface water runoff
    ============  ============================================= =======  ==============


    **State variables**

    =======  ================================================= ==== ============
     Name     Description                                      Pbl      Unit
    =======  ================================================= ==== ============
     NSOIL    total mineral soil N available at start of         N    [kg ha-1]
              growth period
     PSOIL    total mineral soil P available at start of         N    [kg ha-1]
              growth period
     KSOIL    total mineral soil K available at start of         N    [kg ha-1]
              growth period
     NAVAIL   Total mineral N from soil and fertiliser           Y    |kg ha-1|
     PAVAIL   Total mineral N from soil and fertiliser           Y    |kg ha-1|
     KAVAIL   Total mineral N from soil and fertiliser           Y    |kg ha-1|

     TOTN     Total mineral N applied by fertilization           Y    |kg ha-1|
     TOTP     Total mineral P applied by fertilization           Y    |kg ha-1|
     TOTK     Total mineral K applied by fertilization           Y    |kg ha-1|

     SURFACE_N    Mineral N on surface layer                     Y    |kg ha-1|
     SURFACE_P    Mineral P on surface layer                     Y    |kg ha-1|
     SURFACE_K    Mineral K on surface layer                     Y    |kg ha-1|

     TOTN_RUNOFF  Total surface N runoff                         Y    |kg ha-1|
     TOTP_RUNOFF  Total surface N runoff                         Y    |kg ha-1|
     TOTK_RUNOFF  Total surface N runoff                         Y    |kg ha-1|
    =======  ================================================= ==== ============

    **Rate variables**

    ==============  ================================================= ==== =============
     Name            Description                                       Pbl      Unit
    ==============  ================================================= ==== =============
    RNSOIL           Rate of change on total soil mineral N            N   |kg ha-1 d-1|
    RPSOIL           Rate of change on total soil mineral P            N   |kg ha-1 d-1|
    RKSOIL           Rate of change on total soil mineral K            N   |kg ha-1 d-1|

    RNAVAIL          Total change in N availability                    N   |kg ha-1 d-1|
    RPAVAIL          Total change in P availability                    N   |kg ha-1 d-1|
    RKAVAIL          Total change in K availability                    N   |kg ha-1 d-1|

    # Rate of fertilizer supply for N/P/K [kg/ha/day]
    FERT_N_SUPPLY    Supply of fertilizer N. This will be supplied     N   |kg ha-1 d-1|
                     by the AgroManager module through the event
                     mechanism. See the section on signals below.
    FERT_P_SUPPLY    As previous for P                                 N   |kg ha-1 d-1|
    FERT_K_SUPPLY    As previous for K                                 N   |kg ha-1 d-1|
    
    RRUNOFF_N        Rate of N runoff                                  N   |kg ha-1 d-1|
    RRUNOFF_P        Rate of P runoff                                  N   |kg ha-1 d-1|
    RRUNOFF_K        Rate of K runoff                                  N   |kg ha-1 d-1|

    RNSUBSOIL        Rate of N from surface to subsoil                 N   |kg ha-1 d-1|
    RPSUBSOIL        Rate of N from surface to subsoil                 N   |kg ha-1 d-1|
    RKSUBSOIL        Rate of N from surface to subsoil                 N   |kg ha-1 d-1|
    ==============  ================================================= ==== =============

    **Signals send or handled**

    `NPK_Soil_Dynamics` receives the following signals:
        * APPLY_NPK: Is received when an external input from N/P/K fertilizer
          is provided. See `_on_APPLY_NPK()` for details.

    **External dependencies:**

    =========  =================================== ===================  ==============
     Name       Description                         Provided by          Unit
    =========  =================================== ===================  ==============
    DVS        Crop development stage              DVS_Phenology           -
    TRA        Actual crop transpiration           Evapotranspiration     |cm|
               increase
    TRAMX      Potential crop transpiration        Evapotranspiration     |cm|
               increase
    RNUPTAKE   Rate of N uptake by the crop        NPK_Demand_Uptake     |kg ha-1 d-1|
    RPUPTAKE   Rate of P uptake by the crop        NPK_Demand_Uptake     |kg ha-1 d-1|
    RKUPTAKE   Rate of K uptake by the crop        NPK_Demand_Uptake     |kg ha-1 d-1|
    DTSR       Rate of surface runoff              Classic_Waterbalance  |cm day-1|
    =========  =================================== ===================  ==============
    """

    NSOILI = Float(-99.) # initial soil N amount
    PSOILI = Float(-99.) # initial soil P amount
    KSOILI = Float(-99.) # initial soil K amount

    # placeholders for FERT_N/P/K_SUPPLY
    _FERT_N_SUPPLY = Float(0.)
    _FERT_P_SUPPLY = Float(0.)
    _FERT_K_SUPPLY = Float(0.)

    class Parameters(ParamTemplate):
        NSOILBASE    = Float(-99.)  # total mineral soil N available at start of growth period [kg N/ha]
        NSOILBASE_FR = Float(-99.)  # fraction of soil mineral N coming available per day [day-1]

        PSOILBASE    = Float(-99.)  # total mineral soil P available at start of growth period [kg N/ha]
        PSOILBASE_FR = Float(-99.)  # fraction of soil mineral P coming available per day [day-1]
        
        KSOILBASE    = Float(-99.)  # total mineral soil K available at start of growth period [kg N/ha]
        KSOILBASE_FR = Float(-99.)  # fraction of soil mineral K coming available per day [day-1]

        # Initial values of available nutrients which is different from the previous ones
        NAVAILI = Float(-99.)
        PAVAILI = Float(-99.)
        KAVAILI = Float(-99.)

        # Maximum values of available nutrients that soil can hold
        NMAX = Float(-99.)
        PMAX = Float(-99.)
        KMAX = Float(-99.)

        # Background rates of N/P/K supply [kg/ha/day]
        BG_N_SUPPLY = Float(-99.)
        BG_P_SUPPLY = Float(-99.)
        BG_K_SUPPLY = Float(-99.)

        # Max rate of nutrient uptake from surface to subsoil
        RNSOILMAX = Float(-99.)
        RPSOILMAX = Float(-99.)
        RKSOILMAX = Float(-99.)

        # Relative rate of absorption of surface nutrients to subsoil
        RNABSORPTION = Float(-99.)
        RPABSORPTION = Float(-99.)
        RKABSORPTION = Float(-99.)

        # Relative rate of nutrient surface runoff as function of surface runoff
        RNPKRUNOFF = AfgenTrait()

    class StateVariables(StatesTemplate):
        SURFACE_N = Float(-99.) # Mineral N on surface layer
        SURFACE_P = Float(-99.) # Mineral P on surface layer
        SURFACE_K = Float(-99.) # Mineral K on surface layer

        TOTN_RUNOFF = Float(-99.) # Total surface N runoff
        TOTP_RUNOFF = Float(-99.) # Total surface N runoff
        TOTK_RUNOFF = Float(-99.) # Total surface N runoff
        
        NSOIL = Float(-99.)  # mineral N available from soil for crop    kg N ha-1
        PSOIL = Float(-99.)  # mineral P available from soil for crop    kg N ha-1
        KSOIL = Float(-99.)  # mineral K available from soil for crop    kg N ha-1

        NAVAIL = Float(-99.)  # total mineral N from soil and fertiliser  kg N ha-1
        PAVAIL = Float(-99.)  # total mineral P from soil and fertiliser  kg N ha-1
        KAVAIL = Float(-99.)  # total mineral K from soil and fertiliser  kg N ha-1

        TOTN = Float(-99.) # total mineral N applied by fertilization kg N / ha
        TOTP = Float(-99.) # total mineral P applied by fertilization kg N / ha
        TOTK = Float(-99.) # total mineral K applied by fertilization kg N / ha
      
    class RateVariables(RatesTemplate):
        RNSOIL = Float(-99.)
        RPSOIL = Float(-99.)
        RKSOIL = Float(-99.)
        
        RNAVAIL = Float(-99.)
        RPAVAIL = Float(-99.)
        RKAVAIL = Float(-99.)

        # Rate of fertilizer supply for N/P/K [kg/ha/day]
        FERT_N_SUPPLY = Float()
        FERT_P_SUPPLY = Float()
        FERT_K_SUPPLY = Float()

        # Rate of mineral runoff
        RRUNOFF_N = Float(-99.)
        RRUNOFF_P = Float(-99.)
        RRUNOFF_K = Float(-99.)

        # Rate of surface to subsoil
        RNSUBSOIL = Float(-99.)
        RPSUBSOIL = Float(-99.)
        RKSUBSOIL = Float(-99.)

    def initialize(self, day:date, kiosk:VariableKiosk, parvalues:dict):
        """
        :param day: start date of the simulation
        :param kiosk: variable kiosk of this PCSE instance
        :param cropdata: dictionary with WOFOST cropdata key/value pairs
        """

        self.params = self.Parameters(parvalues)
        self.kiosk = kiosk
        
        # INITIAL STATES
        p = self.params
        self.NSOILI = p.NSOILBASE
        self.PSOILI = p.PSOILBASE
        self.KSOILI = p.KSOILBASE
        
        self.states = self.StateVariables(kiosk,
            publish=["NSOIL", "PSOIL", "KSOIL", "NAVAIL", "PAVAIL", "KAVAIL", 
                     "TOTN", "TOTP", "TOTK", "SURFACE_N", "SURFACE_P", "SURFACE_K",
                     "TOTN_RUNOFF", "TOTP_RUNOFF", "TOTK_RUNOFF"],
            NSOIL=p.NSOILBASE, PSOIL=p.PSOILBASE, KSOIL=p.KSOILBASE,
            NAVAIL=p.NAVAILI, PAVAIL=p.PAVAILI, KAVAIL=p.KAVAILI, 
            TOTN=0., TOTP=0., TOTK=0., SURFACE_N=0, SURFACE_P=0, SURFACE_K=0, 
            TOTN_RUNOFF=0, TOTP_RUNOFF=0, TOTK_RUNOFF=0)
        
        self.rates = self.RateVariables(kiosk, 
            publish=["RNSOIL", "RPSOIL", "RKSOIL", "RNAVAIL", "RPAVAIL", "RKAVAIL", 
                     "FERT_N_SUPPLY","FERT_P_SUPPLY", "FERT_K_SUPPLY", "RRUNOFF_N",
                     "RRUNOFF_P", "RRUNOFF_K", "RNSUBSOIL", "RPSUBSOIL", "RKSUBSOIL"])

        self._connect_signal(self._on_APPLY_NPK, signals.apply_npk)
        
    @prepare_rates
    def calc_rates(self, day:date, drv:WeatherDataProvider):
        """Compute Rates for model"""
        r = self.rates
        s = self.states
        p = self.params
        k = self.kiosk

        # Rate of supplied N/P/K
        r.FERT_N_SUPPLY = self._FERT_N_SUPPLY
        r.FERT_P_SUPPLY = self._FERT_P_SUPPLY
        r.FERT_K_SUPPLY = self._FERT_K_SUPPLY

        self._FERT_N_SUPPLY = 0.
        self._FERT_P_SUPPLY = 0.
        self._FERT_K_SUPPLY = 0.

        # Compute runoff rates
        r.RRUNOFF_N = s.SURFACE_N * p.RNPKRUNOFF(k.DTSR)
        r.RRUNOFF_P = s.SURFACE_P * p.RNPKRUNOFF(k.DTSR)
        r.RRUNOFF_K = s.SURFACE_K * p.RNPKRUNOFF(k.DTSR)

        # Relative rate of surface N to subsoil
        r.RNSUBSOIL = min(p.RNSOILMAX, s.SURFACE_N * p.RNABSORPTION)
        r.RPSUBSOIL = min(p.RPSOILMAX, s.SURFACE_P * p.RPABSORPTION)
        r.RKSUBSOIL = min(p.RKSOILMAX, s.SURFACE_K * p.RKABSORPTION)

        r.RNSOIL = -max(0., min(p.NSOILBASE_FR * self.NSOILI, s.NSOIL))
        r.RPSOIL = -max(0., min(p.PSOILBASE_FR * self.PSOILI, s.PSOIL))
        r.RKSOIL = -max(0., min(p.KSOILBASE_FR * self.KSOILI, s.KSOIL))

        # Check uptake rates from crop, if a crop is actually growing
        RNUPTAKE = k.RNUPTAKE if "RNUPTAKE" in self.kiosk else 0.
        RPUPTAKE = k.RPUPTAKE if "RPUPTAKE" in self.kiosk else 0.
        RKUPTAKE = k.RKUPTAKE if "RKUPTAKE" in self.kiosk else 0.

        r.RNAVAIL = r.RNSUBSOIL + p.BG_N_SUPPLY - RNUPTAKE - r.RNSOIL
        r.RPAVAIL = r.RPSUBSOIL + p.BG_P_SUPPLY - RPUPTAKE - r.RPSOIL
        r.RKAVAIL = r.RKSUBSOIL + p.BG_K_SUPPLY - RKUPTAKE - r.RKSOIL
        
    @prepare_states
    def integrate(self, day:date, delt:float=1.0):
        """Integrate states with rates
        """
        rates = self.rates
        states = self.states
        params = self.params

        # Compute the N on the surface
        states.SURFACE_N += (rates.FERT_N_SUPPLY - rates.RNSUBSOIL - rates.RRUNOFF_N)
        states.SURFACE_P += (rates.FERT_P_SUPPLY - rates.RPSUBSOIL - rates.RRUNOFF_P)
        states.SURFACE_K += (rates.FERT_K_SUPPLY - rates.RKSUBSOIL - rates.RRUNOFF_K)

        # Compute total nutrient runoff
        states.TOTN_RUNOFF += rates.RRUNOFF_N
        states.TOTP_RUNOFF += rates.RRUNOFF_P
        states.TOTK_RUNOFF += rates.RRUNOFF_K

        # mineral NPK amount in the soil
        states.NSOIL += rates.RNSOIL * delt
        states.PSOIL += rates.RPSOIL * delt
        states.KSOIL += rates.RKSOIL * delt
        
        # total (soil + fertilizer) NPK amount in soil
        states.NAVAIL += rates.RNAVAIL * delt
        states.PAVAIL += rates.RPAVAIL * delt
        states.KAVAIL += rates.RKAVAIL * delt

        # Clip values to max
        states.NAVAIL = min(states.NAVAIL, params.NMAX)
        states.PAVAIL = min(states.PAVAIL, params.PMAX)
        states.KAVAIL = min(states.KAVAIL, params.KMAX)


    def _on_APPLY_NPK(self, N_amount:float=None, P_amount:float=None, K_amount:float=None, 
                      N_recovery:float=None, P_recovery:float=None, K_recovery:float=None):
        """Apply NPK based on amounts and update relevant parameters
        """
        if N_amount is not None:
            self._FERT_N_SUPPLY = N_amount * N_recovery
            self.states.TOTN += N_amount
        if P_amount is not None:
            self._FERT_P_SUPPLY = P_amount * P_recovery
            self.states.TOTP += P_amount
        if K_amount is not None:
            self._FERT_K_SUPPLY = K_amount * K_recovery
            self.states.TOTK += K_amount

class NPK_Soil_Dynamics_PP(NPK_Soil_Dynamics):
    """A simple module for soil N/P/K dynamics.
    Assumes that there is abundant NPK available at all times

    """

    def initialize(self, day:date, kiosk:VariableKiosk, parvalues:dict):
        """
        :param day: start date of the simulation
        :param kiosk: variable kiosk of this PCSE instance
        :param cropdata: dictionary with WOFOST cropdata key/value pairs
        """

        super().initialize(day, kiosk, parvalues)
          
    @prepare_states
    def integrate(self, day:date, delt:float=1.0):
        """Integrate rates into states"""
        rates = self.rates
        states = self.states
        params = self.params

        states.SURFACE_N += (rates.FERT_N_SUPPLY - rates.RNSUBSOIL)
        states.SURFACE_P += (rates.FERT_P_SUPPLY - rates.RPSUBSOIL)
        states.SURFACE_K += (rates.FERT_K_SUPPLY - rates.RKSUBSOIL)

        # mineral NPK amount in the soil
        states.NSOIL += rates.RNSOIL * delt
        states.PSOIL += rates.RPSOIL * delt
        states.KSOIL += rates.RKSOIL * delt
        
        # total (soil + fertilizer) NPK amount in soil
        states.NAVAIL = params.NMAX
        states.PAVAIL = params.PMAX
        states.KAVAIL = params.KMAX

class NPK_Soil_Dynamics_LN(NPK_Soil_Dynamics):
    """A simple module for soil N/P/K dynamics.
    Assumes that there is abundant PK available at all times and only
    has limited N. 
    """
   
    def initialize(self, day:date, kiosk:VariableKiosk, parvalues:dict):
        """
        :param day: start date of the simulation
        :param kiosk: variable kiosk of this PCSE instance
        :param cropdata: dictionary with WOFOST cropdata key/value pairs
        """

        super().initialize(day, kiosk, parvalues)
        
    @prepare_states
    def integrate(self, day:date, delt:float=1.0):
        """Integrate rates
        """
        rates = self.rates
        states = self.states
        params = self.params

        states.SURFACE_N += (rates.FERT_N_SUPPLY - rates.RNSUBSOIL)
        states.SURFACE_P += (rates.FERT_P_SUPPLY - rates.RPSUBSOIL)
        states.SURFACE_K += (rates.FERT_K_SUPPLY - rates.RKSUBSOIL)

        # mineral NPK amount in the soil
        states.NSOIL += rates.RNSOIL * delt
        states.PSOIL += rates.RPSOIL * delt
        states.KSOIL += rates.RKSOIL * delt
        
        # total (soil + fertilizer) NPK amount in soil
        states.NAVAIL += rates.RNAVAIL * delt
        states.PAVAIL = params.PMAX
        states.KAVAIL = params.KMAX

        # Clip states in range
        states.NAVAIL = min(states.NAVAIL, params.NMAX)
        

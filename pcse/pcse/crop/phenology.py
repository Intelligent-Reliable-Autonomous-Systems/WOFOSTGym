"""Implementation of  models for phenological development in WOFOST

Classes defined here:
- DVS_Phenology: Implements the algorithms for phenologic development
- Vernalisation: 

Written by: Allard de Wit (allard.dewit@wur.nl), April 2014
Modified by Will Solow, 2024
"""
import datetime

from ..utils.traitlets import Float, Instance, Enum, Bool, Int, Dict
from ..utils.decorators import prepare_rates, prepare_states

from ..util import limit, AfgenTrait, daylength
from ..base import ParamTemplate, StatesTemplate, RatesTemplate, \
     SimulationObject, VariableKiosk
from ..utils import signals
from ..utils import exceptions as exc
from ..nasapower import WeatherDataProvider

def daily_temp_units(drv: WeatherDataProvider, T0BC: float, TMBC: float):
    """
    Compute the daily temperature units using the BRIN model.
    Used for predicting budbreak in grapes.

    Slightly modified to not use the min temp at day n+1, but rather reuse the min
    temp at day n
    """
    A_c = 0
    for h in range(1, 25):
        # Perform linear interpolation between the hours 1 and 24
        if h <= 12:
            T_n = drv.TMIN + h * ((drv.TMAX - drv.TMIN) / 12)
        else:
            T_n = drv.TMAX - (h - 12) * ((drv.TMAX - drv.TMIN) / 12)

        # Limit the interpolation based on parameters
        T_n = limit(0, TMBC - T0BC, T_n - T0BC)
        A_c += T_n

    return A_c / 24
            

class Vernalisation(SimulationObject):
    """ Modification of phenological development due to vernalisation.
    
    The vernalization approach here is based on the work of Lenny van Bussel
    (2011), which in turn is based on Wang and Engel (1998). The basic
    principle is that winter wheat needs a certain number of days with temperatures
    within an optimum temperature range to complete its vernalisation
    requirement. Until the vernalisation requirement is fulfilled, the crop
    development is delayed.
    
    The rate of vernalization (VERNR) is defined by the temperature response
    function VERNRTB. Within the optimal temperature range 1 day is added
    to the vernalisation state (VERN). The reduction on the phenological
    development is calculated from the base and saturated vernalisation
    requirements (VERNBASE and VERNSAT). The reduction factor (VERNFAC) is
    scaled linearly between VERNBASE and VERNSAT.
    
    A critical development stage (VERNDVS) is used to stop the effect of
    vernalisation when this DVS is reached. This is done to improve model
    stability in order to avoid that Anthesis is never reached due to a
    somewhat too high VERNSAT. Nevertheless, a warning is written to the log
    file, if this happens.   
    
    * Van Bussel, 2011. From field to globe: Upscaling of crop growth modelling.
      Wageningen PhD thesis. http://edepot.wur.nl/180295
    * Wang and Engel, 1998. Simulation of phenological development of wheat
      crops. Agric. Systems 58:1 pp 1-24

    *Simulation parameters* (provide in cropdata dictionary)
    
    ======== ============================================= =======  ============
     Name     Description                                   Type     Unit
    ======== ============================================= =======  ============
    VERNSAT  Saturated vernalisation requirements           SCr        days
    VERNBASE Base vernalisation requirements                SCr        days
    VERNRTB  Rate of vernalisation as a function of daily   TCr        -
             mean temperature.
    VERNDVS  Critical development stage after which the     SCr        -
             effect of vernalisation is halted
    ======== ============================================= =======  ============

    **State variables**

    ============ ================================================= ==== ========
     Name        Description                                       Pbl   Unit
    ============ ================================================= ==== ========
    VERN         Vernalisation state                                N    days
    DOV          Day when vernalisation requirements are            N    -
                 fulfilled.
    ISVERNALISED Flag indicated that vernalisation                  Y    -
                 requirement has been reached
    ============ ================================================= ==== ========


    **Rate variables**

    =======  ================================================= ==== ============
     Name     Description                                      Pbl      Unit
    =======  ================================================= ==== ============
    VERNR    Rate of vernalisation                              N     -
    VERNFAC  Reduction factor on development rate due to        Y     -
             vernalisation effect.
    =======  ================================================= ==== ============

    
    **External dependencies:**

    ============ =============================== ========================== =====
     Name        Description                         Provided by             Unit
    ============ =============================== ========================== =====
    DVS          Development Stage                 Phenology                 -
                 Used only to determine if the
                 critical development stage for
                 vernalisation (VERNDVS) is
                 reached.
    ============ =============================== ========================== =====
    """
    # Helper variable to indicate that DVS > VERNDVS
    _force_vernalisation = Bool(False)

    class Parameters(ParamTemplate):
        VERNSAT = Float(-99.)     # Saturated vernalisation requirements
        VERNBASE = Float(-99.)     # Base vernalisation requirements
        VERNRTB = AfgenTrait()    # Vernalisation temperature response
        VERNDVS = Float(-99.)     # Critical DVS for vernalisation fulfillment

    class RateVariables(RatesTemplate):
        VERNR = Float(-99.)        # Rate of vernalisation
        VERNFAC = Float(-99.)      # Red. factor for phenol. devel.

    class StateVariables(StatesTemplate):
        VERN = Float(-99.)              # Vernalisation state
                                            # requirements are fulfilled
        ISVERNALISED =  Bool()              # True when VERNSAT is reached and
                                            # Forced when DVS > VERNDVS

    def initialize(self, day:datetime.date, kiosk:VariableKiosk, parvalues:dict):
        """
        :param day: start date of the simulation
        :param kiosk: variable kiosk of this PCSE  instance
        :param cropdata: dictionary with WOFOST cropdata key/value pairs

        """
        self.params = self.Parameters(parvalues)
        self.kiosk = kiosk

        # Define initial states
        self.states = self.StateVariables(kiosk, VERN=0., ISVERNALISED=False,
                                          publish=["VERN", "ISVERNALISED"])
        
        self.rates = self.RateVariables(kiosk, publish=["VERNR", "VERNFAC"])
        
    @prepare_rates
    def calc_rates(self, day:datetime.date, drv:WeatherDataProvider):
        """Compute state rates for integration
        """
        rates = self.rates
        states = self.states
        params = self.params

        DVS = self.kiosk["DVS"]
        if not states.ISVERNALISED:
            if DVS < params.VERNDVS:
                rates.VERNR = params.VERNRTB(drv.TEMP)
                r = (states.VERN - params.VERNBASE)/(params.VERNSAT-params.VERNBASE)
                rates.VERNFAC = limit(0., 1., r)
            else:
                rates.VERNR = 0.
                rates.VERNFAC = 1.0
                self._force_vernalisation = True
        else:
            rates.VERNR = 0.
            rates.VERNFAC = 1.0

    @prepare_states
    def integrate(self, day:datetime.date, delt:float=1.0):
        """Integrate state rates
        """
        states = self.states
        rates = self.rates
        params = self.params
        
        states.VERN += rates.VERNR
        
        if states.VERN >= params.VERNSAT:  # Vernalisation requirements reached
            states.ISVERNALISED = True

            msg = "Vernalization requirements reached at day %s."
            self.logger.info(msg % day)

        elif self._force_vernalisation:  # Critical DVS for vernalisation reached
            # Force vernalisation, but do not set DOV
            states.ISVERNALISED = True

            # Write log message to warn about forced vernalisation
            msg = ("Critical DVS for vernalization (VERNDVS) reached " +
                   "at day %s, " +
                   "but vernalization requirements not yet fulfilled. " +
                   "Forcing vernalization now (VERN=%f).")
            self.logger.info(msg % (day, states.VERN))

        else:  # Reduction factor for phenologic development
            states.ISVERNALISED = False

    def reset(self):
        """Reset states and rates
        """
        s = self.states
        r = self.rates

        # Define initial states
        s.VERN=0.
        s.ISVERNALISED=False
        self._force_vernalisation = False
        
        r.VERNR = r.VERNFAC = 0

class Base_Phenology(SimulationObject):
    """Implements the algorithms for phenologic development in WOFOST.
    
    Phenologic development in WOFOST is expresses using a unitless scale which
    takes the values 0 at emergence, 1 at Anthesis (flowering) and 2 at
    maturity. This type of phenological development is mainly representative
    for cereal crops. All other crops that are simulated with WOFOST are
    forced into this scheme as well, although this may not be appropriate for
    all crops. For example, for potatoes development stage 1 represents the
    start of tuber formation rather than flowering.
    
    Phenological development is mainly governed by temperature and can be
    modified by the effects of day length and vernalization 
    during the period before Anthesis. After Anthesis, only temperature
    influences the development rate.


    **Simulation parameters**
    
    =======  ============================================= =======  ============
     Name     Description                                   Type     Unit
    =======  ============================================= =======  ============
    TSUMEM   Temperature sum from sowing to emergence       SCr        |C| day
    TBASEM   Base temperature for emergence                 SCr        |C|
    TEFFMX   Maximum effective temperature for emergence    SCr        |C|
    TSUM1    Temperature sum from emergence to anthesis     SCr        |C| day
    TSUM2    Temperature sum from anthesis to maturity      SCr        |C| day
    TSUM3    Temperature sum form maturity to death         SCr        |C| day
    IDSL     Switch for phenological development options    SCr        -
             temperature only (IDSL=0), including           SCr
             daylength (IDSL=1) and including               
             vernalization (IDSL>=2)
    DLO      Optimal daylength for phenological             SCr        hr
             development
    DLC      Critical daylength for phenological            SCr        hr
             development
    DVSI     Initial development stage at emergence.        SCr        -
             Usually this is zero, but it can be higher
             for crops that are transplanted (e.g. paddy
             rice)
    DVSEND   Final development stage                        SCr        -
    DTSMTB   Daily increase in temperature sum as a         TCr        |C|
             function of daily mean temperature.
    DTBEM    Days at TBASEM required for crop to start      TCr        |C|
    =======  ============================================= =======  ============

    **State variables**

    =======  ================================================= ==== ============
     Name     Description                                      Pbl      Unit
    =======  ================================================= ==== ============
    DVS      Development stage                                  Y    - 
    TSUM     Temperature sum                                    N    |C| day
    TSUME    Temperature sum for emergence                      N    |C| day
    DOS      Day of sowing                                      N    - 
    DOE      Day of emergence                                   N    - 
    DOA      Day of Anthesis                                    N    - 
    DOM      Day of maturity                                    N    - 
    DOH      Day of harvest                                     N    -
    STAGE    Current phenological stage, can take the           N    -
             folowing values:
             `emerging|vegetative|reproductive|mature`
    DATBE    Days above Temperature sum for emergence           N    days
    =======  ================================================= ==== ============

    **Rate variables**

    =======  ================================================= ==== ============
     Name     Description                                      Pbl      Unit
    =======  ================================================= ==== ============
    DTSUME   Increase in temperature sum for emergence          N    |C|
    DTSUM    Increase in temperature sum for anthesis or        N    |C|
             maturity
    DVR      Development rate                                   Y    |day-1|
    RDEM     Day counter for if day is suitable for germination Y    day
    =======  ================================================= ==== ============
    
    **External dependencies:**

    None    

    **Signals sent or handled**
    
    `DVS_Phenology` sends the `crop_finish` signal when maturity is
    reached and the `end_type` is 'maturity'.
    
    """
    # Placeholder for start/stop types and vernalisation module
    vernalisation = Instance(Vernalisation)

    class Parameters(ParamTemplate):
        TSUMEM = Float(-99.)  # Temp. sum for emergence
        TBASEM = Float(-99.)  # Base temp. for emergence
        TEFFMX = Float(-99.)  # Max eff temperature for emergence
        TSUM1  = Float(-99.)  # Temperature sum emergence to anthesis
        TSUM2  = Float(-99.)  # Temperature sum anthesis to maturity
        TSUM3  = Float(-99.)  # Temperature sum from maturity to death
        IDSL   = Float(-99.)  # Switch for photoperiod (1) and vernalisation (2)
        DLO    = Float(-99.)  # Optimal day length for phenol. development
        DLC    = Float(-99.)  # Critical day length for phenol. development
        DVSI   = Float(-99.)  # Initial development stage
        DVSM   = Float(-99.)  # Mature development stage
        DVSEND = Float(-99.)  # Final development stage
        DTSMTB = AfgenTrait() # Temperature response function for phenol.
                              # development.
        CROP_START_TYPE = Enum(["dormant", "sowing", "emergence"])
        CROP_END_TYPE = Enum(["sowing", "emergence", "maturity", "harvest", "death", "max_duration"])
        DTBEM  = Int(-99)

    class RateVariables(RatesTemplate):
        DTSUME = Float(-99.)  # increase in temperature sum for emergence
        DTSUM  = Float(-99.)  # increase in temperature sum
        DVR    = Float(-99.)  # development rate
        RDEM   = Int(-99.)    # Days above temp sum

    class StateVariables(StatesTemplate):
        DVS = Float(-99.)  # Development stage
        TSUM = Float(-99.)  # Temperature sum state
        TSUME = Float(-99.)  # Temperature sum for emergence state
        # States which register phenological events
        DOP = Instance(datetime.date) # Day of planting
        STAGE = Enum(["sowing", "emerging", "vegetative", "reproductive", "mature", "dead"])
        DATBE = Int(-99)  # Current number of days above TSUMEM

    def initialize(self, day:datetime.date, kiosk:VariableKiosk, parvalues:dict):
        """
        :param day: start date of the simulation
        :param kiosk: variable kiosk of this PCSE  instance
        :param parvalues: `ParameterProvider` object providing parameters as
                key/value pairs
        """
        msg = "Base Phenology not implemented - implement in subclass!"
        raise NotImplementedError(msg)
        
    def _get_initial_stage(self, day:datetime.date):
        """Set the initial state of the crop given the start type
        """
        p = self.params

        # Define initial stage type (emergence/sowing) and fill the
        # respective day of sowing/emergence (DOS/DOE)
        if p.CROP_START_TYPE == "emergence":
            STAGE = "vegetative"
            DVS = p.DVSI
            DOP = day
            # send signal to indicate crop emergence
            self._send_signal(signals.crop_emerged)

        elif p.CROP_START_TYPE == "sowing":
            STAGE = "emerging"
            DOP = day
            DVS = -0.1
        elif p.CROP_START_TYPE == "dormant":
            STAGE = "sowing"
            DOP = day
            DVS = -0.1
        else:
            msg = "Unknown start type: %s. Are you using the corect Phenology \
                module (Calling the correct Gym Environment)?" % p.CROP_START_TYPE
            raise exc.PCSEError(msg)
            
        return DVS, DOP, STAGE

    @prepare_rates
    def calc_rates(self, day, drv):
        """Calculates the rates for phenological development
        """
        p = self.params
        r = self.rates
        s = self.states

        # Day length sensitivity
        DVRED = 1.
        if p.IDSL >= 1:
            DAYLP = daylength(day, drv.LAT)
            DVRED = limit(0., 1., (DAYLP - p.DLC)/(p.DLO - p.DLC))

        # Vernalisation
        VERNFAC = 1.
        if p.IDSL >= 2:
            if s.STAGE == 'vegetative':
                self.vernalisation.calc_rates(day, drv)
                VERNFAC = self.kiosk["VERNFAC"]

        # Development rates
        if s.STAGE == "sowing":
            r.DTSUME = 0.
            r.DTSUM = 0.
            r.DVR = 0.
            if drv.TEMP > p.TBASEM:
                r.RDEM = 1
            else:
                r.RDEM = 0
        elif s.STAGE == "emerging":
            r.DTSUME = limit(0., (p.TEFFMX - p.TBASEM), (drv.TEMP - p.TBASEM))
            r.DTSUM = 0.
            r.DVR = 0.1 * r.DTSUME/p.TSUMEM
            r.RDEM = 0
        elif s.STAGE == 'vegetative':
            r.DTSUME = 0.
            r.DTSUM = p.DTSMTB(drv.TEMP) * VERNFAC * DVRED
            r.DVR = r.DTSUM/p.TSUM1
            r.RDEM = 0
        elif s.STAGE == 'reproductive':
            r.DTSUME = 0.
            r.DTSUM = p.DTSMTB(drv.TEMP)
            r.DVR = r.DTSUM/p.TSUM2
            r.RDEM = 0
        elif s.STAGE == 'mature':
            r.DTSUME = 0.
            r.DTSUM = p.DTSMTB(drv.TEMP)
            r.DVR = r.DTSUM/p.TSUM3
            r.RDEM = 0
        elif s.STAGE == 'dead':
            r.DTSUME = 0.
            r.DTSUM = 0.
            r.DVR = 0.
            r.RDEM = 0
        else:  # Problem: no stage defined
            msg = "Unrecognized STAGE defined in phenology submodule: %s."
            raise exc.PCSEError(msg, self.states.STAGE)
        
        msg = "Finished rate calculation for %s"
        self.logger.debug(msg % day)
        
    @prepare_states
    def integrate(self, day, delt=1.0):
        """Updates the state variable and checks for phenologic stages
        """

        p = self.params
        r = self.rates
        s = self.states

        # Integrate vernalisation module
        if p.IDSL >= 2:
            if s.STAGE == 'vegetative':
                self.vernalisation.integrate(day, delt)
            else:
                self.vernalisation.touch()

        # Integrate phenologic states
        s.TSUME += r.DTSUME
        s.DVS += r.DVR
        s.TSUM += r.DTSUM
        s.DATBE += r.RDEM

        # Check if a new stage is reached
        if s.STAGE == "sowing":
            if s.DATBE >= p.DTBEM:
                self._next_stage(day)
                s.DVS = -0.1
                s.DATBE = 0
        elif s.STAGE == "emerging":
            if s.DVS >= 0.0:
                self._next_stage(day)
                s.DVS = 0.
        elif s.STAGE == 'vegetative':
            if s.DVS >= 1.0:
                self._next_stage(day)
                s.DVS = 1.0
        elif s.STAGE == 'reproductive':
            if s.DVS >= p.DVSM:
                self._next_stage(day)
                s.DVS = p.DVSM
        elif s.STAGE == 'mature':
            if s.DVS >= p.DVSEND:
                self._next_stage(day)
                s.DVS = p.DVSEND
        elif s.STAGE == 'dead':
            pass 
        else: # Problem no stage defined
            msg = "No STAGE defined in phenology submodule"
            raise exc.PCSEError(msg)
            
        msg = "Finished state integration for %s"
        self.logger.debug(msg % day)

    def _next_stage(self, day):
        """Moves states.STAGE to the next phenological stage"""
        s = self.states
        p = self.params

        current_STAGE = s.STAGE
        if s.STAGE == "sowing":
            s.STAGE = "emerging"

        elif s.STAGE == "emerging":
            s.STAGE = "vegetative"
            # send signal to indicate crop emergence
            self._send_signal(signals.crop_emerged)

            if p.CROP_END_TYPE in ["emergence"]:
                self._send_signal(signal=signals.crop_finish,
                                  day=day, finish_type="emergence",
                                  crop_delete=True)
        elif s.STAGE == "vegetative":
            s.STAGE = "reproductive"
                
        elif s.STAGE == "reproductive":
            s.STAGE = "mature"
            if p.CROP_END_TYPE in ["maturity"]:
                self._send_signal(signal=signals.crop_finish,
                                  day=day, finish_type="maturity",
                                  crop_delete=True)
        elif s.STAGE == "mature":
            s.STAGE = "dead"
            if p.CROP_END_TYPE in ["death"]:
                self._send_signal(signal=signals.crop_finish,
                                    day=day, finish_type="death",
                                    crop_delete=True)
        elif s.STAGE == "dead":
            msg = "Cannot move to next phenology stage: maturity already reached!"
            raise exc.PCSEError(msg)

        else: # Problem no stage defined
            msg = "No STAGE defined in phenology submodule."
            raise exc.PCSEError(msg)
        
        msg = "Changed phenological stage '%s' to '%s' on %s"
        self.logger.info(msg % (current_STAGE, s.STAGE, day))

    def _on_CROP_HARVEST(self, day):
        if self.params.CROP_END_TYPE in ["harvest"]:
            self._send_signal(signal=signals.crop_finish,day=day,finish_type="harvest",
                              crop_delete=True)

    def _on_CROP_FINISH(self, day, finish_type=None):
        """Handler for setting day of harvest (DOH). Although DOH is not
        strictly related to phenology (but to management) this is the most
        logical place to put it.
        """
        if finish_type in ['harvest']:
            self._for_finalize["DOH"] = day

class Annual_Phenology(Base_Phenology):
    """Annual Phenology for the crop. Inherits from the Base_Phenology class
    """

    def initialize(self, day: datetime.date, kiosk: VariableKiosk, parvalues: dict):
        """
        :param day: start date of the simulation
        :param kiosk: variable kiosk of this PCSE  instance
        :param parvalues: `ParameterProvider` object providing parameters as
                key/value pairs
        """
        self.params = self.Parameters(parvalues)
        self.kiosk = kiosk

        self._connect_signal(self._on_CROP_FINISH, signal=signals.crop_finish)

        # Define initial states
        DVS, DOP, STAGE = self._get_initial_stage(day)
        self.states = self.StateVariables(kiosk, 
                                          publish=["DVS", "TSUM", "TSUME", 
                                                   "STAGE", "DOP", "DATBE" ],
                                          TSUM=0., TSUME=0., DOP=DOP, DVS=DVS,
                                          STAGE=STAGE, DATBE=0)
        
        self.rates = self.RateVariables(kiosk, publish=["DTSUME", "DTSUM", "DVR", "RDEM"])

        # initialize vernalisation for IDSL=2
        if self.params.IDSL >= 2:
            self.vernalisation = Vernalisation(day, kiosk, parvalues)

class Perennial_Phenology(Base_Phenology):
    """Perennial Phenology class for the crop. Inherits from the Base_Phenology class.
    
    Includes the `dormant` state in which no growth occurs. See the table below for
    added state, rate, and parameter values 

    **Simulation parameters**
    
    =======  ============================================= =======  ============
     Name     Description                                   Type     Unit
    =======  ============================================= =======  ============
    DORM      Dormancy threshold after which the plant       Scr        day 
              enters dormancy    
    DORMCD    The number of days a plant will stay dormant   Scr        day
    AGEI      The initial age of the crop in years           Scr        year
    DCYCLEMAX The maximum number of days in a crop cycle     Scr        day
               before dormancy
    MLDORM    The daylength threshold at which a plant goes  SCR        hr
                into dormancy
    **State variables**

    =======  ================================================= ==== ============
     Name     Description                                      Pbl      Unit
    =======  ================================================= ==== ============
    DSNG     Days since no crop growth                          Y    day
    DSD      Days since dormancy started                        Y    day
    AGE      Age of the crop in years                           Y    year
    DCYCLE   Number of days in current crop cycle               Y    day
    =======  ================================================= ==== ============

    **Rate variables**

    =======  ================================================= ==== ============
     Name     Description                                      Pbl      Unit
    =======  ================================================= ==== ============

    =======  ================================================= ==== ============
    """
    # Day length helper variable
    _DAY_LENGTH = Float(0)

    class Parameters(ParamTemplate):
        TSUMEM = Float(-99.)  # Temp. sum for emergence
        TBASEM = Float(-99.)  # Base temp. for emergence
        TEFFMX = Float(-99.)  # Max eff temperature for emergence
        TSUM1  = Float(-99.)  # Temperature sum emergence to anthesis
        TSUM2  = Float(-99.)  # Temperature sum anthesis to maturity
        TSUM3  = Float(-99.)  # Temperature sum from maturity to death
        IDSL   = Float(-99.)  # Switch for photoperiod (1) and vernalisation (2)
        DLO    = Float(-99.)  # Optimal day length for phenol. development
        DLC    = Float(-99.)  # Critical day length for phenol. development
        DVSI   = Float(-99.)  # Initial development stage
        DVSM   = Float(-99.)  # Mature development stage
        DVSEND = Float(-99.)  # Final development stage
        DTSMTB = AfgenTrait() # Temperature response function for phenol.
                              # development.
        CROP_START_TYPE = Enum(["sowing", "emergence", "dormant"])
        CROP_END_TYPE = Enum(["sowing", "emergence", "maturity", "harvest", "death", "max_duration"])
        DORM   = Int(-99)     # Days after no growth at which crop transitions to dormancy
        DORMCD = Int(-99)     # Minimum days in dormancy
        AGEI   = Int(-99)     # Initial Tree age
        DCYCLEMAX = Int(-99)   # Maximum number of days in crop cycle before dormancy
        DTBEM  = Int(-99)     # Number of days above emergence temp required for germination
        MLDORM = Float(-99.)  # Daylength at which a plant will go into dormancy

    class StateVariables(StatesTemplate):
        DVS   = Float(-99.)  # Development stage
        TSUM  = Float(-99.)  # Temperature sum state
        TSUME = Float(-99.)  # Temperature sum for emergence state
        # States which register phenological events
        DOP    = Instance(datetime.date) # Day of planting
        STAGE  = Enum(["dormant", "sowing", "emerging", "vegetative", "reproductive", "mature", "dead"])
        DSNG   = Int(-99) # Days since no growth
        DSD    = Int(-99) # Days since dormancy
        AGE    = Int(-99) # Age of crop (years)
        DCYCLE = Int(-99) # Days in Crop cycle
        DATBE = Int(-99)  # Current number of days above TSUMEM

    def initialize(self, day: datetime.date, kiosk: VariableKiosk, parvalues: dict):
        self.params = self.Parameters(parvalues)
        self.kiosk = kiosk

        self._connect_signal(self._on_CROP_FINISH, signal=signals.crop_finish)
        self._connect_signal(self._on_DORMANT, signal=signals.crop_dormant)
        AGEI = self.params.AGEI
        # Define initial states
        DVS, DOP, STAGE = self._get_initial_stage(day)
        self.states = self.StateVariables(kiosk, 
                                          publish=["DVS", "TSUM", "TSUME", 
                                                   "STAGE", "DSNG", "DSD", "AGE",
                                                   "DCYCLE", "DATBE", "DOP"],
                                          TSUM=0., TSUME=0., DVS=DVS, STAGE=STAGE, DSNG=0,
                                          DSD=0, AGE=AGEI, DCYCLE=0,DATBE=0, DOP=DOP)
        
        self.rates = self.RateVariables(kiosk, publish=["DTSUME", "DTSUM", "DVR"])

        # initialize vernalisation for IDSL=2
        if self.params.IDSL >= 2:
            self.vernalisation = Vernalisation(day, kiosk, parvalues)

    @prepare_rates
    def calc_rates(self, day, drv):
        """Calculates the rates for phenological development
        """
        p = self.params
        r = self.rates
        s = self.states

        # Day length sensitivity
        DVRED = 1.
        DAYLP = daylength(day, drv.LAT)
        self._DAY_LENGTH = DAYLP
        if p.IDSL >= 1:
            DVRED = limit(0., 1., (DAYLP - p.DLC)/(p.DLO - p.DLC))

        # Vernalisation
        VERNFAC = 1.
        if p.IDSL >= 2:
            if s.STAGE == 'vegetative':
                self.vernalisation.calc_rates(day, drv)
                VERNFAC = self.kiosk["VERNFAC"]

        # Development rates
        if s.STAGE == "sowing":
            r.DTSUME = 0.
            r.DTSUM = 0.
            r.DVR = 0.
            if drv.TEMP > p.TBASEM:
                r.RDEM = 1
            else:
                r.RDEM = 0
        elif s.STAGE == "emerging":
            r.DTSUME = limit(0., (p.TEFFMX - p.TBASEM), (drv.TEMP - p.TBASEM))
            r.DTSUM = 0.
            r.DVR = 0.1 * r.DTSUME/p.TSUMEM
            r.RDEM = 0
        elif s.STAGE == 'vegetative':
            r.DTSUME = 0.
            r.DTSUM = p.DTSMTB(drv.TEMP) * VERNFAC * DVRED
            r.DVR = r.DTSUM/p.TSUM1
            r.RDEM = 0
        elif s.STAGE == 'reproductive':
            r.DTSUME = 0.
            r.DTSUM = p.DTSMTB(drv.TEMP)
            r.DVR = r.DTSUM/p.TSUM2
            r.RDEM = 0
        elif s.STAGE == 'mature':
            r.DTSUME = 0.
            r.DTSUM = p.DTSMTB(drv.TEMP)
            r.DVR = r.DTSUM/p.TSUM3
            r.RDEM = 0
        elif s.STAGE == 'dead':
            r.DTSUME = 0.
            r.DTSUM = 0.
            r.DVR = 0.
            r.RDEM = 0
        elif s.STAGE == 'dormant':
            r.DTSUME = 0.
            r.DTSUM = 0.
            r.DVR = 0.
            r.RDEM = 0
        else:  # Problem: no stage defined
            msg = "Unrecognized STAGE defined in phenology submodule: %s"
            raise exc.PCSEError(msg, self.states.STAGE)
    
        msg = "Finished rate calculation for %s"
        self.logger.debug(msg % day)
        
    @prepare_states
    def integrate(self, day, delt=1.0):
        """Updates the state variable and checks for phenologic stages
        """

        p = self.params
        r = self.rates
        s = self.states
        # Integrate vernalisation module
        if p.IDSL >= 2:
            if s.STAGE == 'vegetative':
                self.vernalisation.integrate(day, delt)
            else:
                self.vernalisation.touch()

        # Integrate phenologic states
        s.TSUME += r.DTSUME
        s.DVS += r.DVR
        s.TSUM += r.DTSUM

        # Require that days above temperature sum must be consecutive
        if r.RDEM == 0:
            s.DATBE = 0
        else:
            s.DATBE += r.RDEM

        # Increment plant age based on Day of Planting
        # Handles leap years
        if s.DOP.day == day.day and s.DOP.month == day.month:
            s.AGE += 1 
        else:
            s.AGE += 0

        # Compute the accumulated dates of no growth
        if r.DVR == 0 and s.STAGE != "emerging" and s.STAGE != "sowing":
            s.DSNG += 1
        else:
            s.DSNG = 0

        # Check if a new stage is reached
        if s.STAGE == "sowing":
            if s.DATBE >= p.DTBEM:
                self._next_stage(day)
                s.DVS = -0.1
                s.DATBE = 0
        elif s.STAGE == "emerging":
            s.DCYCLE += 1
            if s.DVS >= 0.0:
                self._next_stage(day)
                s.DVS = 0.
        elif s.STAGE == 'vegetative':
            s.DCYCLE += 1
            if s.DVS >= 1.0:
                self._next_stage(day)
                s.DVS = 1.0
            if s.DSNG >= p.DORM or s.DCYCLE >= p.DCYCLEMAX or self._DAY_LENGTH < p.MLDORM:
                s.STAGE = "dormant"
        elif s.STAGE == 'reproductive':
            s.DCYCLE += 1
            if s.DVS >= p.DVSM:
                self._next_stage(day)
                s.DVS = p.DVSM
            if s.DSNG >= p.DORM or s.DCYCLE >= p.DCYCLEMAX or self._DAY_LENGTH < p.MLDORM:
                s.STAGE = "dormant"
        elif s.STAGE == 'mature':
            s.DCYCLE += 1
            if s.DVS >= p.DVSEND:
                self._next_stage(day)
                s.DVS = p.DVSEND
            if s.DSNG >= p.DORM or s.DCYCLE >= p.DCYCLEMAX or self._DAY_LENGTH < p.MLDORM:
                s.STAGE = "dormant"
        elif s.STAGE == "dormant":
            if s.DSD >= p.DORMCD:
                s.STAGE = "sowing"
                s.DVS = -0.1
                s.DSD = 0
            else:
                # If we are on the first stage of dormancy, send signal to 
                # reset all crop modules
                if s.DSD == 0:
                    s.DCYCLE = 0
                    s.DVS = -0.2
                    self._send_signal(signal=signals.crop_dormant, day=day)
                s.DSD +=1
        elif s.STAGE == 'dead':
            s.DCYCLE += 1
            if s.DSNG >= p.DORM or s.DCYCLE >= p.DCYCLEMAX:
                s.STAGE = "dormant"
                s.DVS= -0.1
                s.DSD = 0
        else: # Problem no stage defined
            msg = "No STAGE defined in phenology submodule"
            raise exc.PCSEError(msg)
            
        msg = "Finished state integration for %s"
        self.logger.debug(msg % day)
        self._DAY_LENGTH = 0

    def _next_stage(self, day:datetime.date):
        """Moves states.STAGE to the next phenological stage"""
        s = self.states
        p = self.params

        current_STAGE = s.STAGE
        if s.STAGE == "sowing":
            s.STAGE = "emerging"
        elif s.STAGE == "emerging":
            s.STAGE = "vegetative"
            # send signal to indicate crop emergence
            self._send_signal(signals.crop_emerged)

            if p.CROP_END_TYPE in ["emergence"]:
                self._send_signal(signal=signals.crop_finish,
                                  day=day, finish_type="emergence",
                                  crop_delete=True)
        elif s.STAGE == "vegetative":
            s.STAGE = "reproductive"
                
        elif s.STAGE == "reproductive":
            s.STAGE = "mature"
            if p.CROP_END_TYPE in ["maturity"]:
                self._send_signal(signal=signals.crop_finish,
                                  day=day, finish_type="maturity",
                                  crop_delete=True)
        elif s.STAGE == "mature":
            s.STAGE = "dead"
            self._send_signal(signal=signals.crop_death, day=day)

            if p.CROP_END_TYPE in ["death"]:
                self._send_signal(signal=signals.crop_finish,
                                    day=day, finish_type="death",
                                    crop_delete=True)
        elif s.STAGE == "dead":
            msg = "Cannot move to next phenology stage: maturity already reached!"
            raise exc.PCSEError(msg)

        else: # Problem no stage defined
            msg = "No STAGE defined in phenology submodule."
            raise exc.PCSEError(msg)
        
        msg = "Changed phenological stage '%s' to '%s' on %s"
        self.logger.info(msg % (current_STAGE, s.STAGE, day))

    def _on_DORMANT(self, day:datetime.date):
        """Handler for dormant signal. Reset all nonessential states and rates to 0
        """
        if self.params.IDSL >= 2:
            self.vernalisation.reset()
        s = self.states
        r = self.rates

        s.TSUM  = 0
        s.TSUME = 0

        r.DTSUME = 0 
        r.DTSUM  = 0
        r.DVR    = 0

class Grape_Phenology(SimulationObject):
    """Implements grape phenology based on many papers provided by Markus Keller
    at Washington State University
    
    Phenologic development in WOFOST is expresses using a unitless scale which
    takes the values 0 at emergence, 1 at Anthesis (flowering) and 2 at
    maturity. This type of phenological development is mainly representative
    for cereal crops. All other crops that are simulated with WOFOST are
    forced into this scheme as well, although this may not be appropriate for
    all crops. For example, for potatoes development stage 1 represents the
    start of tuber formation rather than flowering.
    
    Phenological development is mainly governed by temperature and can be
    modified by the effects of day length and vernalization 
    during the period before Anthesis. After Anthesis, only temperature
    influences the development rate.


    **Simulation parameters**
    
    =======  ============================================= =======  ============
     Name     Description                                   Type     Unit
    =======  ============================================= =======  ============
    TSUMEM   Temperature sum from sowing to emergence       SCr        |C| day
    TBASEM   Base temperature for emergence                 SCr        |C|
    TEFFMX   Maximum effective temperature for emergence    SCr        |C|
    TSUM1    Temperature sum from emergence to anthesis     SCr        |C| day
    TSUM2    Temperature sum from anthesis to maturity      SCr        |C| day
    TSUM3    Temperature sum form maturity to death         SCr        |C| day
    IDSL     Switch for phenological development options    SCr        -
             temperature only (IDSL=0), including           SCr
             daylength (IDSL=1) and including               
             vernalization (IDSL>=2)
    DLO      Optimal daylength for phenological             SCr        hr
             development
    DLC      Critical daylength for phenological            SCr        hr
             development
    DVSI     Initial development stage at emergence.        SCr        -
             Usually this is zero, but it can be higher
             for crops that are transplanted (e.g. paddy
             rice)
    DVSEND   Final development stage                        SCr        -
    DTSMTB   Daily increase in temperature sum as a         TCr        |C|
             function of daily mean temperature.
    DTBEM    Days at TBASEM required for crop to start      TCr        |C|
    =======  ============================================= =======  ============

    **State variables**

    =======  ================================================= ==== ============
     Name     Description                                      Pbl      Unit
    =======  ================================================= ==== ============
    DVS      Development stage                                  Y    - 
    TSUM     Temperature sum                                    N    |C| day
    TSUME    Temperature sum for emergence                      N    |C| day
    DOS      Day of sowing                                      N    - 
    DOE      Day of emergence                                   N    - 
    DOA      Day of Anthesis                                    N    - 
    DOM      Day of maturity                                    N    - 
    DOH      Day of harvest                                     N    -
    STAGE    Current phenological stage, can take the           N    -
             folowing values:
             `emerging|vegetative|reproductive|mature`
    DATBE    Days above Temperature sum for emergence           N    days
    =======  ================================================= ==== ============

    **Rate variables**

    =======  ================================================= ==== ============
     Name     Description                                      Pbl      Unit
    =======  ================================================= ==== ============
    DTSUME   Increase in temperature sum for emergence          N    |C|
    DTSUM    Increase in temperature sum for anthesis or        N    |C|
             maturity
    DVR      Development rate                                   Y    |day-1|
    RDEM     Day counter for if day is suitable for germination Y    day
    =======  ================================================= ==== ============
    
    **External dependencies:**

    None    

    **Signals sent or handled**
    
    `DVS_Phenology` sends the `crop_finish` signal when maturity is
    reached and the `end_type` is 'maturity'.
    
    """

    _DAY_LENGTH = Float(12.0) # Helper variable for daylength
    _CU_FLAG    = Bool(False) # Helper flag for if chilling units should be accumulated
    _STAGE_VAL = Dict({"ecodorm":0, "budbreak":1, "flowering":2, "verasion":3, "ripe":4, "endodorm":5})
    _HC_YESTERDAY = Float(-99.) # Helper variable for yesterday's HC

    class Parameters(ParamTemplate):
        CROP_START_TYPE = Enum(["predorm", "endodorm", "ecodorm"])
        CROP_END_TYPE = Enum(["endodorm", "ecodorm", "budbreak", "verasion", "ripe", "max_duration"])

        DVSI   = Float(-99.)  # Initial development stage
        DVSM   = Float(-99.)  # Mature development stage
        DVSEND = Float(-99.)  # Final development stage
        TBASEM = Float(-99.)  # Base temp. for bud break
        TEFFMX = Float(-99.)  # Max eff temperature for grow daily units
        TSUMEM = Float(-99.)  # Temp. sum for bud break

        TSUM1  = Float(-99.)  # Temperature sum budbreak to flowering
        TSUM2  = Float(-99.)  # Temperature sum flowering to verasion
        TSUM3  = Float(-99.)  # Temperature sum from verasion to ripe
        TSUM4 = Float(-99.)  # Temperature sum from ripe onwards
        MLDORM = Float(-99.)  # Daylength at which a plant will go into dormancy
        Q10C   = Float(-99.)  # Parameter for chilling unit accumulation
        CSUMDB   = Float(-99.)  # Chilling unit sum for dormancy break

        # Cold Hardiness parameters
        HCINIT     = Float(-99.) # Initial Cold Hardiness
        HCMIN      = Float(-99.) # Minimum cold hardiness (negative)
        HCMAX      = Float(-99.) # Maximum cold hardiness (negative)
        TENDO      = Float(-99.) # Endodorm temp
        TECO       = Float(-99.) # Ecodorm temp
        ENACCLIM   = Float(-99.) # Endo rate of acclimation
        ECACCLIM   = Float(-99.) # Eco rate of acclimation
        ENDEACCLIM = Float(-99.) # Endo rate of deacclimation
        ECDEACCLIM = Float(-99.) # Eco rate of deacclimation
        THETA      = Float(-99.) # Theta param for acclimation
        
        """Unused parameters for grapevines. Kept for compatability purposes"""
        DLO    = Float(-99.)  # Optimal day length for phenol. development
        DLC    = Float(-99.)  # Critical day length for phenol. development
        
        
        DTBEM  = Int(-99)     # Number of days above emergence temp required for germination
        IDSL   = Float(-99.)  # Switch for photoperiod (1) and vernalisation (2)
        DTSMTB = AfgenTrait() # Temperature response function for phenol.
                              # development.
        DORM   = Int(-99)     # Days after no growth at which crop transitions to dormancy
        DORMCD = Int(-99)     # Minimum days in dormancy
        AGEI   = Int(-99)     # Initial Tree age
        DCYCLEMAX = Int(-99)   # Maximum number of days in crop cycle before dormancy
        

    class RateVariables(RatesTemplate):
        DTSUME = Float(-99.)  # increase in temperature sum for emergence
        DTSUM  = Float(-99.)  # increase in temperature sum
        DVR    = Float(-99.)  # development rate
        RDEM   = Int(-99.)    # Days above temp sum
        DCU    = Float(-99.)  # Daily chilling units

        # Cold hardiness rates
        DHR    = Float(-99.) # Daily heating rate
        DCR    = Float(-99.) # Daily chilling rate
        DACC   = Float(-99.) # Deacclimation rate
        ACC    = Float(-99.) # Acclimation rate
        HCR    = Float(-99.) # Change in acclimation

    class StateVariables(StatesTemplate):
        PHENOLOGY = Int(-.99) # Int of Stage
        DVS    = Float(-99.)  # Development stage
        TSUM   = Float(-99.)  # Temperature sum state
        CSUM   = Float(-99.) # Chilling sum state
        # Based on the Elkhorn-Lorenz Grape Phenology Stage
        STAGE  = Enum(["endodorm", "ecodorm", "budbreak", "flowering", "verasion", "ripe"])
        DOP    = Instance(datetime.date) # Day of planting
        AGE    = Int(-99) # Age of crop (years)

        # Cold hardiness states 
        DHSUM = Float(-99.) # Daily heating sum
        DCSUM = Float(-99.) # Daily chilling sum
        HC     = Float(-99.) # Cold hardiness
        PREDBB = Float(-99.) # Predicted bud break
        LTE50  = Float(-99.) # Predicted LTE50 for cold hardiness
        
        """Ununsed, kept for compatibility purposes"""
        TSUME  = Float(-99.)  # Temperature sum for emergence state
        DCYCLE = Int(-99) # Days in Crop cycle
        DSD    = Int(-99) # Days since dormancy
        DATBE  = Int(-99)  # Current number of days above TSUMEM
        DSNG   = Int(-99) # Days since no growth
        DOB    = Instance(datetime.date) # Day of bud break
        DOL    = Instance(datetime.date) # Day of Flowering
        DOV    = Instance(datetime.date) # Day of Verasion
        DOR    = Instance(datetime.date) # Day of Ripe
        DON    = Instance(datetime.date) # Day of Endodormancy
        DOC    = Instance(datetime.date) # Day of Ecodormancy
       
    def initialize(self, day:datetime.date, kiosk:VariableKiosk, parvalues:dict):
        """
        :param day: start date of the simulation
        :param kiosk: variable kiosk of this PCSE  instance
        :param parvalues: `ParameterProvider` object providing parameters as
                key/value pairs
        """

        self.params = self.Parameters(parvalues)
        self.kiosk = kiosk
        p = self.params

        self._connect_signal(self._on_CROP_FINISH, signal=signals.crop_finish)
        self._connect_signal(self._on_DORMANT, signal=signals.crop_dormant)
        AGEI = self.params.AGEI
        # Define initial states
        DVS, DOP, STAGE = self._get_initial_stage(day)
        self.states = self.StateVariables(kiosk, 
                                          publish=["DVS", "TSUM", "TSUME", 
                                                   "STAGE", "DSNG", "DSD", "AGE",
                                                   "DCYCLE", "DATBE", "DOP", "DOB",
                                                   "DOL", "DOV", "DOR", "DOC", "DON", 
                                                   "PHENOLOGY", "DHSUM", "DCSUM", "HC", 
                                                   "PREDBB", "LTE50"],
                                          TSUM=0., TSUME=0., DVS=DVS, STAGE=STAGE, DSNG=0,
                                          DSD=0, AGE=AGEI, DCYCLE=0,DATBE=0, DOP=DOP, CSUM=0.,
                                          DOB=None, DOL=None, DOV=None, DOR=None, DOC=None,
                                          DON=None, PHENOLOGY=self._STAGE_VAL[STAGE],
                                          DHSUM=0., DCSUM=0.,HC=p.HCINIT,
                                          PREDBB=0., LTE50=p.HCINIT)
        
        self.rates = self.RateVariables(kiosk, publish=["DTSUME", "DTSUM", "DVR", 
                                                        "DHR", "DCR", "DACC", "ACC", "HCR"])

        # initialize vernalisation for IDSL=2
        if self.params.IDSL >= 2:
            self.vernalisation = Vernalisation(day, kiosk, parvalues)
  
    def _get_initial_stage(self, day:datetime.date):
        """Set the initial state of the crop given the start type
        """
        p = self.params

        # Define initial stage type (emergence/sowing) and fill the
        # respective day of sowing/emergence (DOS/DOE)
        if p.CROP_START_TYPE == "predorm":
            STAGE = "endodorm"
            DVS = p.DVSI
            DOP = day
        elif p.CROP_START_TYPE == "endodorm":
            STAGE = "ecodorm"
            DOP = day
            DVS = -0.1
        elif p.CROP_START_TYPE == "ecodorm":
            STAGE = "budbreak"
            DVS = p.DVSI
            DOP = day
        else:
            msg = "Unknown start type: %s. Are you using the corect Phenology \
                module (Calling the correct Gym Environment)?" % p.CROP_START_TYPE
            raise Exception(msg) 
        return DVS, DOP, STAGE

    @prepare_rates
    def calc_rates(self, day, drv):
        """
        Calculates the rates for phenological development
        """
        p = self.params
        r = self.rates
        s = self.states

        # Day length sensitivity
        self._DAY_LENGTH = daylength(day, drv.LAT)

        r.DTSUME = 0.
        r.DTSUM = 0.
        r.DVR = 0.
        r.DCU = 0.
        r.DHR = 0.
        r.DCR = 0.
        r.DACC = 0.
        r.ACC = 0.
        r.HCR = 0.
        # Development rates
        if day.day == 1 and day.month == 8:
            self._CU_FLAG = True

        if s.STAGE == "endodorm":
            if self._CU_FLAG:
                r.DCU = p.Q10C**(-drv.TMAX/10) + p.Q10C**(-drv.TMIN/10)
            r.DTSUM =  max(0., daily_temp_units(drv, p.TBASEM, p.TEFFMX))
            r.DVR = r.DTSUM/(p.TSUM4)
            r.DHR = max(0., drv.TEMP-p.TENDO)
            r.DCR = min(0., drv.TEMP-p.TENDO)
            if s.DCSUM != 0:
                r.DACC = r.DHR * p.ENDEACCLIM * (1 - ((self._HC_YESTERDAY-p.HCMAX) / (p.HCMIN-p.HCMAX)))
            else:
                r.DACC = 0
            r.ACC = r.DCR * p.ENACCLIM * (1-((p.HCMIN - self._HC_YESTERDAY)) / ((p.HCMIN-p.HCMAX)))
            r.HCR = r.DACC + r.ACC
        elif s.STAGE == "ecodorm":
            r.DTSUME = max(0., daily_temp_units(drv, p.TBASEM, p.TEFFMX))
            r.DVR = 0.1 * r.DTSUME/p.TSUMEM
            r.DHR = max(0., drv.TEMP-p.TECO)
            r.DCR = min(0., drv.TEMP-p.TECO)
            if s.DCSUM != 0:
                r.DACC = r.DHR * p.ECDEACCLIM * (1 - ((self._HC_YESTERDAY-p.HCMAX) / (p.HCMIN-p.HCMAX)) ** p.THETA)
            else:
                r.DACC = 0
            r.ACC = r.DCR * p.ECACCLIM * (1-((p.HCMIN - self._HC_YESTERDAY)) / ((p.HCMIN-p.HCMAX)))
            r.HCR = r.DACC + r.ACC
        elif s.STAGE == "budbreak":
            r.DTSUM = max(0., daily_temp_units(drv, p.TBASEM, p.TEFFMX))
            r.DVR = r.DTSUM/(p.TSUM1)
            if self._CU_FLAG:
                r.DCU = p.Q10C**(-drv.TMAX/10) + p.Q10C**(-drv.TMIN/10)
        elif s.STAGE == "flowering":
            r.DTSUM =  max(0., daily_temp_units(drv, p.TBASEM, p.TEFFMX))
            r.DVR = r.DTSUM/(p.TSUM2)
            if self._CU_FLAG:
                r.DCU = p.Q10C**(-drv.TMAX/10) + p.Q10C**(-drv.TMIN/10)
        elif s.STAGE == "verasion":
            r.DTSUM =  max(0., daily_temp_units(drv, p.TBASEM, p.TEFFMX))
            r.DVR = r.DTSUM/(p.TSUM3)
            if self._CU_FLAG:
                r.DCU = p.Q10C**(-drv.TMAX/10) + p.Q10C**(-drv.TMIN/10)
        elif s.STAGE == "ripe":
            r.DTSUM = 0.
            r.DVR = 0.
            if self._CU_FLAG:
                r.DCU = p.Q10C**(-drv.TMAX/10) + p.Q10C**(-drv.TMIN/10)
            r.DTSUM =  max(0., daily_temp_units(drv, p.TBASEM, p.TEFFMX))
            r.DVR = r.DTSUM/(p.TSUM4)
        else:  # Problem: no stage defined
            msg = "Unrecognized STAGE defined in phenology submodule: %s."
            raise Exception(msg, self.states.STAGE)

    @prepare_states
    def integrate(self, day, delt=1.0):
        """
        Updates the state variable and checks for phenologic stages
        """

        p = self.params
        r = self.rates
        s = self.states

        # Increment plant age based on Day of Planting
        # Handles leap years
        if s.DOP.day == day.day and s.DOP.month == day.month:
            s.AGE += 1 
        else:
            s.AGE += 0

        # Integrate phenologic states
        s.TSUME += r.DTSUME
        s.DVS += r.DVR
        s.TSUM += r.DTSUM
        s.CSUM += r.DCU
        s.PHENOLOGY = self._STAGE_VAL[s.STAGE]
        self._HC_YESTERDAY = s.HC
        s.HC = limit(p.HCMAX, p.HCMIN, s.HC+r.HCR)
        s.DCSUM += r.DCR
        s.LTE50 = round(s.HC, 2)

        # Check if a new stage is reached
        if s.STAGE == "endodorm":
            if s.CSUM >= p.CSUMDB:
                self._next_stage(day)
                s.DVS = -0.1
                s.CSUM = 0
            # Use HCMIN to determine if vinifera or labrusca
            if p.HCMIN == -1.2:    # Assume vinifera with budbreak at -2.2
                if self._HC_YESTERDAY < -2.2:
                    if s.HC >= -2.2:
                        s.PREDBB = round(s.HC, 2)
            if p.HCMIN == -2.5:    # Assume labrusca with budbreak at -6.4
                if self._HC_YESTERDAY < -6.4:
                    if s.HC >= -6.4:
                        s.PREDBB = round(s.HC, 2)

        elif s.STAGE == "ecodorm":
            s.DHSUM += r.DHR
            if s.TSUME >= p.TSUMEM:
                self._next_stage(day)
                s.DVS = 0.
                s.DHSUM = 0
                s.DCSUM = 0
                s.PREDBB = 0
            # Use HCMIN to determine if vinifera or labrusca
            if p.HCMIN == -1.2:    # Assume vinifera with budbreak at -2.2
                if self._HC_YESTERDAY < -2.2:
                    if s.HC >= -2.2:
                        s.PREDBB = round(s.HC, 2)
            if p.HCMIN == -2.5:    # Assume labrusca with budbreak at -6.4
                if self._HC_YESTERDAY < -6.4:
                    if s.HC >= -6.4:
                        s.PREDBB = round(s.HC, 2)
        elif s.STAGE == "budbreak":
            if s.DVS >= 1.0:
                self._next_stage(day)
                s.DVS = 1.0
        elif s.STAGE == "flowering":
            if s.DVS >= p.DVSM:
                self._next_stage(day)
                s.DVS = p.DVSM
        elif s.STAGE == "verasion":
            if s.DVS >= p.DVSEND:
                self._next_stage(day)
                s.DVS = p.DVSEND
            if self._DAY_LENGTH <= p.MLDORM:
                s.STAGE = "endodorm"
                s.PHENOLOGY = self._STAGE_VAL[s.STAGE]
                s.DOC = day
        elif s.STAGE == "ripe":
            if self._DAY_LENGTH <= p.MLDORM:
                s.STAGE = "endodorm"
                s.PHENOLOGY = self._STAGE_VAL[s.STAGE]
                s.DOC = day
        else:  # Problem: no stage defined
            msg = "Unrecognized STAGE defined in phenology submodule: %s."
            raise Exception(msg, self.states.STAGE)

    def _next_stage(self, day):
        """Moves states.STAGE to the next phenological stage"""
        s = self.states
        p = self.params

        if s.STAGE == "endodorm":
            s.STAGE = "ecodorm"
            s.DON = day
            self._on_DORMANT(day)
            self._CU_FLAG = False
        
        elif s.STAGE == "ecodorm":
            s.STAGE = "budbreak"
            s.PHENOLOGY = self._STAGE_VAL[s.STAGE]
            s.DOB = day
                
        elif s.STAGE == "budbreak":
            s.STAGE = "flowering"
            s.PHENOLOGY = self._STAGE_VAL[s.STAGE]
            s.DOL = day

        elif s.STAGE == "flowering":
            s.STAGE = "verasion"
            s.PHENOLOGY = self._STAGE_VAL[s.STAGE]
            s.DOV = day
            
        elif s.STAGE == "verasion":
            s.STAGE = "ripe"
            s.PHENOLOGY = self._STAGE_VAL[s.STAGE]
            s.DOR = day
            
        elif s.STAGE == "ripe":
            msg = "Cannot move to next phenology stage: maturity already reached!"
            raise Exception(msg)

        else: # Problem no stage defined
            msg = "No STAGE defined in phenology submodule."
            raise Exception(msg)
        
        msg = "Changed phenological stage '%s' to '%s' on %s"

    def _on_CROP_HARVEST(self, day):
        if self.params.CROP_END_TYPE in ["harvest"]:
            self._send_signal(signal=signals.crop_finish,day=day,finish_type="harvest",
                              crop_delete=True)

    def _on_CROP_FINISH(self, day, finish_type=None):
        """Handler for setting day of harvest (DOH). Although DOH is not
        strictly related to phenology (but to management) this is the most
        logical place to put it.
        """
        if finish_type in ['harvest']:
            self._for_finalize["DOH"] = day

    def _on_DORMANT(self, day:datetime.date):
        """Handler for dormant signal. Reset all nonessential states and rates to 0
        """
        if self.params.IDSL >= 2:
            self.vernalisation.reset()
        
        s = self.states
        r = self.rates

        s.TSUM  = 0
        s.TSUME = 0

        r.DTSUME = 0 
        r.DTSUM  = 0
        r.DVR    = 0

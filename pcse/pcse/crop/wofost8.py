"""Main crop class for handling growth of the crop. Includes the base crop model
and WOFOST8 model for annual crop growth

Written by: Allard de Wit (allard.dewit@wur.nl), April 2014
Modified by Will Solow, 2024
"""

from datetime import date

from ..nasapower import WeatherDataProvider
from ..utils.traitlets import Float, Instance, Unicode, Bool
from ..utils.decorators import prepare_rates, prepare_states
from ..base import ParamTemplate, StatesTemplate, RatesTemplate, \
     SimulationObject, VariableKiosk
from .. import signals
from ..util import Afgen, AfgenTrait
from .. import exceptions as exc
from .phenology import Annual_Phenology, Perennial_Phenology, Grape_Phenology
from .respiration import WOFOST_Maintenance_Respiration as MaintenanceRespiration
from .respiration import Perennial_WOFOST_Maintenance_Respiration as Perennial_MaintenanceRespiration
from .stem_dynamics import Annual_WOFOST_Stem_Dynamics as Annual_Stem_Dynamics
from .root_dynamics import Annual_WOFOST_Root_Dynamics as Annual_Root_Dynamics
from .leaf_dynamics import Annual_WOFOST_Leaf_Dynamics_NPK as Annual_Leaf_Dynamics
from .stem_dynamics import Perennial_WOFOST_Stem_Dynamics as Perennial_Stem_Dynamics
from .root_dynamics import Perennial_WOFOST_Root_Dynamics as Perennial_Root_Dynamics
from .leaf_dynamics import Perennial_WOFOST_Leaf_Dynamics_NPK as Perennial_Leaf_Dynamics
from .storage_organ_dynamics import Annual_WOFOST_Storage_Organ_Dynamics as \
    Annual_Storage_Organ_Dynamics
from .storage_organ_dynamics import Perennial_WOFOST_Storage_Organ_Dynamics as \
    Perennial_Storage_Organ_Dynamics
from .assimilation import WOFOST_Assimilation as Assimilation
from .partitioning import Annual_Partitioning_NPK as Annual_Partitioning
from .partitioning import Perennial_Partitioning_NPK as Perennial_Partitioning
from .evapotranspiration import EvapotranspirationCO2 as Evapotranspiration

from .npk_dynamics import NPK_Crop_Dynamics as NPK_crop
from .nutrients.npk_stress import NPK_Stress as NPK_Stress

class BaseCropModel(SimulationObject):
    """Top level object organizing the different components of the WOFOST crop
    simulation including the implementation of N/P/K dynamics.
            
    The CropSimulation object organizes the different processes of the crop
    simulation. Moreover, it contains the parameters, rate and state variables
    which are relevant at the level of the entire crop. The processes that are
    implemented as embedded simulation objects consist of:
    
        1. Phenology (self.pheno)
        2. Partitioning (self.part)
        3. Assimilation (self.assim)
        4. Maintenance respiration (self.mres)
        5. Evapotranspiration (self.evtra)
        6. Leaf dynamics (self.lv_dynamics)
        7. Stem dynamics (self.st_dynamics)
        8. Root dynamics (self.ro_dynamics)
        9. Storage organ dynamics (self.so_dynamics)
        10. N/P/K crop dynamics (self.npk_crop_dynamics)
        12. N/P/K stress (self.npk_stress)

        **Simulation parameters:**
    
    ======== =============================================== =======  ==========
     Name     Description                                     Type     Unit
    ======== =============================================== =======  ==========
    CVL      Conversion factor for assimilates to leaves       SCr     -
    CVO      Conversion factor for assimilates to storage      SCr     -
             organs.
    CVR      Conversion factor for assimilates to roots        SCr     -
    CVS      Conversion factor for assimilates to stems        SCr     -
    ======== =============================================== =======  ==========
    
    
    **State variables:**

    ============  ================================================= ==== ===============
     Name          Description                                      Pbl      Unit
    ============  ================================================= ==== ===============
    TAGP          Total above-ground Production                      N    |kg ha-1|
    GASST         Total gross assimilation                           N    |kg CH2O ha-1|
    MREST         Total gross maintenance respiration                N    |kg CH2O ha-1|
    CTRAT         Total crop transpiration accumulated over the
                  crop cycle                                         N    cm
    CEVST         Total soil evaporation accumulated over the
                  crop cycle                                         N    cm
    HI            Harvest Index (only calculated during              N    -
                  `finalize()`)
    DOF           Date representing the day of finish of the crop    N    -
                  simulation.
    FINISH_TYPE   String representing the reason for finishing the   N    -
                  simulation: maturity, harvest, leave death, etc.
    FIN           Boolean value for if the crop has finished         Y    - 
    ============  ================================================= ==== ===============

 
     **Rate variables:**

    =======  ================================================ ==== =============
     Name     Description                                      Pbl      Unit
    =======  ================================================ ==== =============
    GASS     Assimilation rate corrected for water stress       N  |kg CH2O ha-1 d-1|
    PGASS    Potential assimilation rate                        N  |kg CH2O ha-1 d-1|
    MRES     Actual maintenance respiration rate, taking into
             account that MRES <= GASS.                         N  |kg CH2O ha-1 d-1|
    PMRES    Potential maintenance respiration rate             N  |kg CH2O ha-1 d-1|
    ASRC     Net available assimilates (GASS - MRES)            N  |kg CH2O ha-1 d-1|
    DMI      Total dry matter increase, calculated as ASRC
             times a weighted conversion efficieny.             Y  |kg ha-1 d-1|
    ADMI     Aboveground dry matter increase                    Y  |kg ha-1 d-1|
    =======  ================================================ ==== =============

    """

    # Parameters, rates and states which are relevant at the main crop
    # simulation level
    class Parameters(ParamTemplate):
        CVL = Float(-99.)
        CVO = Float(-99.)
        CVR = Float(-99.)
        CVS = Float(-99.)

    class StateVariables(StatesTemplate):
        TAGP = Float(-99.)
        GASST = Float(-99.)
        MREST = Float(-99.)
        CTRAT = Float(-99.) # Crop total transpiration
        CEVST = Float(-99.)
        HI = Float(-99.)
        DOF = Instance(date)
        FINISH_TYPE = Unicode("")
        FIN = Bool(False)

    class RateVariables(RatesTemplate):
        GASS = Float(-99.)
        PGASS = Float(-99.)
        MRES = Float(-99.)
        ASRC = Float(-99.)
        DMI = Float(-99.)
        ADMI = Float(-99.)

    # sub-model components for crop simulation
    pheno = Instance(SimulationObject)
    part = Instance(SimulationObject)
    assim = Instance(SimulationObject)
    mres = Instance(SimulationObject)
    evtra = Instance(SimulationObject)
    lv_dynamics = Instance(SimulationObject)
    st_dynamics = Instance(SimulationObject)
    ro_dynamics = Instance(SimulationObject)
    so_dynamics = Instance(SimulationObject)
    npk_crop_dynamics = Instance(SimulationObject)
    npk_stress = Instance(SimulationObject)

    def initialize(self, day:date, kiosk:VariableKiosk, parvalues:dict):
        msg = "`initialize` method not yet implemented on %s" % self.__class__.__name__
        raise NotImplementedError(msg)
    
    @staticmethod
    def _check_carbon_balance(day, DMI:float, GASS:float, MRES:float, CVF:float, pf:float):
        """Checks that the carbon balance is valid after integration
        """
        (FR, FL, FS, FO) = pf
        checksum = (GASS - MRES - (FR+(FL+FS+FO)*(1.-FR)) * DMI/CVF) * \
                    1./(max(0.0001,GASS))
        if abs(checksum) >= 0.0001:
            msg = "Carbon flows not balanced on day %s\n" % day
            msg += "Checksum: %f, GASS: %f, MRES: %f\n" % (checksum, GASS, MRES)
            msg += "FR,L,S,O: %5.3f,%5.3f,%5.3f,%5.3f, DMI: %f, CVF: %f\n" % \
                   (FR,FL,FS,FO,DMI,CVF)
            #raise exc.CarbonBalanceError(msg)

    @prepare_rates
    def calc_rates(self, day:date, drv:WeatherDataProvider):
        """Calculate state rates for integration 
        """
        params = self.params
        rates  = self.rates
        k = self.kiosk

        # Phenology
        self.pheno.calc_rates(day, drv)
        crop_stage = self.pheno.get_variable("STAGE")

        # if before emergence there is no need to continue
        # because only the phenology is running.
        if crop_stage == "emerging":
            return

        # Potential assimilation
        rates.PGASS = self.assim(day, drv)
        
        # (evapo)transpiration rates
        self.evtra(day, drv)

        # nutrient status and reduction factor
        NNI, NPKI, RFNPK = self.npk_stress(day, drv)

        # Select minimum of nutrient and water/oxygen stress
        reduction = min(RFNPK, k.RFTRA)

        rates.GASS = rates.PGASS * reduction

        # Respiration
        PMRES = self.mres(day, drv)
        rates.MRES = min(rates.GASS, PMRES)

        # Net available assimilates
        rates.ASRC = rates.GASS - rates.MRES

        # DM partitioning factors (pf), conversion factor (CVF),
        # dry matter increase (DMI) and check on carbon balance
        pf = self.part.calc_rates(day, drv)
        CVF = 1./((pf.FL/params.CVL + pf.FS/params.CVS + pf.FO/params.CVO) *
                  (1.-pf.FR) + pf.FR/params.CVR)
        rates.DMI = CVF * rates.ASRC
        self._check_carbon_balance(day, rates.DMI, rates.GASS, rates.MRES,
                                   CVF, pf)

        # distribution over plant organ
        # Below-ground dry matter increase and root dynamics
        self.ro_dynamics.calc_rates(day, drv)
        # Aboveground dry matter increase and distribution over stems,
        # leaves, organs
        rates.ADMI = (1. - pf.FR) * rates.DMI
        self.st_dynamics.calc_rates(day, drv)
        self.so_dynamics.calc_rates(day, drv)
        self.lv_dynamics.calc_rates(day, drv)
        
        # Update nutrient rates in crop and soil
        self.npk_crop_dynamics.calc_rates(day, drv)

    @prepare_states
    def integrate(self, day:date, delt:float=1.0):
        """Integrate state rates
        """
        rates = self.rates
        states = self.states

        # crop stage before integration
        crop_stage = self.pheno.get_variable("STAGE")

        # Phenology
        self.pheno.integrate(day, delt)

        # if before emergence there is no need to continue
        # because only the phenology is running.
        # Just run a touch() to to ensure that all state variables are available
        # in the kiosk
        if crop_stage == "emerging":
            self.touch()
            return

        # Partitioning
        self.part.integrate(day, delt)
        
        # Integrate states on leaves, storage organs, stems and roots
        self.ro_dynamics.integrate(day, delt)
        self.so_dynamics.integrate(day, delt)
        self.st_dynamics.integrate(day, delt)
        self.lv_dynamics.integrate(day, delt)

        # Update nutrient states in crop and soil
        self.npk_crop_dynamics.integrate(day, delt)

        # Integrate total (living+dead) above-ground biomass of the crop
        states.TAGP = self.kiosk.TWLV + \
                      self.kiosk.TWST + \
                      self.kiosk.TWSO

        # total gross assimilation and maintenance respiration 
        states.GASST += rates.GASS
        states.MREST += rates.MRES
        
        # total crop transpiration and soil evaporation
        states.CTRAT += self.kiosk.TRA
        EVS = self.kiosk.EVS if "EVS" in self.kiosk else self.kiosk.MEVS
        states.CEVST += EVS

    @prepare_states
    def finalize(self, day:date):
        """Finalize crop parameters and output at the end of the simulation
        """
        # Calculate Harvest Index
        if self.states.TAGP > 0:
            self.states.HI = self.kiosk.TWSO/self.states.TAGP
        else:
            msg = "Cannot calculate Harvest Index because TAGP=0"
            self.logger.warning(msg)
            self.states.HI = -1.
        
        SimulationObject.finalize(self, day)

    def _on_CROP_FINISH(self, day, finish_type=None):
        """Handler for setting day of finish (DOF) and reason for
        crop finishing (FINISH).
        """
        self.states.FIN = True
        self._for_finalize["DOF"] = day
        self._for_finalize["FINISH_TYPE"] = finish_type

class Wofost80(BaseCropModel):
    
    """Top level object organizing the different components of the WOFOST crop
    simulation including the implementation of N/P/K dynamics.
    """

    def initialize(self, day:date, kiosk:VariableKiosk, parvalues:dict):
        """
        :param day: start date of the simulation
        :param kiosk: variable kiosk of this PCSE model instance
        :param parvalues: dictionary with parameter key/value pairs
        """
        
        self.params = self.Parameters(parvalues)
        self.kiosk = kiosk
        
        # Initialize components of the crop
        self.pheno = Annual_Phenology(day, kiosk,  parvalues)
        self.part = Annual_Partitioning(day, kiosk, parvalues)
        self.assim = Assimilation(day, kiosk, parvalues)
        self.mres = MaintenanceRespiration(day, kiosk, parvalues)
        self.evtra = Evapotranspiration(day, kiosk, parvalues)
        self.ro_dynamics = Annual_Root_Dynamics(day, kiosk, parvalues)
        self.st_dynamics = Annual_Stem_Dynamics(day, kiosk, parvalues)
        self.so_dynamics = Annual_Storage_Organ_Dynamics(day, kiosk, parvalues)
        self.lv_dynamics = Annual_Leaf_Dynamics(day, kiosk, parvalues)
        # Added for book keeping of N/P/K in crop and soil
        self.npk_crop_dynamics = NPK_crop(day, kiosk, parvalues)
        self.npk_stress = NPK_Stress(day, kiosk, parvalues)
        

        # Initial total (living+dead) above-ground biomass of the crop
        TAGP = self.kiosk.TWLV + self.kiosk.TWST + self.kiosk.TWSO

        self.states = self.StateVariables(kiosk,
                publish=["TAGP", "GASST", "MREST", "CTRAT", "CEVST", "HI", 
                         "DOF", "FINISH_TYPE", "FIN",],
                TAGP=TAGP, GASST=0.0, MREST=0.0, CTRAT=0.0, HI=0.0, CEVST=0.0,
                DOF=None, FINISH_TYPE=None, FIN=False)
        
        self.rates = self.RateVariables(kiosk, 
                    publish=["GASS", "PGASS", "MRES", "ASRC", "DMI", "ADMI"])

        # Check partitioning of TDWI over plant organs
        checksum = parvalues["TDWI"] - self.states.TAGP - self.kiosk.TWRT
        if abs(checksum) > 0.0001:
            msg = "Error in partitioning of initial biomass (TDWI)!"
            raise exc.PartitioningError(msg)
            
        # assign handler for CROP_FINISH signal
        self._connect_signal(self._on_CROP_FINISH, signal=signals.crop_finish)

class Wofost80Perennial(BaseCropModel):
    
    """Top level object organizing the different components of the WOFOST crop
    simulation including the implementation of N/P/K dynamics.
            
    """
    parvalues: dict

    # Parameters, rates and states which are relevant at the main crop
    # simulation level
    class Parameters(ParamTemplate):
        CVL = AfgenTrait()
        CVO = AfgenTrait()
        CVR = AfgenTrait()
        CVS = AfgenTrait()

    def initialize(self, day:date, kiosk:VariableKiosk, parvalues:dict):
        """
        :param day: start date of the simulation
        :param kiosk: variable kiosk of this PCSE model instance
        :param parvalues: dictionary with parameter key/value pairs
        """
        self.params = self.Parameters(parvalues)
        self.kiosk = kiosk
        self._par_values = parvalues
        
        # Initialize components of the crop
        self.pheno = Perennial_Phenology(day, kiosk,  parvalues)
        self.part = Perennial_Partitioning(day, kiosk, parvalues)
        self.assim = Assimilation(day, kiosk, parvalues)
        self.mres = Perennial_MaintenanceRespiration(day, kiosk, parvalues)
        self.evtra = Evapotranspiration(day, kiosk, parvalues)
        self.ro_dynamics = Perennial_Root_Dynamics(day, kiosk, parvalues)
        self.st_dynamics = Perennial_Stem_Dynamics(day, kiosk, parvalues)
        self.so_dynamics = Perennial_Storage_Organ_Dynamics(day, kiosk, parvalues)
        self.lv_dynamics = Perennial_Leaf_Dynamics(day, kiosk, parvalues)
        # Added for book keeping of N/P/K in crop and soil
        self.npk_crop_dynamics = NPK_crop(day, kiosk, parvalues)
        self.npk_stress = NPK_Stress(day, kiosk, parvalues)
        

        # Initial total (living+dead) above-ground biomass of the crop
        TAGP = self.kiosk.TWLV + self.kiosk.TWST + self.kiosk.TWSO
        self.states = self.StateVariables(kiosk,
                publish=["TAGP", "GASST", "MREST", "CTRAT", "CEVST", "HI", 
                         "DOF", "FINISH_TYPE", "FIN",],
                TAGP=TAGP, GASST=0.0, MREST=0.0, CTRAT=0.0, HI=0.0, CEVST=0.0,
                DOF=None, FINISH_TYPE=None, FIN=False)
        
        self.rates = self.RateVariables(kiosk, 
                    publish=["GASS", "PGASS", "MRES", "ASRC", "DMI", "ADMI"])

        AGE = self.kiosk["AGE"]
        # Check partitioning of TDWI over plant organs
        checksum = Afgen(self._par_values["TDWI"])(AGE) - self.states.TAGP - self.kiosk.TWRT
        if abs(checksum) > 0.0001:
            msg = "Error in partitioning of initial biomass (TDWI)!"
            #raise exc.PartitioningError(msg)
            
        # assign handler for CROP_FINISH signal
        self._connect_signal(self._on_CROP_FINISH, signal=signals.crop_finish)
        self._connect_signal(self._on_DORMANT, signal=signals.crop_dormant)

    @prepare_rates
    def calc_rates(self, day:date, drv:WeatherDataProvider):
        """Calculate state rates for integration 
        """
        params = self.params
        rates  = self.rates
        k = self.kiosk

        # Phenology
        crop_stage = self.pheno.get_variable("STAGE")
        self.pheno.calc_rates(day, drv)
    
        # if before emergence there is no need to continue
        # because only the phenology is running.
        if crop_stage == "emerging" or crop_stage == "dormant":
            return

        # Potential assimilation
        rates.PGASS = self.assim(day, drv)
        
        # (evapo)transpiration rates
        self.evtra(day, drv)

        # nutrient status and reduction factor
        NNI, NPKI, RFNPK = self.npk_stress(day, drv)

        # Select minimum of nutrient and water/oxygen stress
        reduction = min(RFNPK, k.RFTRA)

        rates.GASS = rates.PGASS * reduction

        # Respiration
        PMRES = self.mres(day, drv)
        rates.MRES = min(rates.GASS, PMRES)

        # Net available assimilates
        rates.ASRC = rates.GASS - rates.MRES

        # DM partitioning factors (pf), conversion factor (CVF),
        # dry matter increase (DMI) and check on carbon balance
        pf = self.part.calc_rates(day, drv)
        CVF = 1./((pf.FL/params.CVL(k.AGE) + pf.FS/params.CVS(k.AGE) + pf.FO/params.CVO(k.AGE)) *
                  (1.-pf.FR) + pf.FR/params.CVR(k.AGE))
        rates.DMI = CVF * rates.ASRC
        self._check_carbon_balance(day, rates.DMI, rates.GASS, rates.MRES, CVF, pf)

        # distribution over plant organ
        # Below-ground dry matter increase and root dynamics
        self.ro_dynamics.calc_rates(day, drv)
        # Aboveground dry matter increase and distribution over stems,
        # leaves, organs
        rates.ADMI = (1. - pf.FR) * rates.DMI
        self.st_dynamics.calc_rates(day, drv)
        self.so_dynamics.calc_rates(day, drv)
        self.lv_dynamics.calc_rates(day, drv)
        
        # Update nutrient rates in crop and soil
        self.npk_crop_dynamics.calc_rates(day, drv)

    @prepare_states
    def integrate(self, day:date, delt:float=1.0):
        """Integrate state rates
        """
        rates = self.rates
        states = self.states

        # crop stage before integration
        crop_stage = self.pheno.get_variable("STAGE")
    
        # Phenology
        self.pheno.integrate(day, delt)
        # if before emergence there is no need to continue
        # because only the phenology is running.
        # Just run a touch() to to ensure that all state variables are available
        # in the kiosk
        if crop_stage == "emerging" or crop_stage == "dormant":
            self.touch()
            return

        # Partitioning
        self.part.integrate(day, delt)
        
        # Integrate states on leaves, storage organs, stems and roots
        self.ro_dynamics.integrate(day, delt)
        self.so_dynamics.integrate(day, delt)
        self.st_dynamics.integrate(day, delt)
        self.lv_dynamics.integrate(day, delt)

        # Update nutrient states in crop and soil
        self.npk_crop_dynamics.integrate(day, delt)

        # Integrate total (living+dead) above-ground biomass of the crop
        states.TAGP = self.kiosk.TWLV + \
                      self.kiosk.TWST + \
                      self.kiosk.TWSO

        # total gross assimilation and maintenance respiration 
        states.GASST += rates.GASS
        states.MREST += rates.MRES
        
        # total crop transpiration and soil evaporation
        states.CTRAT += self.kiosk.TRA
        states.CEVST += self.kiosk.EVS

    def _on_DORMANT(self, day:date):
        """Handler for recieving the crop dormancy signal. Upon dormancy, reset
        all crop parameters
        """
        # Deregister parameters from kiosk
        self.part.reset()
        self.assim.reset()
        self.mres.reset()
        self.evtra.reset()
        #self.ro_dynamics.reset()
        self.ro_dynamics.publish_states()
        #self.st_dynamics.reset()
        self.st_dynamics.publish_states()
        self.so_dynamics.reset()
        self.lv_dynamics.reset()
        # Added for book keeping of N/P/K in crop and soil
        self.npk_crop_dynamics.reset()
        self.npk_stress.reset()

        # Manually reset all WOFOST8 crop variables
        s = self.states
        r = self.rates
        
        # Initial total (living+dead) above-ground biomass of the crop
        s.TAGP = self.kiosk.TWLV + self.kiosk.TWST + self.kiosk.TWSO
        s.GASST = s.MREST = s.CTRAT = s.CEVST = s.HI = 0
        s.DOF = s.FINISH_TYPE = None
        s.FIN = False

        r.GASS = r.PGASS = r.MRES = r.ASRC = r.DMI = r.ADMI = 0

        AGE = self.kiosk["AGE"]
        # Check partitioning of TDWI over plant organs
        checksum = Afgen(self._par_values["TDWI"])(AGE) - self.states.TAGP - self.kiosk.TWRT
        if abs(checksum) > 0.0001:
            msg = "Error in partitioning of initial biomass (TDWI)!"
            #raise exc.PartitioningError(msg)
        
        #print(f'Resetting from Dormant: {day}')

class Wofost80Grape(BaseCropModel):
    """Top level object organizing the different components of the WOFOST crop
    simulation including the implementation of N/P/K dynamics.
            
    """
    parvalues: dict

    # Parameters, rates and states which are relevant at the main crop
    # simulation level
    class Parameters(ParamTemplate):
        CVL = AfgenTrait()
        CVO = AfgenTrait()
        CVR = AfgenTrait()
        CVS = AfgenTrait()

    def initialize(self, day:date, kiosk:VariableKiosk, parvalues:dict):
        """
        :param day: start date of the simulation
        :param kiosk: variable kiosk of this PCSE model instance
        :param parvalues: dictionary with parameter key/value pairs
        """
        self.params = self.Parameters(parvalues)
        self.kiosk = kiosk
        self._par_values = parvalues
        
        # Initialize components of the crop
        self.pheno = Grape_Phenology(day, kiosk,  parvalues)
        self.part = Perennial_Partitioning(day, kiosk, parvalues)
        self.assim = Assimilation(day, kiosk, parvalues)
        self.mres = Perennial_MaintenanceRespiration(day, kiosk, parvalues)
        self.evtra = Evapotranspiration(day, kiosk, parvalues)
        self.ro_dynamics = Perennial_Root_Dynamics(day, kiosk, parvalues)
        self.st_dynamics = Perennial_Stem_Dynamics(day, kiosk, parvalues)
        self.so_dynamics = Perennial_Storage_Organ_Dynamics(day, kiosk, parvalues)
        self.lv_dynamics = Perennial_Leaf_Dynamics(day, kiosk, parvalues)
        # Added for book keeping of N/P/K in crop and soil
        self.npk_crop_dynamics = NPK_crop(day, kiosk, parvalues)
        self.npk_stress = NPK_Stress(day, kiosk, parvalues)
        

        # Initial total (living+dead) above-ground biomass of the crop
        TAGP = self.kiosk.TWLV + self.kiosk.TWST + self.kiosk.TWSO
        self.states = self.StateVariables(kiosk,
                publish=["TAGP", "GASST", "MREST", "CTRAT", "CEVST", "HI", 
                         "DOF", "FINISH_TYPE", "FIN",],
                TAGP=TAGP, GASST=0.0, MREST=0.0, CTRAT=0.0, HI=0.0, CEVST=0.0,
                DOF=None, FINISH_TYPE=None, FIN=False)
        
        self.rates = self.RateVariables(kiosk, 
                    publish=["GASS", "PGASS", "MRES", "ASRC", "DMI", "ADMI"])

        AGE = self.kiosk["AGE"]
        # Check partitioning of TDWI over plant organs
        checksum = Afgen(self._par_values["TDWI"])(AGE) - self.states.TAGP - self.kiosk.TWRT
        if abs(checksum) > 0.0001:
            msg = "Error in partitioning of initial biomass (TDWI)!"
            #raise exc.PartitioningError(msg)
            
        # assign handler for CROP_FINISH signal
        self._connect_signal(self._on_CROP_FINISH, signal=signals.crop_finish)
        self._connect_signal(self._on_DORMANT, signal=signals.crop_dormant)

    @prepare_rates
    def calc_rates(self, day:date, drv:WeatherDataProvider):
        """Calculate state rates for integration 
        """
        params = self.params
        rates  = self.rates
        k = self.kiosk

        # Phenology
        crop_stage = self.pheno.get_variable("STAGE")
        self.pheno.calc_rates(day, drv)
    
        # if before emergence there is no need to continue
        # because only the phenology is running.
        if crop_stage == "ecodorm" or crop_stage == "endodorm":
            return

        # Potential assimilation
        rates.PGASS = self.assim(day, drv)
        
        # (evapo)transpiration rates
        self.evtra(day, drv)

        # nutrient status and reduction factor
        NNI, NPKI, RFNPK = self.npk_stress(day, drv)

        # Select minimum of nutrient and water/oxygen stress
        reduction = min(RFNPK, k.RFTRA)

        rates.GASS = rates.PGASS * reduction

        # Respiration
        PMRES = self.mres(day, drv)
        rates.MRES = min(rates.GASS, PMRES)

        # Net available assimilates
        rates.ASRC = rates.GASS - rates.MRES

        # DM partitioning factors (pf), conversion factor (CVF),
        # dry matter increase (DMI) and check on carbon balance
        pf = self.part.calc_rates(day, drv)
        CVF = 1./((pf.FL/params.CVL(k.AGE) + pf.FS/params.CVS(k.AGE) + pf.FO/params.CVO(k.AGE)) *
                  (1.-pf.FR) + pf.FR/params.CVR(k.AGE))
        rates.DMI = CVF * rates.ASRC
        self._check_carbon_balance(day, rates.DMI, rates.GASS, rates.MRES, CVF, pf)

        # distribution over plant organ
        # Below-ground dry matter increase and root dynamics
        self.ro_dynamics.calc_rates(day, drv)
        # Aboveground dry matter increase and distribution over stems,
        # leaves, organs
        rates.ADMI = (1. - pf.FR) * rates.DMI
        self.st_dynamics.calc_rates(day, drv)
        self.so_dynamics.calc_rates(day, drv)
        self.lv_dynamics.calc_rates(day, drv)
        
        # Update nutrient rates in crop and soil
        self.npk_crop_dynamics.calc_rates(day, drv)

    @prepare_states
    def integrate(self, day:date, delt:float=1.0):
        """Integrate state rates
        """
        rates = self.rates
        states = self.states

        # crop stage before integration
        crop_stage = self.pheno.get_variable("STAGE")
    
        # Phenology
        self.pheno.integrate(day, delt)
        # if before emergence there is no need to continue
        # because only the phenology is running.
        # Just run a touch() to to ensure that all state variables are available
        # in the kiosk
        if crop_stage == "ecodorm" or crop_stage == "endodorm":
            self.touch()
            return

        # Partitioning
        self.part.integrate(day, delt)
        
        # Integrate states on leaves, storage organs, stems and roots
        self.ro_dynamics.integrate(day, delt)
        self.so_dynamics.integrate(day, delt)
        self.st_dynamics.integrate(day, delt)
        self.lv_dynamics.integrate(day, delt)

        # Update nutrient states in crop and soil
        self.npk_crop_dynamics.integrate(day, delt)

        # Integrate total (living+dead) above-ground biomass of the crop
        states.TAGP = self.kiosk.TWLV + \
                      self.kiosk.TWST + \
                      self.kiosk.TWSO

        # total gross assimilation and maintenance respiration 
        states.GASST += rates.GASS
        states.MREST += rates.MRES
        
        # total crop transpiration and soil evaporation
        states.CTRAT += self.kiosk.TRA
        states.CEVST += self.kiosk.EVS

    def _on_DORMANT(self, day:date):
        """Handler for recieving the crop dormancy signal. Upon dormancy, reset
        all crop parameters
        """
        # Deregister parameters from kiosk
        self.part.reset()
        self.assim.reset()
        self.mres.reset()
        self.evtra.reset()
        #self.ro_dynamics.reset()
        self.ro_dynamics.publish_states()
        #self.st_dynamics.reset()
        self.st_dynamics.publish_states()
        self.so_dynamics.reset()
        self.lv_dynamics.reset()
        # Added for book keeping of N/P/K in crop and soil
        self.npk_crop_dynamics.reset()
        self.npk_stress.reset()

        # Manually reset all WOFOST8 crop variables
        s = self.states
        r = self.rates
        
        # Initial total (living+dead) above-ground biomass of the crop
        s.TAGP = self.kiosk.TWLV + self.kiosk.TWST + self.kiosk.TWSO
        s.GASST = s.MREST = s.CTRAT = s.CEVST = s.HI = 0
        s.DOF = s.FINISH_TYPE = None
        s.FIN = False

        r.GASS = r.PGASS = r.MRES = r.ASRC = r.DMI = r.ADMI = 0

        AGE = self.kiosk["AGE"]
        # Check partitioning of TDWI over plant organs
        checksum = Afgen(self._par_values["TDWI"])(AGE) - self.states.TAGP - self.kiosk.TWRT
        if abs(checksum) > 0.0001:
            msg = "Error in partitioning of initial biomass (TDWI)!"
            #raise exc.PartitioningError(msg)
        
        #print(f'Resetting from Dormant: {day}')
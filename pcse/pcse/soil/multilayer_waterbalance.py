"""
Class for layered water balance

Written by: Allard de Wit
Modified by: Will Solow, 2025
"""

from math import sqrt
import numpy as np

from ..utils.traitlets import Float, Int, Instance, Bool
from ..utils.decorators import prepare_rates, prepare_states
from ..util import limit
from ..base import ParamTemplate, StatesTemplate, RatesTemplate, \
     SimulationObject
from ..utils import exceptions as exc
from ..utils import signals

from .soil_profile import SoilProfile

class WaterBalanceLayered_PP(SimulationObject):
    _default_RD = Float(10.)
    _RDold = _default_RD
    _RDM = Float(None)
    
    DSLR = Float(1)
    
    RAINold = Float(0)

    soil_profile = None
    crop_start = Bool(False)

    class Parameters(ParamTemplate):
        pass

    class StateVariables(StatesTemplate):
        MSM = Instance(np.ndarray)
        MWC = Instance(np.ndarray)
        MWTRAT = Float(-99.)
        MEVST = Float(-99.)

    class RateVariables(RatesTemplate):
        MEVS = Float(-99.)
        MWTRA = Float(-99.)

    def initialize(self, day, kiosk, parvalues):
        self.soil_profile = SoilProfile(parvalues)
        parvalues._soildata["soil_profile"] = self.soil_profile

        # Maximum rootable depth
        self._RDM = self.soil_profile.get_max_rootable_depth()
        self.soil_profile.validate_max_rooting_depth(self._RDM)

        SM = np.zeros(len(self.soil_profile))
        WC = np.zeros_like(SM)
        for il, layer in enumerate(self.soil_profile):
            SM[il] = layer.SMFCF
            WC[il] = SM[il] * layer.Thickness
        
        WTRAT = 0.
        EVST = 0.

        states = { "MWC": WC, "MSM":SM, "MEVST": EVST, "MWTRAT": WTRAT}
        self.rates = self.RateVariables(kiosk, publish=["MEVS", "MWTRA"])      
        self.states = self.StateVariables(kiosk, publish=["MWC", "MSM", "MEVST", "MWTRAT"], **states)

    @prepare_rates
    def calc_rates(self, day, drv):
        r = self.rates
        # Transpiration and maximum soil and surface water evaporation rates
        # are calculated by the crop Evapotranspiration module.
        # However, if the crop is not yet emerged then set TRA=0 and use
        # the potential soil/water evaporation rates directly because there is
        # no shading by the canopy.
        if "TRA" not in self.kiosk:
            r.MWTRA = 0.
            EVSMX = drv.ES0
        else:
            r.MWTRA = self.kiosk["TRA"]
            EVSMX = self.kiosk["EVSMX"]

        # Actual evaporation rates
        if self.RAINold >= 1:
            # If rainfall amount >= 1cm on previous day assume maximum soil
            # evaporation
            r.MEVS = EVSMX
            self.DSLR = 1.
        else:
            # Else soil evaporation is a function days-since-last-rain (DSLR)
            self.DSLR += 1
            EVSMXT = EVSMX * (sqrt(self.DSLR) - sqrt(self.DSLR - 1))
            r.MEVS = min(EVSMX, EVSMXT + self.RAINold)

        # Hold rainfall amount to keep track of soil surface wetness and reset self.DSLR if needed
        self.RAINold = drv.RAIN
        
    @prepare_states
    def integrate(self, day, delt=1.0):
        self.states.MSM = self.states.MSM
        self.states.MWC = self.states.MWC

        # Accumulated transpiration and soil evaporation amounts
        self.states.MEVST += self.rates.MEVS * delt
        self.states.MWTRAT += self.rates.MWTRA * delt
        
class WaterBalanceLayered(SimulationObject):
    """This implements a layered water balance to estimate soil water availability for crop growth and water stress.

    The classic free-drainage water-balance had some important limitations such as the inability to take into
    account differences in soil texture throughout the profile and its impact on soil water flow. Moreover,
    in the single layer water balance, rainfall or irrigation will become immediately available to the crop.
    This is incorrect physical behaviour and in many situations it leads to a very quick recovery of the crop
    after rainfall since all the roots have immediate access to infiltrating water. Therefore, with more detailed
    soil data becoming available a more realistic soil water balance was deemed necessary to better simulate soil
    processes and its impact on crop growth.

    The multi-layer water balance represents a compromise between computational complexity, realistic simulation
    of water content and availability of data to calibrate such models. The model still runs on a daily time step
    but does implement the concept of downward and upward flow based on the concept of hydraulic head and soil
    water conductivity. The latter are combined in the so-called Matric Flux Potential. The model computes
    two types of flow of water in the soil:

      (1) a "dry flow" from the matric flux potentials (e.g. the suction gradient between layers)
      (2) a "wet flow" under the current layer conductivities and downward gravity.

    Clearly, only the dry flow may be negative (=upward). The dry flow accounts for the large
    gradient in water potential under dry conditions (but neglects gravity). The wet flow takes into
    account gravity only and will dominate under wet conditions. The maximum of the dry and wet
    flow is taken as the downward flow, which is then further limited in order the prevent
    (a) oversaturation and (b) water content to decrease below field capacity.
    Upward flow is just the dry flow when it is negative. In this case the flow is limited
    to a certain fraction of what is required to get the layers at equal potential, taking
    into account, however, the contribution of an upward flow from further down.

    The configuration of the soil layers is variable but is bound to certain limitations:

    - The layer thickness cannot be made too small. In practice, the top layer should not
      be smaller than 10 to 20 cm. Smaller layers would require smaller time steps than
      one day to simulate realistically, since rain storms will fill up the top layer very
      quickly leading to surface runoff because the model cannot handle the infiltration of
      the rainfall in a single timestep (a day).
    - The crop maximum rootable depth must coincide with a layer boundary. This is to avoid
      that roots can directly access water below the rooting depth. Of course such water may become
      available gradually by upward flow of moisture at some point during the simulation.

    The current python implementation does not yet implement the impact of shallow groundwater
    but this will be added in future versions of the model.

    For an introduction to the concept of Matric Flux Potential see for example:

        Pinheiro, Everton Alves Rodrigues, et al. “A Matric Flux Potential Approach to Assess Plant Water
        Availability in Two Climate Zones in Brazil.” Vadose Zone Journal, vol. 17, no. 1, Jan. 2018, pp. 1–10.
        https://doi.org/10.2136/vzj2016.09.0083.

    **Note**: the current implementation of the model (April 2024) is rather 'Fortran-ish'. This has been done
    on purpose to allow comparisons with the original code in Fortran90. When we are sure that
    the implementation performs properly, we can refactor this in to a more functional structure
    instead of the current code which is too long and full of loops.


    **Simulation parameters:**

    Besides the parameters in the table below, the multi-layer waterbalance requires
    a `SoilProfileDescription` which provides the properties of the different soil
    layers. See the `SoilProfile` and `SoilLayer` classes for the details.

    ========== ====================================================  ====================
     Name      Description                                           Unit
    ========== ====================================================  ====================
    MNOTINF     Maximum fraction of rain not-infiltrating into          -
               the soil
    MIFUNRN     Indicates whether non-infiltrating fraction of   SSi    -
               rain is a function of storm size (1)
               or not (0)
    MSSI        Initial surface storage                                 cm
    MSSMAX      Maximum surface storage                                 cm
    MSMLIM      Maximum soil moisture content of top soil layer         cm3/cm3
    MWAV        Initial amount of water in the soil                     cm
    ========== ====================================================  ====================


    **State variables:**

    =======  ========================================================  ============
     Name     Description                                                  Unit
    =======  ========================================================  ============
    MWTRAT     Total water lost as transpiration as calculated           cm
              by the water balance. This can be different
              from the CTRAT variable which only counts
              transpiration for a crop cycle.
    MEVST      Total evaporation from the soil surface                   cm
    MEVWT      Total evaporation from a water surface                    cm
    MTSR       Total surface runoff                                      cm
    MRAINT     Total amount of rainfall (eff + non-eff)                  cm
    MWDRT      Amount of water added to root zone by increase            cm
              of root growth
    MTOTINF    Total amount of infiltration                              cm
    MTOTIRR    Total amount of effective irrigation                      cm

    MSM        Volumetric moisture content in the different soil          -
              layers (array)
    MWC        Water content in the different soil                       cm
              layers (array)
    MW         Amount of water in root zone                              cm
    MWLOW      Amount of water in the subsoil (between current           cm
              rooting depth and maximum rootable depth)
    MWWLOW     Total amount of water                                     cm
              in the  soil profile (WWLOW = WLOW + W)
    MWBOT      Water below maximum rootable depth and unavailable
              for plant growth.                                         cm
    MWAVUPP    Plant available water (above wilting point) in the        cm
              rooted zone.
    MWAVLOW    Plant available water (above wilting point) in the        cm
              potential root zone (below current roots)
    MWAVBOT    Plant available water (above wilting point) in the        cm
              zone below the maximum rootable depth
    MSS        Surface storage (layer of water on surface)               cm
    MSM_MEAN   Mean water content in rooted zone                         cm3/cm3
    MPERCT     Total amount of water percolating from rooted             cm
              zone to subsoil
    MLOSST     Total amount of water lost to deeper soil                 cm
    =======  ========================================================  ============


    **Rate variables**

    ========== ==================================================  ====================
     Name      Description                                          Units
    ========== ==================================================  ====================
    MFlow        Rate of flow from one layer to the next              cm/day
    MRIN         Rate of infiltration at the surface                  cm/day
    MWTRALY      Rate of transpiration from the different
                soil layers (array)                                  cm/day
    MWTRA        Total crop transpiration rate accumulated over       cm/day
                soil layers.
    MEVS         Soil evaporation rate                                cm/day
    MEVW         Open water evaporation rate                          cm/day
    MRIRR        Rate of irrigation                                   cm/day
    MDWC         Net change in water amount per layer (array)         cm/day
    MDRAINT      Change in rainfall accumlation                       cm/day
    MDSS         Change in surface storage                            cm/day
    MDTSR        Rate of surface runoff                               cm/day
    MBOTTOMFLOW  Flow of the bottom of the profile                    cm/day
    ========== ==================================================  ====================
    """
    _default_RD = Float(10.) 
    _RDold = _default_RD
    _RINold = Float(0.)
    _RIRR = Float(0.)
    _DSLR = Int(None)
    _RDM = Float(None)
    _RAIN = Float(None)
    _WCI = Float(None)

    # Max number of flow iterations and precision required
    MaxFlowIter = 50
    TinyFlow = 0.001

    # Maximum upward flow is 50% of amount needed to reach equilibrium between layers
    UpwardFlowLimit = 0.50

    soil_profile = None
    parameter_provider = None

    crop_start = Bool(False)

    class Parameters(ParamTemplate):
        MIFUNRN   = Float(-99.)
        MNOTINF   = Float(-99.)
        MSSI      = Float(-99.)
        MSSMAX    = Float(-99.)
        MSMLIM    = Float(-99.)
        MWAV      = Float(-99.)

    class StateVariables(StatesTemplate):
        MWTRAT        = Float(-99.)
        MEVST         = Float(-99.)
        MEVWT         = Float(-99.)
        MTSR          = Float(-99.)
        MRAINT        = Float(-99.)
        MWDRT         = Float(-99.)
        MTOTINF       = Float(-99.)
        MTOTIRR       = Float(-99.)
        MCRT          = Float(-99.)
        MSM           = Instance(np.ndarray)
        MSM_MEAN      = Float(-99.)
        MWC           = Instance(np.ndarray)
        MW            = Float(-99.)
        MWLOW         = Float(-99.)
        MWWLOW        = Float(-99.)
        MWBOT         = Float(-99.)
        MWAVUPP       = Float(-99.)
        MWAVLOW       = Float(-99.)
        MWAVBOT       = Float(-99.)
        MSS           = Float(-99.)
        MBOTTOMFLOWT  = Float(-99.)
        MPERCT        = Float(-99.)

    class RateVariables(RatesTemplate):
        MFlow       =    Instance(np.ndarray)
        MRIN        =    Float(-99.)
        MWTRALY     =    Instance(np.ndarray)
        MWTRA       =    Float(-99.)
        MEVS        =    Float(-99.)
        MEVW        =    Float(-99.)
        MRIRR       =    Float(-99.)
        MDWC        =    Instance(np.ndarray)
        MDRAINT     =    Float(-99.)
        MDSS        =    Float(-99.)
        MDTSR       =    Float(-99.)
        MBOTTOMFLOW =    Float(-99.)
        MPERC       =    Float(-99.)

    def initialize(self, day, kiosk, parvalues):

        self.soil_profile = SoilProfile(parvalues)
        parvalues._soildata["soil_profile"] = self.soil_profile

        # Maximum rootable depth
        RDMsoil = self.soil_profile.get_max_rootable_depth()

        self._RDM = self.soil_profile.get_max_rootable_depth()
        self.soil_profile.validate_max_rooting_depth(self._RDM)

        self.params = self.Parameters(parvalues)
        p = self.params

        self.parameter_provider = parvalues

        self.soil_profile.determine_rooting_status(self._default_RD, self._RDM)

        if self.soil_profile.GroundWater:
            raise NotImplementedError("Groundwater influence not yet implemented.")
        else:
            # AVMAX -  maximum available content of layer(s)
            TOPLIM = 0.0
            LOWLIM = 0.0
            AVMAX = []
            for il, layer in enumerate(self.soil_profile):
                if layer.rooting_status in ["rooted", "partially rooted"]:
                    # Check whether SMLIM is within boundaries
                    SML = limit(layer.SMW, layer.SM0, p.MSMLIM)
                    AVMAX.append((SML - layer.SMW) * layer.Thickness)   
                    TOPLIM += AVMAX[il]
                elif layer.rooting_status == "potentially rooted":
                    # below the rooted zone the maximum is saturation
                    SML = layer.SM0
                    AVMAX.append((SML - layer.SMW) * layer.Thickness)  
                    LOWLIM += AVMAX[il]
                else:  
                    break

        if p.MWAV <= 0.0:
            # no available water
            TOPRED = 0.0
            LOWRED = 0.0
        elif p.MWAV <= TOPLIM:
            # available water fits in layer(s) 1..ILR, these layers are rooted or almost rooted
            # reduce amounts with ratio WAV / TOPLIM
            TOPRED = p.MWAV / TOPLIM
            LOWRED = 0.0
        elif p.MWAV < TOPLIM + LOWLIM:
            # available water fits in potentially rooted layer
            # rooted zone is filled at capacity ; the rest reduced
            TOPRED = 1.0
            LOWRED = (p.WAV-TOPLIM) / LOWLIM
        else:
            # water does not fit ; all layers "full"
            TOPRED = 1.0
            LOWRED = 1.0

        W = 0.0    ; WAVUPP = 0.0
        WLOW = 0.0 ; WAVLOW = 0.0
        SM = np.zeros(len(self.soil_profile))
        WC = np.zeros_like(SM)
        Flow = np.zeros(len(self.soil_profile) + 1)

        for il, layer in enumerate(self.soil_profile):
            if layer.rooting_status in ["rooted", "partially rooted"]:
                # Part of the water assigned to ILR may not actually be in the rooted zone, but it will
                # be available shortly through root growth (and through numerical mixing).
                SM[il] = layer.SMW + AVMAX[il] * TOPRED / layer.Thickness
                W += SM[il] * layer.Thickness * layer.Wtop
                WLOW += SM[il] * layer.Thickness * layer.Wpot
                # available water
                WAVUPP += (SM[il] - layer.SMW) * layer.Thickness * layer.Wtop
                WAVLOW += (SM[il] - layer.SMW) * layer.Thickness * layer.Wpot
            elif layer.rooting_status == "potentially rooted":
                SM[il] = layer.SMW + AVMAX[il] * LOWRED / layer.Thickness
                WLOW += SM[il] * layer.Thickness * layer.Wpot
                # available water
                WAVLOW += (SM[il] - layer.SMW) * layer.Thickness * layer.Wpot
            else:
                # below the maximum rooting depth, set SM content to wilting point
                SM[il] = layer.SMW
            WC[il] = SM[il] * layer.Thickness

            # set groundwater depth far away for clarity ; this prevents also
            # the root routine to stop root growth when they reach the groundwater
            ZT = 999.0

        # soil evaporation, days since last rain
        top_layer = self.soil_profile[0]
        top_layer_half_wet = top_layer.SMW + 0.5 * (top_layer.SMFCF - top_layer.SMW)
        self._DSLR = 5 if SM[0] <= top_layer_half_wet else 1

        # all summation variables of the water balance are set at zero.
        states = {"MWTRAT": 0., "MEVST": 0., "MEVWT": 0., "MTSR": 0., "MWDRT": 0.,
                  "MTOTINF": 0., "MTOTIRR": 0., "MBOTTOMFLOWT": 0.,
                  "MCRT": 0., "MRAINT": 0., "MWLOW": WLOW, "MW": W, "MWC": WC, "MSM":SM,
                  "MSS": p.MSSI, "MWWLOW": W+WLOW, "MWBOT":0., "MSM_MEAN": W/self._default_RD,
                  "MWAVUPP": WAVUPP, "MWAVLOW": WAVLOW, "MWAVBOT":0., "MPERCT": 0
                  }
        self.states = self.StateVariables(kiosk, publish=["MWTRAT", "MEVST", "MEVWT", "MTSR", "MWDRT", "MTOTINF", "MPERCT",
                                                          "MTOTIRR", "MBOTTOMFLOWT", "MCRT", "MRAINT", "MWLOW", "MW", "MWC", "MSM",
                                                          "MSS", "MWWLOW", "MWBOT", "MSM_MEAN", "MWAVUPP", "MWAVLOW", "MWAVBOT"], **states)

        # Initial values for profile water content
        self._WCI = WC.sum()

        # rate variables
        self.rates = self.RateVariables(kiosk, publish=["MRIN", "MFlow", "MWTRALY", "MWTRA", "MEVS", "MEVW", "MRIRR", 
                                                        "MDWC", "MDRAINT", "MDSS", "MDTSR", "MBOTTOMFLOW", "MPERC"])
        self.rates.MFlow = Flow

        # Connect to CROP_START/CROP_FINISH/IRRIGATE signals
        self._connect_signal(self._on_CROP_START, signals.crop_start)
        self._connect_signal(self._on_CROP_FINISH, signals.crop_finish)
        self._connect_signal(self._on_IRRIGATE, signals.irrigate)

    @prepare_rates
    def calc_rates(self, day, drv):
        p = self.params
        s = self.states
        k = self.kiosk
        r = self.rates

        delt = 1.0

        # Update rooting setup if a new crop has started
        if self.crop_start:
            self.crop_start = False
            self._setup_new_crop()

        # Rate of irrigation (RIRR)
        r.MRIRR = self._RIRR
        self._RIRR = 0.

        # copy rainfall rate for totalling in RAINT
        self._RAIN = drv.RAIN

        # Crop transpiration and maximum evaporation rates
        if "TRALY" in self.kiosk:
            # Transpiration and maximum soil and surface water evaporation rates
            WTRALY = k.TRALY
            r.MWTRA = k.TRA
            EVWMX = k.EVWMX
            EVSMX = k.EVSMX
        else:
            # However, if the crop is not yet emerged then set WTRALY/TRA=0
            WTRALY = np.zeros_like(s.MSM)
            r.MWTRA = 0.
            EVWMX = drv.E0
            EVSMX = drv.ES0

        # Actual evaporation rates
        r.MEVW = 0.
        r.MEVS = 0.
        if s.MSS > 1.:
            # If surface storage > 1cm then evaporate from water layer on soil surface
            r.MEVW = EVWMX
        else:
            # else assume evaporation from soil surface
            if self._RINold >= 1:
                r.MEVS = EVSMX
                self._DSLR = 1
            else:
                # Else soil evaporation is a function days-since-last-rain (DSLR)
                EVSMXT = EVSMX * (sqrt(self._DSLR + 1) - sqrt(self._DSLR))
                r.MEVS = min(EVSMX, EVSMXT + self._RINold)
                self._DSLR += 1

        # conductivities and Matric Flux Potentials for all layers
        pF = np.zeros_like(s.MSM)
        conductivity = np.zeros_like(s.MSM)
        matricfluxpot = np.zeros_like(s.MSM)
        for i, layer in enumerate(self.soil_profile):
            pF[i] = layer.PFfromSM(s.MSM[i])
            conductivity[i] = 10**layer.CONDfromPF(pF[i])
            matricfluxpot[i] = layer.MFPfromPF(pF[i])
            if self.soil_profile.GroundWater:
                raise NotImplementedError("Groundwater influence not yet implemented.")

        # Potentially infiltrating rainfall
        if p.MIFUNRN == 0:
            RINPRE = (1. - p.MNOTINF) * drv.RAIN
        else:
            # infiltration is function of storm size (NINFTB)
            RINPRE = (1. - p.MNOTINF * self.NINFTB(drv.RAIN)) * drv.RAIN


        # Second stage preliminary infiltration rate (RINPRE)
        # including surface storage and irrigation
        RINPRE = RINPRE + r.MRIRR + s.MSS
        if s.MSS > 0.1:
            # with surface storage, infiltration limited by SOPE
            AVAIL = RINPRE + r.MRIRR - r.MEVW
            RINPRE = min(self.soil_profile.SurfaceConductivity, AVAIL)

        # maximum flow at Top Boundary of each layer
        # ------------------------------------------
        # DOWNWARD flows are calculated in two ways,
        # (1) a "dry flow" from the matric flux potentials
        # (2) a "wet flow" under the current layer conductivities and downward gravity.
        # Clearly, only the dry flow may be negative (=upward). The dry flow accounts for the large
        # gradient in potential under dry conditions (but neglects gravity). The wet flow takes into
        # account gravity only and will dominate under wet conditions. The maximum of the dry and wet
        # flow is taken as the downward flow, which is then further limited in order the prevent
        # (a) oversaturation and (b) water content to decrease below field capacity.
        #
        # UPWARD flow is just the dry flow when it is negative. In this case the flow is limited
        # to a certain fraction of what is required to get the layers at equal potential, taking
        # into account, however, the contribution of an upward flow from further down. Hence, in
        # case of upward flow from the groundwater, this upward flow is propagated upward if the
        # suction gradient is sufficiently large.

        FlowMX = np.zeros(len(s.MSM) + 1)
        # first get flow through lower boundary of bottom layer
        if self.soil_profile.GroundWater:
            raise NotImplementedError("Groundwater influence not yet implemented.")
        #    the old capillairy rise routine is used to estimate flow to/from the groundwater
        #    note that this routine returns a positive value for capillairy rise and a negative
        #    value for downward flow, which is the reverse from the convention in WATFDGW.

        # is = SubSoilType
        # if (ZT >= LBSL(NSL)) then
        #     # groundwater below the layered system ; call the old capillairty rise routine
        #     # the layer PF is allocated at 1/3 * TSL above the lower boundary ; this leeds
        #     # to a reasonable result for groundwater approaching the bottom layer
        #     call SUBSOL (PF(NSL), ZT-LBSL(NSL)+TSL(NSL)/3.0, SubFlow, Soil(is)%CONDfromPF, Soil(is)%ilCOND)
        #     # write (*,*) 'call SUBSOL ', PF(NSL), ZT-LBSL(NSL)+TSL(NSL)/3.0, SubFlow
        #     if (SubFlow >= 0.0) then
        #         # capillairy rise is limited by the amount required to reach equilibrium:
        #         # step 1. calculate equilibrium ZT for all air between ZT and top of layer
        #         EqAir   = WSUB0 - WSUB + (WC0(NSL)-WC(NSL))
        #         # step 2. the groundwater level belonging to this amount of air in equilibrium
        #         ZTeq1   = (LBSL(NSL)-TSL(NSL)) + AFGEN(Soil(is)%HeightFromAir, EquilTableLEN, EqAir)
        #         # step 3. this level should normally lie below the current level (otherwise there should
        #         # not be capillairy rise). In rare cases however, due to the use of a mid-layer height
        #         # in subroutine SUBSOL, a deviation could occur
        #         ZTeq2   = MAX(ZT, ZTeq1)
        #         # step 4. calculate for this ZTeq2 the equilibrium amount of water in the layer
        #         WCequil = AFGEN(Soil(is)%WaterFromHeight, EquilTableLEN, ZTeq2-LBSL(NSL)+TSL(NSL)) - &
        #                   AFGEN(Soil(is)%WaterFromHeight, EquilTableLEN, ZTeq2-LBSL(NSL))
        #         # step5. use this equilibrium amount to limit the upward flow
        #         FlowMX(NSL+1) = -1.0 * MIN (SubFlow, MAX(WCequil-WC(NSL),0.0)/DELT)
        #     else:
        #         # downward flow ; air-filled pore space of subsoil limits downward flow
        #         AirSub = (ZT-LBSL(NSL))*SubSM0 - AFGEN(Soil(is)%WaterFromHeight, EquilTableLEN, ZT-LBSL(NSL))
        #         FlowMX(NSL+1) = MIN (ABS(SubFlow), MAX(AirSub,0.0)/DELT)
        #         # write (*,*) 'Limiting downward flow: AirSub, FlowMX(NSL+1) = ', AirSub, FlowMX(NSL+1)
        # else:
        #     # groundwater is in the layered system ; no further downward flow
        #     FlowMX(NSL+1) = 0.0
        else:
            # Bottom layer conductivity limits the flow. Below field capacity there is no
            # downward flow, so downward flow through lower boundary can be guessed as
            FlowMX[-1] = max(self.soil_profile[-1].CondFC, conductivity[-1])

        # drainage
        DMAX = 0.0

        LIMDRY = np.zeros_like(s.MSM)
        LIMWET = np.zeros_like(s.MSM)
        TSL = [l.Thickness for l in self.soil_profile]
        for il in reversed(range(len(s.MSM))):
            # limiting DOWNWARD flow rate
            # == wet conditions: the soil conductivity is larger
            #    the soil conductivity is the flow rate for gravity only
            #    this limit is DOWNWARD only
            # == dry conditions: the MFP gradient
            #    the MFP gradient is larger for dry conditions
            #    allows SOME upward flow
            if il == 0:  # Top soil layer
                LIMWET[il] = self.soil_profile.SurfaceConductivity
                LIMDRY[il] = 0.0
            else:
                # the limit under wet conditions is a unit gradient
                LIMWET[il] = (TSL[il-1]+TSL[il]) / (TSL[il-1]/conductivity[il-1] + TSL[il]/conductivity[il])

                # compute dry flow given gradients in matric flux potential
                if self.soil_profile[il-1] == self.soil_profile[il]:
                    # Layers il-1 and il have same properties: flow rates are estimated from
                    # the gradient in Matric Flux Potential
                    LIMDRY[il] = 2.0 * (matricfluxpot[il-1]-matricfluxpot[il]) / (TSL[il-1]+TSL[il])
                    if LIMDRY[il] < 0.0:
                        # upward flow rate ; amount required for equal water content is required below
                        MeanSM = (s.MWC[il-1] + s.MWC[il]) / (TSL[il-1]+TSL[il])
                        EqualPotAmount = s.MWC[il-1] - TSL[il-1] * MeanSM  # should be negative like the flow
                else:
                    # iterative search to PF at layer boundary (by bisection)
                    il1  = il-1; il2 = il
                    PF1  = pF[il1]; PF2 = pF[il2]
                    MFP1 = matricfluxpot[il1]; MFP2 = matricfluxpot[il2]
                    for z in range(self.MaxFlowIter):  # Loop counter not used here
                        PFx = (PF1 + PF2) / 2.0
                        Flow1 = 2.0 * (+ MFP1 - self.soil_profile[il1].MFPfromPF(PFx)) / TSL[il1]
                        Flow2 = 2.0 * (- MFP2 + self.soil_profile[il2].MFPfromPF(PFx)) / TSL[il2]
                        if abs(Flow1-Flow2) < self.TinyFlow:
                            # sufficient accuracy
                            break
                        elif abs(Flow1) > abs(Flow2):
                            # flow in layer 1 is larger ; PFx must shift in the direction of PF1
                            PF2 = PFx
                        elif abs(Flow1) < abs(Flow2):
                            # flow in layer 2 is larger ; PFx must shift in the direction of PF2
                            PF1 = PFx
                    else:  # No break
                        msg = 'WATFDGW: LIMDRY flow iteration failed. Are your soil moisture and ' + \
                              'conductivity curves decreasing with increasing pF?'
                        raise exc.PCSEError(msg)
                    LIMDRY[il] = (Flow1 + Flow2) / 2.0

                    if LIMDRY[il] < 0.0:
                        # upward flow rate ; amount required for equal potential is required below
                        Eq1 = -s.MWC[il2]; Eq2 = 0.0
                        for z in range(self.MaxFlowIter):
                            EqualPotAmount = (Eq1 + Eq2) / 2.0
                            SM1 = (s.MWC[il1] - EqualPotAmount) / TSL[il1]
                            SM2 = (s.MWC[il2] + EqualPotAmount) / TSL[il2]
                            PF1 = self.soil_profile[il1].SMfromPF(SM1)
                            PF2 = self.soil_profile[il2].SMfromPF(SM2)
                            if abs(Eq1-Eq2) < self.TinyFlow:
                                # sufficient accuracy
                                break
                            elif PF1 > PF2:
                                # suction in top layer 1 is larger ; absolute amount should be larger
                                Eq2 = EqualPotAmount
                            else:
                                # suction in bottom layer 1 is larger ; absolute amount should be reduced
                                Eq1 = EqualPotAmount
                        else:
                            msg = "WATFDGW: Limiting amount iteration in dry flow failed. Are your soil moisture " \
                                  "and conductivity curves decreasing with increase pF?"
                            raise exc.PCSEError(msg)

            FlowDown = True  # default
            if LIMDRY[il] < 0.0:
                # upward flow (negative !) is limited by fraction of amount required for equilibrium
                FlowMax = max(LIMDRY[il], EqualPotAmount * self.UpwardFlowLimit)
                if il > 0:
                    # upward flow is limited by amount required to bring target layer at equilibrium/field capacity
                    # if (il==2) write (*,*) '2: ',FlowMax, LIMDRY(il), EqualPotAmount * UpwardFlowLimit
                    if self.soil_profile.GroundWater:
                        # soil does not drain below equilibrium with groundwater
                        # FCequil = MAX(WCFC(il-1), EquilWater(il-1))
                        raise NotImplementedError("Groundwater influence not implemented yet.")
                    else:
                        # free drainage
                        FCequil = self.soil_profile[il-1].WCFC

                    TargetLimit = WTRALY[il-1] + FCequil - s.MWC[il-1]/delt
                    if TargetLimit > 0.0:
                        # target layer is "dry": below field capacity ; limit upward flow
                        FlowMax = max(FlowMax, -1.0 * TargetLimit)
                        # there is no saturation prevention since upward flow leads to a decrease of WC[il]
                        # instead flow is limited in order to prevent a negative water content
                        FlowMX[il] = max(FlowMax, FlowMX[il+1] + WTRALY[il] - s.MWC[il]/delt)
                        FlowDown = False
                    elif self.soil_profile.GroundWater:
                        # target layer is "wet", above field capacity. Since gravity is neglected
                        # in the matrix potential model, this "wet" upward flow is neglected.
                        FlowMX[il] = 0.0
                        FlowDown = True
                    else:
                        # target layer is "wet", above field capacity, without groundwater
                        # The free drainage model implies that upward flow is rejected here.
                        # Downward flow is enabled and the free drainage model applies.
                        FlowDown = True

            if FlowDown:
                # maximum downward flow rate (LIMWET is always a positive number)
                FlowMax = max(LIMDRY[il], LIMWET[il])
                # this prevents saturation of layer il
                # maximum top boundary flow is bottom boundary flow plus saturation deficit plus sink
                FlowMX[il] = min(FlowMax, FlowMX[il+1] + (self.soil_profile[il].WC0 - s.MWC[il])/delt + WTRALY[il])
        # end for

        r.MRIN = min(RINPRE, FlowMX[0])

        # contribution of layers to soil evaporation in case of drought upward flow is allowed
        EVSL = np.zeros_like(s.MSM)
        for il, layer in enumerate(self.soil_profile):
            if il == 0:
                EVSL[il] = min(r.MEVS, (s.MWC[il] - layer.WCW) / delt + r.MRIN - WTRALY[il])
                EVrest = r.MEVS - EVSL[il]
            else:
                Available = max(0.0, (s.MWC[il] - layer.WCW)/delt - WTRALY[il])
                if Available >= EVrest:
                    EVSL[il] = EVrest
                    EVrest   = 0.0
                    break
                else:
                    EVSL[il] = Available
                    EVrest   = EVrest - Available
        # reduce evaporation if entire profile becomes airdry
        # there is no evaporative flow through lower boundary of layer NSL
        r.MEVS = r.MEVS - EVrest

        # Convert contribution of soil layers to EVS as an upward flux
        # evaporative flow (taken positive !!!!) at layer boundaries
        NSL = len(s.MSM)
        EVflow = np.zeros_like(FlowMX)
        EVflow[0] = r.MEVS
        for il in range(1, NSL):
            EVflow[il] = EVflow[il-1] - EVSL[il-1]
        EVflow[NSL] = 0.0  # see comment above

        # limit downward flows as to not get below field capacity / equilibrium content
        Flow = np.zeros_like(FlowMX)
        r.MDWC = np.zeros_like(s.MSM)
        Flow[0] = r.MRIN - EVflow[0]
        for il, layer in enumerate(self.soil_profile):
            if self.soil_profile.GroundWater:
                # soil does not drain below equilibrium with groundwater
                #WaterLeft = max(self.WCFC[il], EquilWater[il])
                raise NotImplementedError("Groundwater influence not implemented yet.")
            else:
                # free drainage
                WaterLeft = layer.WCFC
            MXLOSS = (s.MWC[il] - WaterLeft)/delt               # maximum loss
            Excess = max(0.0, MXLOSS + Flow[il] - WTRALY[il])  # excess of water (positive)
            Flow[il+1] = min(FlowMX[il+1], Excess - EVflow[il+1])  # note that a negative (upward) flow is not affected
            # rate of change
            r.MDWC[il] = Flow[il] - Flow[il+1] - WTRALY[il]

        # Flow at the bottom of the profile
        r.MBOTTOMFLOW = Flow[-1]

        if self.soil_profile.GroundWater:
            # groundwater influence
            # DWBOT = LOSS - Flow[self.NSL+1]
            # DWSUB = Flow[self.NSL+1]
            raise NotImplementedError("Groundwater influence not implemented yet.")

        # Computation of rate of change in surface storage and surface runoff
        # SStmp is the layer of water that cannot infiltrate and that can potentially
        # be stored on the surface. Here we assume that RAIN_NOTINF automatically
        # ends up in the surface storage (and finally runoff).
        SStmp = drv.RAIN + r.MRIRR - r.MEVW - r.MRIN
        # rate of change in surface storage is limited by SSMAX - SS
        r.MDSS = min(SStmp, (p.MSSMAX - s.MSS))
        # Remaining part of SStmp is send to surface runoff
        r.MDTSR = SStmp - r.MDSS
        # incoming rainfall rate
        r.MDRAINT = drv.RAIN

        self._RINold = r.MRIN
        r.MFlow = Flow

    @prepare_states
    def integrate(self, day, delt):
        p = self.params
        s = self.states
        k = self.kiosk
        r = self.rates

        # amount of water in soil layers ; soil moisture content
        SM = np.zeros_like(s.MSM)
        WC = np.zeros_like(s.MWC)
        for il, layer in enumerate(self.soil_profile):
            WC[il] = s.MWC[il] + r.MDWC[il] * delt
            SM[il] = WC[il] / layer.Thickness
        # NOTE: We cannot replace WC[il] with s.WC[il] above because the kiosk will not
        # be updated since traitlets cannot monitor changes within lists/arrays.
        # So we have to assign:
        s.MSM = SM
        s.MWC = WC

        # total transpiration
        s.MWTRAT += r.MWTRA * delt

        # total evaporation from surface water layer and/or soil
        s.MEVWT += r.MEVW * delt
        s.MEVST += r.MEVS * delt

        # totals for rainfall, irrigation and infiltration
        s.MRAINT += self._RAIN
        s.MTOTINF += r.MRIN * delt
        s.MTOTIRR += r.MRIRR * delt

        # surface storage and runoff
        s.MSS += r.MDSS * delt
        s.MTSR += r.MDTSR * delt

        # loss of water by outflow through bottom of profile
        s.MBOTTOMFLOWT += r.MBOTTOMFLOW * delt

        # percolation from rootzone ; interpretation depends on mode
        if self.soil_profile.GroundWater:
            # with groundwater this flow is either percolation or capillary rise
            if r.MPERC > 0.0:
                s.MPERCT = s.MPERCT + r.MPERC * delt
            else:
                s.MCRT = s.MCRT - r.MPERC * delt
        else:
            s.MCRT = 0.0

        RD = self._determine_rooting_depth()
        if abs(RD - self._RDold) > 0.001:
            self.soil_profile.determine_rooting_status(RD, self._RDM)

        # compute summary values for rooted, potentially rooted and unrooted soil compartments
        W = 0.0 ; WAVUPP = 0.0
        WLOW = 0.0 ; WAVLOW = 0.0
        WBOT = 0.0 ; WAVBOT = 0.0

        # get W and WLOW and available water amounts
        for il, layer in enumerate(self.soil_profile):
            W += s.MWC[il] * layer.Wtop
            WLOW += s.MWC[il] * layer.Wpot
            WBOT += s.MWC[il] * layer.Wund
            WAVUPP += (s.MWC[il] - layer.WCW) * layer.Wtop
            WAVLOW += (s.MWC[il] - layer.WCW) * layer.Wpot
            WAVBOT += (s.MWC[il] - layer.WCW) * layer.Wund

        # Update states
        s.MW = W
        s.MWLOW = WLOW
        s.MWWLOW = s.MW + s.MWLOW
        s.MWBOT = WBOT
        s.MWAVUPP = WAVUPP
        s.MWAVLOW = WAVLOW
        s.MWAVBOT = WAVBOT

        self._RDold = RD
        s.MSM_MEAN = s.MW/RD

    @prepare_states
    def finalize(self, day):
        s = self.states
        p = self.params
        if self.soil_profile.GroundWater:
            pass
        else:
            # checksums waterbalance for system Free Drainage version
            checksum = (p.MSSI - s.MSS  
                        + self._WCI - s.MWC.sum()  
                        + s.MRAINT + s.MTOTIRR  
                        - s.MWTRAT - s.MEVWT - s.MEVST - s.MTSR - s.MBOTTOMFLOWT
                        )
            if abs(checksum) > 0.0001:
                msg = "Waterbalance not closing on %s with checksum: %f" % (day, checksum)
                raise exc.WaterBalanceError(msg)

    def _determine_rooting_depth(self):
        """Determines appropriate use of the rooting depth (RD)

        This function includes the logic to determine the depth of the upper (rooted)
        layer of the water balance. See the comment in the code for a detailed description.
        """
        if "RD" in self.kiosk:
            return self.kiosk["RD"]
        else:
            # Hold RD at default value
            return self._default_RD

    def _on_CROP_START(self):
        self.crop_start = True

    def _on_CROP_FINISH(self):
        pass
        # self.in_crop_cycle = False
        # self.rooted_layer_needs_reset = True

    def _on_IRRIGATE(self, amount, efficiency):
        self._RIRR = amount * efficiency

    def _setup_new_crop(self):
        """Retrieves the crop maximum rootable depth, validates it and updates the rooting status
        in order to have a correct calculation of the summary waterbalance states.

        """
        self._RDM = self.parameter_provider["RDMCR"]
        self.soil_profile.validate_max_rooting_depth(self._RDM)
        self.soil_profile.determine_rooting_status(self._default_RD, self._RDM)

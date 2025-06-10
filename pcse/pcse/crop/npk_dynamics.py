"""Overall implementation for the NPK dynamics of the crop including
subclasses to 
    * NPK Demand Uptake
    * NPK Stress
    * NPK Translocation
    
Written by: Allard de Wit (allard.dewit@wur.nl), April 2014
Modified by Will Solow, 2024
"""

from datetime import date

from ..nasapower import WeatherDataProvider
from ..utils import exceptions as exc
from ..utils.traitlets import Float, Instance
from ..utils.decorators import prepare_rates, prepare_states
from ..base import ParamTemplate, StatesTemplate, RatesTemplate, \
    SimulationObject, VariableKiosk
from ..util import AfgenTrait
from .nutrients import NPK_Translocation
from .nutrients import NPK_Demand_Uptake


class NPK_Crop_Dynamics(SimulationObject):
    """Implementation of overall NPK crop dynamics.

    NPK_Crop_Dynamics implements the overall logic of N/P/K book-keeping within the
    crop.

    **Simulation parameters**
    
    =============  ================================================= =======================
     Name           Description                                        Unit
    =============  ================================================= =======================
    NMAXLV_TB      Maximum N concentration in leaves as               kg N kg-1 dry biomass
                   function of dvs
    PMAXLV_TB      As for P                                           kg P kg-1 dry biomass
    KMAXLV_TB      As for K                                           kg K kg-1 dry biomass

    NMAXRT_FR      Maximum N concentration in roots as fraction       -
                   of maximum N concentration in leaves
    PMAXRT_FR      As for P                                           -
    KMAXRT_FR      As for K                                           -

    NMAXST_FR      Maximum N concentration in stems as fraction       -
                   of maximum N concentration in leaves
    KMAXST_FR      As for K                                           -
    PMAXST_FR      As for P                                           -

    NRESIDLV       Residual N fraction in leaves                      kg N kg-1 dry biomass
    PRESIDLV       Residual P fraction in leaves                      kg P kg-1 dry biomass
    KRESIDLV       Residual K fraction in leaves                      kg K kg-1 dry biomass

    NRESIDRT       Residual N fraction in roots                       kg N kg-1 dry biomass
    PRESIDRT       Residual P fraction in roots                       kg P kg-1 dry biomass
    KRESIDRT       Residual K fraction in roots                       kg K kg-1 dry biomass

    NRESIDST       Residual N fraction in stems                       kg N kg-1 dry biomass
    PRESIDST       Residual P fraction in stems                       kg P kg-1 dry biomass
    KRESIDST       Residual K fraction in stems                       kg K kg-1 dry biomass
    =============  ================================================= =======================

    **State variables**

    ==========  ================================================== ============
     Name        Description                                          Unit
    ==========  ================================================== ============
    NAMOUNTLV     Actual N amount in living leaves                  |kg N ha-1|
    PAMOUNTLV     Actual P amount in living leaves                  |kg P ha-1|
    KAMOUNTLV     Actual K amount in living leaves                  |kg K ha-1|
        
    NAMOUNTST     Actual N amount in living stems                   |kg N ha-1|
    PAMOUNTST     Actual P amount in living stems                   |kg P ha-1|
    KAMOUNTST     Actual K amount in living stems                   |kg K ha-1|

    NAMOUNTSO     Actual N amount in living storage organs          |kg N ha-1|
    PAMOUNTSO     Actual P amount in living storage organs          |kg P ha-1|
    KAMOUNTSO     Actual K amount in living storage organs          |kg K ha-1|
    
    NAMOUNTRT     Actual N amount in living roots                   |kg N ha-1|
    PAMOUNTRT     Actual P amount in living roots                   |kg P ha-1|
    KAMOUNTRT     Actual K amount in living roots                   |kg K ha-1|
    
    NUPTAKE_T    total absorbed N amount                            |kg N ha-1|
    PUPTAKE_T    total absorbed P amount                            |kg P ha-1|
    KUPTAKE_T    total absorbed K amount                            |kg K ha-1|
    NFIX_T       total biological fixated N amount                  |kg N ha-1|
    ==========  ================================================== ============

    **Rate variables**

    ===========  =================================================  ================
     Name         Description                                           Unit
    ===========  =================================================  ================
    RNAMOUNTLV     Weight increase (N) in leaves                    |kg N ha-1 d-1|
    RPAMOUNTLV     Weight increase (P) in leaves                    |kg P ha-1 d-1|
    RKAMOUNTLV     Weight increase (K) in leaves                    |kg K ha-1 d-1|
    
    RNAMOUNTST     Weight increase (N) in stems                     |kg N ha-1 d-1|
    RPAMOUNTST     Weight increase (P) in stems                     |kg P ha-1 d-1|
    RKAMOUNTST     Weight increase (K) in stems                     |kg K ha-1 d-1|
        
    RNAMOUNTRT     Weight increase (N) in roots                     |kg N ha-1 d-1|
    RPAMOUNTRT     Weight increase (P) in roots                     |kg P ha-1 d-1|
    RKAMOUNTRT     Weight increase (K) in roots                     |kg K ha-1 d-1|
    
    RNAMOUNTSO     Weight increase (N) in storage organs            |kg N ha-1 d-1|
    RPAMOUNTSO     Weight increase (P) in storage organs            |kg P ha-1 d-1|
    RKAMOUNTSO     Weight increase (K) in storage organs            |kg K ha-1 d-1|

    RNDEATHLV      Rate of N loss in leaves                         |kg N ha-1 d-1|
    RPDEATHLV      as for P                                         |kg P ha-1 d-1|
    RKDEATHLV      as for K                                         |kg K ha-1 d-1|

    RNDEATHST      Rate of N loss in roots                          |kg N ha-1 d-1|
    RPDEATHST      as for P                                         |kg P ha-1 d-1|
    RKDEATHST      as for K                                         |kg K ha-1 d-1|

    RNDEATHRT      Rate of N loss in stems                          |kg N ha-1 d-1|
    RPDEATHRT      as for P                                         |kg P ha-1 d-1|
    RKDEATHRT      as for K                                         |kg K ha-1 d-1|

    RNLOSS         N loss due to senescence                         |kg N ha-1 d-1|
    RPLOSS         P loss due to senescence                         |kg P ha-1 d-1|
    RKLOSS         K loss due to senescence                         |kg K ha-1 d-1|
    ===========  =================================================  ================
    
    **Signals send or handled**
    
    None
    
    **External dependencies**
    
    =======  =================================== ====================  ==============
     Name     Description                         Provided by            Unit
    =======  =================================== ====================  ==============
    DVS      Crop development stage              DVS_Phenology           -
    WLV      Dry weight of living leaves         WOFOST_Leaf_Dynamics  |kg ha-1|
    WRT      Dry weight of living roots          WOFOST_Root_Dynamics  |kg ha-1|
    WST      Dry weight of living stems          WOFOST_Stem_Dynamics  |kg ha-1|
    DRLV     Death rate of leaves                WOFOST_Leaf_Dynamics  |kg ha-1 d-1|
    DRRT     Death rate of roots                 WOFOST_Root_Dynamics  |kg ha-1 d-1|
    DRST     Death rate of stems                 WOFOST_Stem_Dynamics  |kg ha-1 d-1|
    =======  =================================== ====================  ==============
    """

    translocation = Instance(SimulationObject)
    demand_uptake = Instance(SimulationObject)

    NAMOUNTLVI = Float(-99.)  # initial soil N amount in leaves
    NAMOUNTSTI = Float(-99.)  # initial soil N amount in stems
    NAMOUNTRTI = Float(-99.)  # initial soil N amount in roots
    NAMOUNTSOI = Float(-99.)  # initial soil N amount in storage organs
    
    PAMOUNTLVI = Float(-99.)  # initial soil P amount in leaves
    PAMOUNTSTI = Float(-99.)  # initial soil P amount in stems
    PAMOUNTRTI = Float(-99.)  # initial soil P amount in roots
    PAMOUNTSOI = Float(-99.)  # initial soil P amount in storage organs

    KAMOUNTLVI = Float(-99.)  # initial soil K amount in leaves
    KAMOUNTSTI = Float(-99.)  # initial soil K amount in stems
    KAMOUNTRTI = Float(-99.)  # initial soil K amount in roots
    KAMOUNTSOI = Float(-99.)  # initial soil K amount in storage organs

    class Parameters(ParamTemplate):
        NMAXLV_TB = AfgenTrait()
        PMAXLV_TB = AfgenTrait()
        KMAXLV_TB = AfgenTrait()
        NMAXST_FR = Float(-99.)
        NMAXRT_FR = Float(-99.)
        PMAXST_FR = Float(-99.)
        PMAXRT_FR = Float(-99.)
        KMAXST_FR = Float(-99.)
        KMAXRT_FR = Float(-99.)
        NRESIDLV = Float(-99.)  # residual N fraction in leaves [kg N kg-1 dry biomass]
        NRESIDST = Float(-99.)  # residual N fraction in stems [kg N kg-1 dry biomass]
        NRESIDRT = Float(-99.)  # residual N fraction in roots [kg N kg-1 dry biomass]
        PRESIDLV = Float(-99.)  # residual P fraction in leaves [kg P kg-1 dry biomass]
        PRESIDST = Float(-99.)  # residual P fraction in stems [kg P kg-1 dry biomass]
        PRESIDRT = Float(-99.)  # residual P fraction in roots [kg P kg-1 dry biomass]
        KRESIDLV = Float(-99.)  # residual K fraction in leaves [kg K kg-1 dry biomass]
        KRESIDST = Float(-99.)  # residual K fraction in stems [kg K kg-1 dry biomass]
        KRESIDRT = Float(-99.)  # residual K fraction in roots [kg K kg-1 dry biomass]

    class StateVariables(StatesTemplate):
        NAMOUNTLV = Float(-99.) # N amount in leaves [kg N ha-1]
        PAMOUNTLV = Float(-99.) # P amount in leaves [kg P ]
        KAMOUNTLV = Float(-99.) # K amount in leaves [kg K ]
        
        NAMOUNTST = Float(-99.) # N amount in stems [kg N ]
        PAMOUNTST = Float(-99.) # P amount in stems [kg P ]
        KAMOUNTST = Float(-99.) # K amount in stems [kg K ]
      
        NAMOUNTSO = Float(-99.) # N amount in storage organs [kg N ]
        PAMOUNTSO = Float(-99.) # P amount in storage organs [kg P ]
        KAMOUNTSO = Float(-99.) # K amount in storage organs [kg K ]
        
        NAMOUNTRT = Float(-99.) # N amount in roots [kg N ]
        PAMOUNTRT = Float(-99.) # P amount in roots [kg P ]
        KAMOUNTRT = Float(-99.) # K amount in roots [kg K ]
        
        NUPTAKETOTAL = Float(-99.) # total absorbed N amount [kg N ]
        PUPTAKETOTAL = Float(-99.) # total absorbed P amount [kg P ]
        KUPTAKETOTAL = Float(-99.) # total absorbed K amount [kg K ]
        NFIXTOTAL = Float(-99.) # total biological fixated N amount [kg N ]
        
        NlossesTotal = Float(-99.)
        PlossesTotal = Float(-99.)
        KlossesTotal = Float(-99.)

    class RateVariables(RatesTemplate):
        RNAMOUNTLV = Float(-99.)  # Net rates of NPK in different plant organs 
        RPAMOUNTLV = Float(-99.)
        RKAMOUNTLV = Float(-99.)
        
        RNAMOUNTST = Float(-99.)
        RPAMOUNTST = Float(-99.)
        RKAMOUNTST = Float(-99.)
               
        RNAMOUNTRT = Float(-99.)
        RPAMOUNTRT = Float(-99.)
        RKAMOUNTRT = Float(-99.)
        
        RNAMOUNTSO = Float(-99.)
        RPAMOUNTSO = Float(-99.)
        RKAMOUNTSO = Float(-99.)
               
        RNDEATHLV = Float(-99.)  # N loss rate leaves [kg ha-1 d-1]
        RNDEATHST = Float(-99.)  # N loss rate stems  [kg ha-1 d-1]
        RNDEATHRT = Float(-99.)  # N loss rate roots  [kg ha-1 d-1]
        
        RPDEATHLV = Float(-99.)  # P loss rate leaves [kg ha-1 d-1]
        RPDEATHST = Float(-99.)  # P loss rate stems  [kg ha-1 d-1]
        RPDEATHRT = Float(-99.)  # P loss rate roots  [kg ha-1 d-1]
        
        RKDEATHLV = Float(-99.)  # K loss rate leaves [kg ha-1 d-1]
        RKDEATHST = Float(-99.)  # K loss rate stems  [kg ha-1 d-1]
        RKDEATHRT = Float(-99.)  # K loss rate roots  [kg ha-1 d-1]

        RNLOSS = Float(-99.)
        RPLOSS = Float(-99.)
        RKLOSS = Float(-99.)
        
    def initialize(self, day:date, kiosk:VariableKiosk, parvalues:dict):
        """
        :param day: current day
        :param kiosk: variable kiosk of this PCSE instance
        :param parvalues: dictionary with parameters as key/value pairs
        """  
        
        self.params = self.Parameters(parvalues)
        self.kiosk = kiosk
        
        # Initialize components of the npk_crop_dynamics
        self.translocation = NPK_Translocation(day, kiosk, parvalues)
        self.demand_uptake = NPK_Demand_Uptake(day, kiosk, parvalues)

        # INITIAL STATES
        params = self.params
        k = kiosk

        # Initial amounts
        self.NAMOUNTLVI = NAMOUNTLV = k.WLV * params.NMAXLV_TB(k.DVS)
        self.NAMOUNTSTI = NAMOUNTST = k.WST * params.NMAXLV_TB(k.DVS) * params.NMAXST_FR
        self.NAMOUNTRTI = NAMOUNTRT = k.WRT * params.NMAXLV_TB(k.DVS) * params.NMAXRT_FR
        self.NAMOUNTSOI = NAMOUNTSO = 0.
        
        self.PAMOUNTLVI = PAMOUNTLV = k.WLV * params.PMAXLV_TB(k.DVS)
        self.PAMOUNTSTI = PAMOUNTST = k.WST * params.PMAXLV_TB(k.DVS) * params.PMAXST_FR
        self.PAMOUNTRTI = PAMOUNTRT = k.WRT * params.PMAXLV_TB(k.DVS) * params.PMAXRT_FR
        self.PAMOUNTSOI = PAMOUNTSO = 0.

        self.KAMOUNTLVI = KAMOUNTLV = k.WLV * params.KMAXLV_TB(k.DVS)
        self.KAMOUNTSTI = KAMOUNTST = k.WST * params.KMAXLV_TB(k.DVS) * params.KMAXST_FR
        self.KAMOUNTRTI = KAMOUNTRT = k.WRT * params.KMAXLV_TB(k.DVS) * params.KMAXRT_FR
        self.KAMOUNTSOI = KAMOUNTSO = 0.

        self.states = self.StateVariables(kiosk,
            publish=["NAMOUNTLV", "PAMOUNTLV", "KAMOUNTLV", "NAMOUNTST", "PAMOUNTST", 
                     "KAMOUNTST", "NAMOUNTSO", "PAMOUNTSO", "KAMOUNTSO", "NAMOUNTRT", 
                     "PAMOUNTRT", "KAMOUNTRT","NUPTAKETOTAL", "PUPTAKETOTAL", "KUPTAKETOTAL", 
                     "NFIXTOTAL", "NlossesTotal", "PlossesTotal", "KlossesTotal"],
                        NAMOUNTLV=NAMOUNTLV, NAMOUNTST=NAMOUNTST, NAMOUNTRT=NAMOUNTRT, NAMOUNTSO=NAMOUNTSO,
                        PAMOUNTLV=PAMOUNTLV, PAMOUNTST=PAMOUNTST, PAMOUNTRT=PAMOUNTRT, PAMOUNTSO=PAMOUNTSO,
                        KAMOUNTLV=KAMOUNTLV, KAMOUNTST=KAMOUNTST, KAMOUNTRT=KAMOUNTRT, KAMOUNTSO=KAMOUNTSO,
                        NUPTAKETOTAL=0, PUPTAKETOTAL=0., KUPTAKETOTAL=0., NFIXTOTAL=0.,
                        NlossesTotal=0, PlossesTotal=0., KlossesTotal=0.)
        
        self.rates = self.RateVariables(kiosk,
            publish=["RNAMOUNTLV", "RPAMOUNTLV", "RKAMOUNTLV", "RNAMOUNTST", 
                     "RPAMOUNTST", "RKAMOUNTST", "RNAMOUNTRT", "RPAMOUNTRT",  
                     "RKAMOUNTRT", "RNAMOUNTSO", "RPAMOUNTSO", "RKAMOUNTSO", 
                     "RNDEATHLV", "RNDEATHST", "RNDEATHRT", "RPDEATHLV", "RPDEATHST", 
                     "RPDEATHRT", "RKDEATHLV","RKDEATHST", "RKDEATHRT", "RNLOSS", 
                     "RPLOSS", "RKLOSS"])

    @prepare_rates
    def calc_rates(self, day:date, drv:WeatherDataProvider):
        """Calculate state rates
        """
        rates = self.rates
        params = self.params
        k = self.kiosk
        
        self.demand_uptake.calc_rates(day, drv)
        self.translocation.calc_rates(day, drv)

        # Compute loss of NPK due to death of plant material
        rates.RNDEATHLV = params.NRESIDLV * k.DRLV
        rates.RNDEATHST = params.NRESIDST * k.DRST
        rates.RNDEATHRT = params.NRESIDRT * k.DRRT

        rates.RPDEATHLV = params.PRESIDLV * k.DRLV
        rates.RPDEATHST = params.PRESIDST * k.DRST
        rates.RPDEATHRT = params.PRESIDRT * k.DRRT

        rates.RKDEATHLV = params.KRESIDLV * k.DRLV
        rates.RKDEATHST = params.KRESIDST * k.DRST
        rates.RKDEATHRT = params.KRESIDRT * k.DRRT

        # N rates in leaves, stems, root and storage organs computed as
        # uptake - translocation - death.
        # except for storage organs which only take up as a result of translocation.
        rates.RNAMOUNTLV = k.RNUPTAKELV - k.RNTRANSLOCATIONLV - rates.RNDEATHLV
        rates.RNAMOUNTST = k.RNUPTAKEST - k.RNTRANSLOCATIONST - rates.RNDEATHST
        rates.RNAMOUNTRT = k.RNUPTAKERT - k.RNTRANSLOCATIONRT - rates.RNDEATHRT
        rates.RNAMOUNTSO = k.RNUPTAKESO
        
        # P rates in leaves, stems, root and storage organs
        rates.RPAMOUNTLV = k.RPUPTAKELV - k.RPTRANSLOCATIONLV - rates.RPDEATHLV
        rates.RPAMOUNTST = k.RPUPTAKEST - k.RPTRANSLOCATIONST - rates.RPDEATHST
        rates.RPAMOUNTRT = k.RPUPTAKERT - k.RPTRANSLOCATIONRT - rates.RPDEATHRT
        rates.RPAMOUNTSO = k.RPUPTAKESO

        # K rates in leaves, stems, root and storage organs
        rates.RKAMOUNTLV = k.RKUPTAKELV - k.RKTRANSLOCATIONLV - rates.RKDEATHLV
        rates.RKAMOUNTST = k.RKUPTAKEST - k.RKTRANSLOCATIONST - rates.RKDEATHST
        rates.RKAMOUNTRT = k.RKUPTAKERT - k.RKTRANSLOCATIONRT - rates.RKDEATHRT
        rates.RKAMOUNTSO = k.RKUPTAKESO
        
        rates.RNLOSS = rates.RNDEATHLV + rates.RNDEATHST + rates.RNDEATHRT
        rates.RPLOSS = rates.RPDEATHLV + rates.RPDEATHST + rates.RPDEATHRT
        rates.RKLOSS = rates.RKDEATHLV + rates.RKDEATHST + rates.RKDEATHRT

        self._check_N_balance(day)
        self._check_P_balance(day)
        self._check_K_balance(day)
        
    @prepare_states
    def integrate(self, day:date, delt:float=1.0):
        """Integrate state rates
        """
        rates = self.rates
        states = self.states
        k = self.kiosk

        # N amount in leaves, stems, root and storage organs
        states.NAMOUNTLV += rates.RNAMOUNTLV
        states.NAMOUNTST += rates.RNAMOUNTST
        states.NAMOUNTRT += rates.RNAMOUNTRT
        states.NAMOUNTSO += rates.RNAMOUNTSO
        
        # P amount in leaves, stems, root and storage organs
        states.PAMOUNTLV += rates.RPAMOUNTLV
        states.PAMOUNTST += rates.RPAMOUNTST
        states.PAMOUNTRT += rates.RPAMOUNTRT
        states.PAMOUNTSO += rates.RPAMOUNTSO

        # K amount in leaves, stems, root and storage organs
        states.KAMOUNTLV += rates.RKAMOUNTLV
        states.KAMOUNTST += rates.RKAMOUNTST
        states.KAMOUNTRT += rates.RKAMOUNTRT
        states.KAMOUNTSO += rates.RKAMOUNTSO
        
        self.translocation.integrate(day, delt)
        self.demand_uptake.integrate(day, delt)

        # total NPK uptake from soil
        states.NUPTAKETOTAL += k.RNUPTAKE
        states.PUPTAKETOTAL += k.RPUPTAKE
        states.KUPTAKETOTAL += k.RKUPTAKE
        states.NFIXTOTAL += k.RNFIXATION
        
        states.NlossesTotal += rates.RNLOSS
        states.PlossesTotal += rates.RPLOSS
        states.KlossesTotal += rates.RKLOSS

    def _check_N_balance(self, day:date):
        """Check the Nitrogen balance is valid"""
        s = self.states
        checksum = abs(s.NUPTAKETOTAL + s.NFIXTOTAL +
                       (self.NAMOUNTLVI + self.NAMOUNTSTI + self.NAMOUNTRTI + self.NAMOUNTSOI) -
                       (s.NAMOUNTLV + s.NAMOUNTST + s.NAMOUNTRT + s.NAMOUNTSO + s.NlossesTotal))

        if abs(checksum) >= 1.0:
            msg = "N flows not balanced on day %s\n" % day
            msg += "Checksum: %f, NUPTAKE_T: %f, NFIX_T: %f\n" % (checksum, s.NUPTAKETOTAL, s.NFIXTOTAL)
            msg += "NAMOUNTLVI: %f, NAMOUNTSTI: %f, NAMOUNTRTI: %f, NAMOUNTSOI: %f\n"  % \
                   (self.NAMOUNTLVI, self.NAMOUNTSTI, self.NAMOUNTRTI, self.NAMOUNTSOI)
            msg += "NAMOUNTLV: %f, NAMOUNTST: %f, NAMOUNTRT: %f, NAMOUNTSO: %f\n" % \
                   (s.NAMOUNTLV, s.NAMOUNTST, s.NAMOUNTRT, s.NAMOUNTSO)
            msg += "NLOSST: %f\n" % (s.NlossesTotal)
            raise exc.NutrientBalanceError(msg)

    def _check_P_balance(self, day:date):
        """Check that the Phosphorous balance is valid"""
        s = self.states
        checksum = abs(s.PUPTAKETOTAL +
                       (self.PAMOUNTLVI + self.PAMOUNTSTI + self.PAMOUNTRTI + self.PAMOUNTSOI) -
                       (s.PAMOUNTLV + s.PAMOUNTST + s.PAMOUNTRT + s.PAMOUNTSO + s.PlossesTotal))

        if abs(checksum) >= 1.:
            msg = "P flows not balanced on day %s\n" % day
            msg += "Checksum: %f, PUPTAKE_T: %f\n" % (checksum, s.PUPTAKETOTAL)
            msg += "PAMOUNTLVI: %f, PAMOUNTSTI: %f, PAMOUNTRTI: %f, PAMOUNTSOI: %f\n" % \
                   (self.PAMOUNTLVI, self.PAMOUNTSTI, self.PAMOUNTRTI, self.PAMOUNTSOI)
            msg += "PAMOUNTLV: %f, PAMOUNTST: %f, PAMOUNTRT: %f, PAMOUNTSO: %f\n" % \
                   (s.PAMOUNTLV, s.PAMOUNTST, s.PAMOUNTRT, s.PAMOUNTSO)
            msg += "PLOSST: %f\n" % (s.PlossesTotal)
            raise exc.NutrientBalanceError(msg)

    def _check_K_balance(self, day:date):
        """Check that the Potassium balance is valid"""
        s = self.states
        checksum = abs(s.KUPTAKETOTAL +
                       (self.KAMOUNTLVI + self.KAMOUNTSTI + self.KAMOUNTRTI + self.KAMOUNTSOI) -
                       (s.KAMOUNTLV + s.KAMOUNTST + s.KAMOUNTRT + s.KAMOUNTSO + s.KlossesTotal))

        if abs(checksum) >= 1.:
            msg = "K flows not balanced on day %s\n" % day
            msg += "Checksum: %f, KUPTAKE_T: %f\n"  % (checksum, s.KUPTAKETOTAL)
            msg += "KAMOUNTLVI: %f, KAMOUNTSTI: %f, KAMOUNTRTI: %f, KAMOUNTSOI: %f\n" % \
                   (self.KAMOUNTLVI, self.KAMOUNTSTI, self.KAMOUNTRTI, self.KAMOUNTSOI)
            msg += "KAMOUNTLV: %f, KAMOUNTST: %f, KAMOUNTRT: %f, KAMOUNTSO: %f\n" % \
                   (s.KAMOUNTLV, s.KAMOUNTST, s.KAMOUNTRT, s.KAMOUNTSO)
            msg += "KLOSST: %f\n" % (s.KlossesTotal)
            raise exc.NutrientBalanceError(msg)

    def reset(self):
        """Reset states and rates
        """

        # Initialize components of the npk_crop_dynamics
        self.translocation.reset()
        self.demand_uptake.reset()

        # INITIAL STATES
        params = self.params
        k = self.kiosk
        s = self.states
        r = self.rates

        # Initial amounts
        self.NAMOUNTLVI = NAMOUNTLV = k.WLV * params.NMAXLV_TB(k.DVS)
        self.NAMOUNTSTI = NAMOUNTST = k.WST * params.NMAXLV_TB(k.DVS) * params.NMAXST_FR
        self.NAMOUNTRTI = NAMOUNTRT = k.WRT * params.NMAXLV_TB(k.DVS) * params.NMAXRT_FR
        self.NAMOUNTSOI = NAMOUNTSO = 0.
        
        self.PAMOUNTLVI = PAMOUNTLV = k.WLV * params.PMAXLV_TB(k.DVS)
        self.PAMOUNTSTI = PAMOUNTST = k.WST * params.PMAXLV_TB(k.DVS) * params.PMAXST_FR
        self.PAMOUNTRTI = PAMOUNTRT = k.WRT * params.PMAXLV_TB(k.DVS) * params.PMAXRT_FR
        self.PAMOUNTSOI = PAMOUNTSO = 0.

        self.KAMOUNTLVI = KAMOUNTLV = k.WLV * params.KMAXLV_TB(k.DVS)
        self.KAMOUNTSTI = KAMOUNTST = k.WST * params.KMAXLV_TB(k.DVS) * params.KMAXST_FR
        self.KAMOUNTRTI = KAMOUNTRT = k.WRT * params.KMAXLV_TB(k.DVS) * params.KMAXRT_FR
        self.KAMOUNTSOI = KAMOUNTSO = 0.

        s.NAMOUNTLV=NAMOUNTLV
        s.NAMOUNTST=NAMOUNTST
        s.NAMOUNTRT=NAMOUNTRT
        s.NAMOUNTSO=NAMOUNTSO
        s.PAMOUNTLV=PAMOUNTLV
        s.PAMOUNTST=PAMOUNTST
        s.PAMOUNTRT=PAMOUNTRT
        s.PAMOUNTSO=PAMOUNTSO
        s.KAMOUNTLV=KAMOUNTLV
        s.KAMOUNTST=KAMOUNTST
        s.KAMOUNTRT=KAMOUNTRT
        s.KAMOUNTSO=KAMOUNTSO
        s.NUPTAKETOTAL=0
        s.PUPTAKETOTAL=0.
        s.KUPTAKETOTAL=0.
        s.NFIXTOTAL=0.
        s.NlossesTotal=0
        s.PlossesTotal=0.
        s.KlossesTotal=0.

        r.RNAMOUNTLV = r.RPAMOUNTLV = r.RKAMOUNTLV = r.RNAMOUNTST = r.RPAMOUNTST \
            = r.RKAMOUNTST = r.RNAMOUNTRT = r.RPAMOUNTRT = r.RKAMOUNTRT = r.RNAMOUNTSO \
            = r.RPAMOUNTSO = r.RKAMOUNTSO = r.RNDEATHLV = r.RNDEATHST = r.RNDEATHRT \
            = r.RPDEATHLV = r.RPDEATHST = r.RPDEATHRT = r.RKDEATHLV = r.RKDEATHST \
            = r.RKDEATHRT = r.RNLOSS = r.RPLOSS = r.RKLOSS = 0
        
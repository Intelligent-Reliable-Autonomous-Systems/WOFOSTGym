"""Calculates NPK Demand for the crop and corresponding uptake from soil

Written by: Allard de Wit (allard.dewit@wur.nl), April 2014
Modified by Will Solow, 2024
"""
from datetime import date
from collections import namedtuple

from ...base import ParamTemplate, SimulationObject, RatesTemplate, VariableKiosk
from ...utils.decorators import prepare_rates, prepare_states
from ...utils.traitlets import Float
from ...util import AfgenTrait
from ...nasapower import WeatherDataProvider

MaxNutrientConcentrations = namedtuple("MaxNutrientConcentrations",
                                       ["NMAXLV", "PMAXLV", "KMAXLV",
                                        "NMAXST", "PMAXST", "KMAXST",
                                        "NMAXRT", "PMAXRT", "KMAXRT",
                                        "NMAXSO", "PMAXSO", "KMAXSO"])

class NPK_Demand_Uptake(SimulationObject):
    """Calculates the crop N/P/K demand and its uptake from the soil.

    Crop N/P/K demand is calculated as the difference between the
    actual N/P/K concentration (kg N/P/K per kg biomass) in the
    vegetative plant organs (leaves, stems and roots) and the maximum
    N/P/K concentration for each organ. N/P/K uptake is then estimated
    as the minimum of supply from the soil and demand from the crop.

    Nitrogen fixation (leguminous plants) is calculated by assuming that a
    fixed fraction of the daily N demand is supplied by nitrogen fixation.
    The remaining part has to be supplied by the soil.

    The N/P/K demand of the storage organs is calculated in a somewhat
    different way because it is assumed that the demand from the storage
    organs is fulfilled by translocation of N/P/K from the leaves, stems
    and roots. So Therefore the uptake of the storage organs is calculated
    as the minimum of the translocatable N/P/K (supply) and the demand from
    the storage organs. Moreover, there is time coefficient for translocation
    which takes into account that there is a delay in the availability of
    translocatable N/P/K

    **Simulation parameters**

    ============  =============================================  ======================
     Name          Description                                    Unit
    ============  =============================================  ======================
    NMAXLV_TB      Maximum N concentration in leaves as          kg N kg-1 dry biomass
                   function of DVS
    PMAXLV_TB      As for P                                      kg P kg-1 dry biomass
    KMAXLV_TB      As for K                                      kg K kg-1 dry biomass

    NMAXRT_FR      Maximum N concentration in roots as fraction  -
                   of maximum N concentration in leaves
    PMAXRT_FR      As for P                                      -
    KMAXRT_FR      As for K                                      -

    NMAXST_FR      Maximum N concentration in stems as fraction  -
                   of maximum N concentration in leaves
    PMAXST_FR      As for P                                      -
    KMAXST_FR      As for K                                      -

    NMAXSO         Maximum N concentration in storage organs     kg N kg-1 dry biomass
    PMAXSO         As for P                                      kg P kg-1 dry biomass
    KMAXSO         As for K                                      kg K kg-1 dry biomass

    NCRIT_FR       Critical N concentration as fraction of       -
                   maximum N concentration for vegetative
                   plant organs as a whole (leaves + stems)
    PCRIT_FR       As for P                                      -
    KCRIT_FR       As for K                                      -

    TCNT           Time coefficient for N translation to         days
                   storage organs
    TCPT           As for P                                      days
    TCKT           As for K                                      days

    NFIX_FR        fraction of crop nitrogen uptake by           kg N kg-1 dry biomass
                   biological fixation
    RNUPTAKEMAX    Maximum rate of N uptake                      |kg N ha-1 d-1|
    RPUPTAKEMAX    Maximum rate of P uptake                      |kg N ha-1 d-1|
    RKUPTAKEMAX    Maximum rate of K uptake                      |kg N ha-1 d-1|
    DVS_NPK_STOP   DVS above which NPK uptake halts               - 
    ============  =============================================  ======================

    **State variables**

    =============  ================================================= ==== ============
     Name           Description                                      Pbl      Unit
    =============  ================================================= ==== ============
    NUPTAKETOTAL     Total N uptake by the crop                        N   |kg N ha-1|
    PUPTAKETOTAL     Total P uptake by the crop                        N   |kg N ha-1|
    KUPTAKETOTAL     Total K uptake by the crop                        N   |kg N ha-1|
    NFIXTOTAL      Total N fixated by the crop                         N   |kg N ha-1|

    NDEMANDST     N Demand in living stems                          N   |kg N ha-1|
    NDEMANDRT     N Demand in living roots                          N   |kg N ha-1|
    NDEMANDSO     N Demand in storage organs                        N   |kg N ha-1|

    PDEMANDLV     P Demand in living leaves                         N   |kg P ha-1|
    PDEMANDST     P Demand in living stems                          N   |kg P ha-1|
    PDEMANDRT     P Demand in living roots                          N   |kg P ha-1|
    PDEMANDSO     P Demand in storage organs                        N   |kg P ha-1|

    KDEMANDLV     K Demand in living leaves                         N   |kg K ha-1|
    KDEMANDST     K Demand in living stems                          N   |kg K ha-1|
    KDEMANDRT     K Demand in living roots                          N   |kg K ha-1|
    KDEMANDSO     K Demand in storage organs                        N   |kg K ha-1|
    ==========  ================================================= ==== ============


    **Rate variables**

    ===========  ================================================= ==== ================
     Name         Description                                      Pbl      Unit
    ===========  ================================================= ==== ================
    RNUPTAKELV     Rate of N uptake in leaves                        Y   |kg N ha-1 d-1|
    RNUPTAKEST     Rate of N uptake in stems                         Y   |kg N ha-1 d-1|
    RNUPTAKERT     Rate of N uptake in roots                         Y   |kg N ha-1 d-1|
    RNUPTAKESO     Rate of N uptake in storage organs                Y   |kg N ha-1 d-1|

    RPUPTAKELV     Rate of P uptake in leaves                        Y   |kg P ha-1 d-1|
    RPUPTAKEST     Rate of P uptake in stems                         Y   |kg P ha-1 d-1|
    RPUPTAKERT     Rate of P uptake in roots                         Y   |kg P ha-1 d-1|
    RPUPTAKESO     Rate of P uptake in storage organs                Y   |kg P ha-1 d-1|

    RKUPTAKELV     Rate of K uptake in leaves                        Y   |kg K ha-1 d-1|
    RKUPTAKEST     Rate of K uptake in stems                         Y   |kg K ha-1 d-1|
    RKUPTAKERT     Rate of K uptake in roots                         Y   |kg K ha-1 d-1|
    RKUPTAKESO     Rate of K uptake in storage organs                Y   |kg K ha-1 d-1|

    RNUPTAKE       Total rate of N uptake                            Y   |kg N ha-1 d-1|
    RPUPTAKE       Total rate of P uptake                            Y   |kg P ha-1 d-1|
    RKUPTAKE       Total rate of K uptake                            Y   |kg K ha-1 d-1|
    RNFIXATION     Rate of N fixation                                Y   |kg N ha-1 d-1|

    NDEMANDLV      N Demand in living leaves                         N   |kg N ha-1|
    NDEMANDST      N Demand in living stems                          N   |kg N ha-1|
    NDEMANDRT      N Demand in living roots                          N   |kg N ha-1|
    NDEMANDSO      N Demand in storage organs                        N   |kg N ha-1|

    PDEMANDLV      P Demand in living leaves                         N   |kg P ha-1|
    PDEMANDST      P Demand in living stems                          N   |kg P ha-1|
    PDEMANDRT      P Demand in living roots                          N   |kg P ha-1|
    PDEMANDSO      P Demand in storage organs                        N   |kg P ha-1|

    KDEMANDLV      K Demand in living leaves                         N   |kg K ha-1|
    KDEMANDST      K Demand in living stems                          N   |kg K ha-1|
    KDEMANDRT      K Demand in living roots                          N   |kg K ha-1|
    KDEMANDSO      K Demand in storage organs                        N   |kg K ha-1|

    NDEMAND        Total crop N demand                               N   |kg N ha-1 d-1|
    PDEMAND        Total crop P demand                               N   |kg P ha-1 d-1|
    KDEMAND        Total crop K demand                               N   |kg K ha-1 d-1|
    ===========  ================================================= ==== ================

    **Signals send or handled**

    None

    **External dependencies**

    ================  =================================== ====================  ===========
     Name              Description                         Provided by            Unit
    ================  =================================== ====================  ===========
    DVS               Crop development stage              DVS_Phenology              -
    TRA               Crop transpiration                  Evapotranspiration     |cm d-1|
    TRAMX             Potential crop transpiration        Evapotranspiration     |cm d-1|
    NAVAIL            Total available N from soil         NPK_Soil_Dynamics      |kg ha-1|
    PAVAIL            Total available P from soil         NPK_Soil_Dynamics      |kg ha-1|
    KAVAIL            Total available K from soil         NPK_Soil_Dynamics      |kg ha-1|
    NTRANSLOCATABLE   Translocatable amount of N from     NPK_Translocation      |kg ha-1|
                      stems, Leaves and roots
    PTRANSLOCATABLE   As for P                            NPK_Translocation      |kg ha-1|
    KTRANSLOCATABLE   As for K                            NPK_Translocation      |kg ha-1|
    ================  =================================== ====================  ===========

    """

    class Parameters(ParamTemplate):
        NMAXLV_TB = AfgenTrait()  # maximum N concentration in leaves as function of dvs
        PMAXLV_TB = AfgenTrait()  # maximum P concentration in leaves as function of dvs
        KMAXLV_TB = AfgenTrait()  # maximum P concentration in leaves as function of dvs
        
        NMAXRT_FR = Float(-99.)  # maximum N concentration in roots as fraction of maximum N concentration in leaves
        PMAXRT_FR = Float(-99.)  # maximum P concentration in roots as fraction of maximum P concentration in leaves
        KMAXRT_FR = Float(-99.)  # maximum K concentration in roots as fraction of maximum K concentration in leaves

        NMAXST_FR = Float(-99.)  # maximum N concentration in stems as fraction of maximum N concentration in leaves
        PMAXST_FR = Float(-99.)  # maximum P concentration in stems as fraction of maximum P concentration in leaves
        KMAXST_FR = Float(-99.)  # maximum K concentration in stems as fraction of maximum K concentration in leaves
        
        NMAXSO = Float(-99.)  # maximum P concentration in storage organs [kg N kg-1 dry biomass]
        PMAXSO = Float(-99.)  # maximum P concentration in storage organs [kg P kg-1 dry biomass]
        KMAXSO = Float(-99.)  # maximum K concentration in storage organs [kg K kg-1 dry biomass]
        
        TCNT = Float(-99.)  # time coefficient for N translocation to storage organs [days]
        TCPT = Float(-99.)  # time coefficient for P translocation to storage organs [days]
        TCKT = Float(-99.)  # time coefficient for K translocation to storage organs [days]

        NFIX_FR = Float(-99.)  # fraction of crop nitrogen uptake by biological fixation
        RNUPTAKEMAX = Float()  # Maximum N uptake rate
        RPUPTAKEMAX = Float()  # Maximum P uptake rate
        RKUPTAKEMAX = Float()  # Maximum K uptake rate

        DVS_NPK_STOP = Float(-99.)

    class RateVariables(RatesTemplate):
        RNUPTAKELV = Float(-99.)  # N uptake rates in organs [kg ha-1 d -1]
        RNUPTAKEST = Float(-99.)
        RNUPTAKERT = Float(-99.)
        RNUPTAKESO = Float(-99.)

        RPUPTAKELV = Float(-99.)  # P uptake rates in organs [kg ha-1 d -1]
        RPUPTAKEST = Float(-99.)
        RPUPTAKERT = Float(-99.)
        RPUPTAKESO = Float(-99.)

        RKUPTAKELV = Float(-99.)  # K uptake rates in organs [kg ha-1 d -1]
        RKUPTAKEST = Float(-99.)
        RKUPTAKERT = Float(-99.)
        RKUPTAKESO = Float(-99.)

        RNUPTAKE = Float(-99.)  # Total N uptake rates [kg ha-1 d -1]
        RPUPTAKE = Float(-99.)  # For P
        RKUPTAKE = Float(-99.)  # For K
        RNFIXATION = Float(-99.)  # Total N fixated

        NDEMANDLV = Float(-99.)  # N demand in organs [kg ha-1]
        NDEMANDST = Float(-99.)
        NDEMANDRT = Float(-99.)
        NDEMANDSO = Float(-99.)

        PDEMANDLV = Float(-99.)  # P demand in organs [kg ha-1]
        PDEMANDST = Float(-99.)
        PDEMANDRT = Float(-99.)
        PDEMANDSO = Float(-99.)

        KDEMANDLV = Float(-99.)  # K demand in organs [kg ha-1]
        KDEMANDST = Float(-99.)
        KDEMANDRT = Float(-99.)
        KDEMANDSO = Float(-99.)

        NDEMAND = Float()  # Total N/P/K demand of the crop
        PDEMAND = Float()
        KDEMAND = Float()

    def initialize(self, day:date, kiosk:VariableKiosk, parvalues:dict):
        """
        :param day: start date of the simulation
        :param kiosk: variable kiosk of this PCSE instance
        :param parvalues: a ParameterProvider with parameter key/value pairs
        """

        self.params = self.Parameters(parvalues)
        self.kiosk = kiosk

        self.rates = self.RateVariables(kiosk,
            publish=["RNUPTAKELV", "RNUPTAKEST", "RNUPTAKERT", "RNUPTAKESO", 
                     "RPUPTAKELV", "RPUPTAKEST", "RPUPTAKERT", "RPUPTAKESO", 
                     "RKUPTAKELV", "RKUPTAKEST", "RKUPTAKERT", "RKUPTAKESO", 
                     "RNUPTAKE", "RPUPTAKE", "RKUPTAKE", "RNFIXATION",
                     "NDEMANDLV", "NDEMANDST", "NDEMANDRT", "NDEMANDSO", 
                     "PDEMANDLV", "PDEMANDST", "PDEMANDRT", "PDEMANDSO", 
                     "KDEMANDLV", "KDEMANDST", "KDEMANDRT","KDEMANDSO", 
                     "NDEMAND", "PDEMAND", "KDEMAND", ])

    @prepare_rates
    def calc_rates(self, day:date, drv:WeatherDataProvider):
        """Calculate rates
        """
        r = self.rates
        p = self.params
        k = self.kiosk

        delt = 1.0
        mc = self._compute_NPK_max_concentrations()

        # Total NPK demand of leaves, stems, roots and storage organs
        # Demand consists of a demand carried over from previous timesteps plus a demand from new growth
        # Note that we are pre-integrating here, so a multiplication with time-step delt is required

        # N demand [kg ha-1]
        r.NDEMANDLV = max(mc.NMAXLV * k.WLV - k.NAMOUNTLV, 0.) + max(k.GRLV * mc.NMAXLV, 0) * delt
        r.NDEMANDST = max(mc.NMAXST * k.WST - k.NAMOUNTST, 0.) + max(k.GRST * mc.NMAXST, 0) * delt
        r.NDEMANDRT = max(mc.NMAXRT * k.WRT - k.NAMOUNTRT, 0.) + max(k.GRRT * mc.NMAXRT, 0) * delt
        r.NDEMANDSO = max(mc.NMAXSO * k.WSO - k.NAMOUNTSO, 0.)

        # P demand [kg ha-1]
        r.PDEMANDLV = max(mc.PMAXLV * k.WLV - k.PAMOUNTLV, 0.) + max(k.GRLV * mc.PMAXLV, 0) * delt
        r.PDEMANDST = max(mc.PMAXST * k.WST - k.PAMOUNTST, 0.) + max(k.GRST * mc.PMAXST, 0) * delt
        r.PDEMANDRT = max(mc.PMAXRT * k.WRT - k.PAMOUNTRT, 0.) + max(k.GRRT * mc.PMAXRT, 0) * delt
        r.PDEMANDSO = max(mc.PMAXSO * k.WSO - k.PAMOUNTSO, 0.)

        # K demand [kg ha-1]
        r.KDEMANDLV = max(mc.KMAXLV * k.WLV - k.KAMOUNTLV, 0.) + max(k.GRLV * mc.KMAXLV, 0) * delt
        r.KDEMANDST = max(mc.KMAXST * k.WST - k.KAMOUNTST, 0.) + max(k.GRST * mc.KMAXST, 0) * delt
        r.KDEMANDRT = max(mc.KMAXRT * k.WRT - k.KAMOUNTRT, 0.) + max(k.GRRT * mc.KMAXRT, 0) * delt
        r.KDEMANDSO = max(mc.KMAXSO * k.WSO - k.KAMOUNTSO, 0.)

        r.NDEMAND = r.NDEMANDLV + r.NDEMANDST + r.NDEMANDRT
        r.PDEMAND = r.PDEMANDLV + r.PDEMANDST + r.PDEMANDRT
        r.KDEMAND = r.KDEMANDLV + r.KDEMANDST + r.KDEMANDRT

        # NPK uptake rate in storage organs (kg N ha-1 d-1) is the mimimum of supply and
        # demand divided by the time coefficient for N/P/K translocation
        r.RNUPTAKESO = min(r.NDEMANDSO, k.NTRANSLOCATABLE)/p.TCNT
        r.RPUPTAKESO = min(r.PDEMANDSO, k.PTRANSLOCATABLE)/p.TCPT
        r.RKUPTAKESO = min(r.KDEMANDSO, k.KTRANSLOCATABLE)/p.TCKT

        # No nutrients are absorbed when severe water shortage occurs i.e. RFTRA <= 0.01
        if k.RFTRA > 0.01:
            NutrientLIMIT = 1.0
        else:
            NutrientLIMIT = 0.

        # biological nitrogen fixation
        r.RNFIXATION = (max(0., p.NFIX_FR * r.NDEMAND) * NutrientLIMIT)

        # NPK uptake rate from soil
        if k.DVS < p.DVS_NPK_STOP:
            r.RNUPTAKE = (max(0., min(r.NDEMAND - r.RNFIXATION, k.NAVAIL, p.RNUPTAKEMAX)) * NutrientLIMIT)
            r.RPUPTAKE = (max(0., min(r.PDEMAND, k.PAVAIL, p.RPUPTAKEMAX)) * NutrientLIMIT)
            r.RKUPTAKE = (max(0., min(r.KDEMAND, k.KAVAIL, p.RKUPTAKEMAX)) * NutrientLIMIT)
        else:
            r.RNUPTAKE = r.RPUPTAKE = r.RKUPTAKE = 0

        # NPK uptake rate for different organs weighted as fraction of total demand
        # if no demand then uptake rate = 0.
        if r.NDEMAND == 0.:
            r.RNUPTAKELV = r.RNUPTAKEST = r.RNUPTAKERT = 0.
        else:
            r.RNUPTAKELV = (r.NDEMANDLV / r.NDEMAND) * (r.RNUPTAKE + r.RNFIXATION)
            r.RNUPTAKEST = (r.NDEMANDST / r.NDEMAND) * (r.RNUPTAKE + r.RNFIXATION)
            r.RNUPTAKERT = (r.NDEMANDRT / r.NDEMAND) * (r.RNUPTAKE + r.RNFIXATION)

        if r.PDEMAND == 0.:
            r.RPUPTAKELV = r.RPUPTAKEST = r.RPUPTAKERT = 0.
        else:
            r.RPUPTAKELV = (r.PDEMANDLV / r.PDEMAND) * r.RPUPTAKE
            r.RPUPTAKEST = (r.PDEMANDST / r.PDEMAND) * r.RPUPTAKE
            r.RPUPTAKERT = (r.PDEMANDRT / r.PDEMAND) * r.RPUPTAKE

        if r.KDEMAND == 0.:
            r.RKUPTAKELV = r.RKUPTAKEST = r.RKUPTAKERT = 0.
        else:
            r.RKUPTAKELV = (r.KDEMANDLV / r.KDEMAND) * r.RKUPTAKE
            r.RKUPTAKEST = (r.KDEMANDST / r.KDEMAND) * r.RKUPTAKE
            r.RKUPTAKERT = (r.KDEMANDRT / r.KDEMAND) * r.RKUPTAKE

    @prepare_states
    def integrate(self, day:date, delt:float=1.0):
        """Integrate states - no states to integrate in NPK Demand Uptake
        """
        pass

    def _compute_NPK_max_concentrations(self):
        """Computes the maximum N/P/K concentrations in leaves, stems, roots and storage organs.
        
        Note that max concentrations are first derived from the dilution curve for leaves. 
        Maximum concentrations for stems and roots are computed as a fraction of the 
        concentration for leaves. Maximum concentration for storage organs is directly taken from
        the parameters N/P/KMAXSO.
        """

        p = self.params
        k = self.kiosk
        NMAXLV = p.NMAXLV_TB(k.DVS)
        PMAXLV = p.PMAXLV_TB(k.DVS)
        KMAXLV = p.KMAXLV_TB(k.DVS)
        max_NPK_conc = MaxNutrientConcentrations(
            # Maximum NPK concentrations in leaves [kg N kg-1 DM]
            NMAXLV=NMAXLV,
            PMAXLV=PMAXLV,
            KMAXLV=KMAXLV,
            # Maximum NPK concentrations in stems and roots [kg N kg-1 DM]
            NMAXST=(p.NMAXST_FR * NMAXLV),
            NMAXRT=p.NMAXRT_FR * NMAXLV,
            NMAXSO=p.NMAXSO,

            PMAXST=p.PMAXST_FR * PMAXLV,
            PMAXRT=p.PMAXRT_FR * PMAXLV,
            PMAXSO=p.PMAXSO,

            KMAXST=p.KMAXST_FR * KMAXLV,
            KMAXRT=p.KMAXRT_FR * KMAXLV,
            KMAXSO=p.KMAXSO
        )

        return max_NPK_conc

    def reset(self):
        """Reset states and rates
        """
        r = self.rates
        r.RNUPTAKELV = r.RNUPTAKEST = r.RNUPTAKERT = r.RNUPTAKESO = r.RPUPTAKELV = \
                    r.RPUPTAKEST = r.RPUPTAKERT = r.RPUPTAKESO =  \
                    r.RKUPTAKELV = r.RKUPTAKEST = r.RKUPTAKERT = r.RKUPTAKESO =  \
                    r.RNUPTAKE = r.RPUPTAKE = r.RKUPTAKE = r.RNFIXATION = \
                    r.NDEMANDLV = r.NDEMANDST = r.NDEMANDRT = r.NDEMANDSO =  \
                    r.PDEMANDLV = r.PDEMANDST = r.PDEMANDRT = r.PDEMANDSO = \
                    r.KDEMANDLV = r.KDEMANDST = r.KDEMANDRT = r.KDEMANDSO =  \
                    r.NDEMAND = r.PDEMAND = r.KDEMAND = 0
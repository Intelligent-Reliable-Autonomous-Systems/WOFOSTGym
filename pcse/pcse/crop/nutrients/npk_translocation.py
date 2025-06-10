"""
Performs bookkeeping for how NPK is translocated around roots, leaves, and stems

Written by: Allard de Wit and Iwan Supi (allard.dewit@wur.nl), July 2015
Approach based on: LINTUL N/P/K made by Joost Wolf
Modified by Will Solow, 2024
"""

from datetime import date

from ...utils.traitlets import Float
from ...utils.decorators import prepare_rates, prepare_states
from ...base import ParamTemplate, StatesTemplate, RatesTemplate, \
    SimulationObject, VariableKiosk
from ...nasapower import WeatherDataProvider

class NPK_Translocation(SimulationObject):
    """Does the bookkeeping for translocation of N/P/K from the roots, leaves
    and stems towards the storage organs of the crop.

    First the routine calculates the state of the translocatable amount of N/P/K.
    This translocatable amount is defined as the amount of N/P/K above the
    residual N/P/K amount calculated as the residual concentration times the
    living biomass. The residual amount is locked into the plant structural biomass
    and cannot be mobilized anymore. The translocatable amount is calculated for
    stems, roots and leaves and published as the state variables
    NTRANSLOCATABLE, PTRANSLOCATABLE and KTRANSLOCATABLE.

    The overal translocation rate is calculated as the minimum of supply (the
    translocatable amount) and demand from the storage organs as calculated in
    the component on Demand_Uptake.
    The actual rate of N/P/K translocation from the different plant organs is
    calculated assuming that the uptake rate is distributed over roots, stems and
    leaves in proportion to the translocatable amount for each organ.

    **Simulation parameters**

    ===============  =============================================  ======================
     Name             Description                                    Unit
    ===============  =============================================  ======================
    NRESIDLV          Residual N fraction in leaves                 kg N kg-1 dry biomass
    PRESIDLV          Residual P fraction in leaves                 kg P kg-1 dry biomass
    KRESIDLV          Residual K fraction in leaves                 kg K kg-1 dry biomass

    NRESIDST          Residual N fraction in stems                  kg N kg-1 dry biomass
    PRESIDST          Residual P fraction in stems                  kg P kg-1 dry biomass
    KRESIDST          Residual K fraction in stems                  kg K kg-1 dry biomass

    NPK_TRANSLRT_FR   NPK translocation from roots as a fraction     -
                      of resp. total NPK amounts translocated
                      from leaves and stems
    DVS_NPK_TRANSL    DVS above which translocation to storage       -
                      organs begin
    ===============  =============================================  ======================


    **State variables**

    ===================  ================================================= ===== ============
     Name                  Description                                      Pbl      Unit
    ===================  ================================================= ===== ============
    NTRANSLOCATABLELV     Translocatable N amount in living leaves           N    |kg N ha-1|
    PTRANSLOCATABLELV     Translocatable P amount in living leaves           N    |kg P ha-1|
    KTRANSLOCATABLELV     Translocatable K amount in living leaves           N    |kg K ha-1|
    NTRANSLOCATABLEST     Translocatable N amount in living stems            N    |kg N ha-1|
    PTRANSLOCATABLEST     Translocatable P amount in living stems            N    |kg P ha-1|
    KTRANSLOCATABLEST     Translocatable K amount in living stems            N    |kg K ha-1|
    NTRANSLOCATABLERT     Translocatable N amount in living roots            N    |kg N ha-1|
    PTRANSLOCATABLERT     Translocatable P amount in living roots            N    |kg P ha-1|
    KTRANSLOCATABLERT     Translocatable K amount in living roots            N    |kg K ha-1|
    NTRANSLOCATABLE       Total N amount that can be translocated to the     Y    [kg N ha-1]
                          storage organs
    PTRANSLOCATABLE       Total P amount that can be translocated to the     Y    [kg P ha-1]
                          storage organs
    KTRANSLOCATABLE       Total K amount that can be translocated to the     Y    [kg K ha-1]
                          storage organs
    ===================  ================================================= ===== ============


    **Rate variables**


    ===================  ================================================= ==== ==============
     Name                 Description                                      Pbl      Unit
    ===================  ================================================= ==== ==============
    RNTRANSLOCATIONLV     Weight increase (N) in leaves                     Y    |kg ha-1 d-1|
    RPTRANSLOCATIONLV     Weight increase (P) in leaves                     Y    |kg ha-1 d-1|
    RKTRANSLOCATIONLV     Weight increase (K) in leaves                     Y    |kg ha-1 d-1|
    RNTRANSLOCATIONST     Weight increase (N) in stems                      Y    |kg ha-1 d-1|
    RPTRANSLOCATIONST     Weight increase (P) in stems                      Y    |kg ha-1 d-1|
    RKTRANSLOCATIONST     Weight increase (K) in stems                      Y    |kg ha-1 d-1|
    RNTRANSLOCATIONRT     Weight increase (N) in roots                      Y    |kg ha-1 d-1|
    RPTRANSLOCATIONRT     Weight increase (P) in roots                      Y    |kg ha-1 d-1|
    RKTRANSLOCATIONRT     Weight increase (K) in roots                      Y    |kg ha-1 d-1|
    ===================  ================================================= ==== ==============

    **Signals send or handled**

    None

    **External dependencies:**

    ===========  ================================ ======================  ===========
     Name         Description                      Provided by             Unit
    ===========  ================================ ======================  ===========
    DVS           Crop development stage           DVS_Phenology           -
    WST           Dry weight of living stems       WOFOST_Stem_Dynamics   |kg ha-1|
    WLV           Dry weight of living leaves      WOFOST_Leaf_Dynamics   |kg ha-1|
    WRT           Dry weight of living roots       WOFOST_Root_Dynamics   |kg ha-1|
    NAMOUNTLV     Amount of N in leaves            NPK_Crop_Dynamics      |kg ha-1|
    NAMOUNTST     Amount of N in stems             NPK_Crop_Dynamics      |kg ha-1|
    NAMOUNTRT     Amount of N in roots             NPK_Crop_Dynamics      |kg ha-1|
    PAMOUNTLV     Amount of P in leaves            NPK_Crop_Dynamics      |kg ha-1|
    PAMOUNTST     Amount of P in stems             NPK_Crop_Dynamics      |kg ha-1|
    PAMOUNTRT     Amount of P in roots             NPK_Crop_Dynamics      |kg ha-1|
    KAMOUNTLV     Amount of K in leaves            NPK_Crop_Dynamics      |kg ha-1|
    KAMOUNTST     Amount of K in stems             NPK_Crop_Dynamics      |kg ha-1|
    KAMOUNTRT     Amount of K in roots             NPK_Crop_Dynamics      |kg ha-1|
    ===========  ================================ ======================  ===========
    """

    class Parameters(ParamTemplate):
        NRESIDLV = Float(-99.)  # residual N fraction in leaves [kg N kg-1 dry biomass]
        NRESIDST = Float(-99.)  # residual N fraction in stems [kg N kg-1 dry biomass]
        NRESIDRT = Float(-99.)  # residual N fraction in roots [kg N kg-1 dry biomass]

        PRESIDLV = Float(-99.)  # residual P fraction in leaves [kg P kg-1 dry biomass]
        PRESIDST = Float(-99.)  # residual P fraction in stems [kg P kg-1 dry biomass]
        PRESIDRT = Float(-99.)  # residual P fraction in roots [kg P kg-1 dry biomass]

        KRESIDLV = Float(-99.)  # residual K fraction in leaves [kg P kg-1 dry biomass]
        KRESIDST = Float(-99.)  # residual K fraction in stems [kg P kg-1 dry biomass]
        KRESIDRT = Float(-99.)  # residual K fraction in roots [kg P kg-1 dry biomass]

        NPK_TRANSLRT_FR = Float(-99.)  # NPK translocation from roots as a fraction of
                                       # resp. total NPK amounts translocated from leaves
                                       # and stems
        DVS_NPK_TRANSL = Float(-99.) # Rate at which translocation to storage organs begins
        

    class RateVariables(RatesTemplate):
        RNTRANSLOCATIONLV = Float(-99.)  # N translocation rate from leaves [kg ha-1 d-1]
        RNTRANSLOCATIONST = Float(-99.)  # N translocation rate from stems [kg ha-1 d-1]
        RNTRANSLOCATIONRT = Float(-99.)  # N translocation rate from roots [kg ha-1 d-1]

        RPTRANSLOCATIONLV = Float(-99.)  # P translocation rate from leaves [kg ha-1 d-1]
        RPTRANSLOCATIONST = Float(-99.)  # P translocation rate from stems [kg ha-1 d-1]
        RPTRANSLOCATIONRT = Float(-99.)  # P translocation rate from roots [kg ha-1 d-1]

        RKTRANSLOCATIONLV = Float(-99.)  # K translocation rate from leaves [kg ha-1 d-1]
        RKTRANSLOCATIONST = Float(-99.)  # K translocation rate from stems [kg ha-1 d-1]
        RKTRANSLOCATIONRT = Float(-99.)  # K translocation rate from roots [kg ha-1 d-1]

    class StateVariables(StatesTemplate):
        NTRANSLOCATABLELV = Float(-99.)  # translocatable N amount in leaves [kg N ha-1]
        NTRANSLOCATABLEST = Float(-99.)  # translocatable N amount in stems [kg N ha-1]
        NTRANSLOCATABLERT = Float(-99.)  # translocatable N amount in roots [kg N ha-1]
        
        PTRANSLOCATABLELV = Float(-99.)  # translocatable P amount in leaves [kg N ha-1]
        PTRANSLOCATABLEST = Float(-99.)  # translocatable P amount in stems [kg N ha-1]
        PTRANSLOCATABLERT = Float(-99.)  # translocatable P amount in roots [kg N ha-1]
        
        KTRANSLOCATABLELV = Float(-99.)  # translocatable K amount in leaves [kg N ha-1
        KTRANSLOCATABLEST = Float(-99.)  # translocatable K amount in stems [kg N ha-1]
        KTRANSLOCATABLERT = Float(-99.)  # translocatable K amount in roots [kg N ha-1]

        NTRANSLOCATABLE = Float(-99.)  # Total N amount that can be translocated to the storage organs [kg N ha-1]
        PTRANSLOCATABLE = Float(-99.)  # Total P amount that can be translocated to the storage organs [kg P ha-1]
        KTRANSLOCATABLE = Float(-99.)  # Total K amount that can be translocated to the storage organs [kg K ha-1]

    def initialize(self, day:date, kiosk:VariableKiosk, parvalues:dict):
        """
        :param day: start date of the simulation
        :param kiosk: variable kiosk of this PCSE instance
        :param parvalues: dictionary with WOFOST cropdata key/value pairs
        """

        self.params = self.Parameters(parvalues)
        self.rates = self.RateVariables(kiosk, publish=["RNTRANSLOCATIONLV", "RNTRANSLOCATIONST", "RNTRANSLOCATIONRT",
                                                        "RPTRANSLOCATIONLV", "RPTRANSLOCATIONST", "RPTRANSLOCATIONRT",
                                                        "RKTRANSLOCATIONLV", "RKTRANSLOCATIONST", "RKTRANSLOCATIONRT"])

        self.states = self.StateVariables(kiosk,
            NTRANSLOCATABLELV=0., NTRANSLOCATABLEST=0., NTRANSLOCATABLERT=0., PTRANSLOCATABLELV=0., PTRANSLOCATABLEST=0.,
            PTRANSLOCATABLERT=0., KTRANSLOCATABLELV=0., KTRANSLOCATABLEST=0. ,KTRANSLOCATABLERT=0.,
            NTRANSLOCATABLE=0., PTRANSLOCATABLE=0., KTRANSLOCATABLE=0.,
            publish=["NTRANSLOCATABLE", "PTRANSLOCATABLE", "KTRANSLOCATABLE", "NTRANSLOCATABLELV", 
                     "NTRANSLOCATABLEST", "NTRANSLOCATABLERT", "PTRANSLOCATABLELV", 
                     "PTRANSLOCATABLEST", "PTRANSLOCATABLERT", "KTRANSLOCATABLELV", 
                     "KTRANSLOCATABLEST", "KTRANSLOCATABLERT",])
        self.kiosk = kiosk
        
    @prepare_rates
    def calc_rates(self, day:date, drv:WeatherDataProvider):
        """Calculate rates for integration
        """
        r = self.rates
        s = self.states
        k = self.kiosk

        # partitioning of the uptake for storage organs from the leaves, stems, roots
        # assuming equal distribution of N/P/K from each organ.
        # If amount of translocatable N/P/K = 0 then translocation rate is 0
        if s.NTRANSLOCATABLE > 0.:
            r.RNTRANSLOCATIONLV = k.RNUPTAKESO * s.NTRANSLOCATABLELV / s.NTRANSLOCATABLE
            r.RNTRANSLOCATIONST = k.RNUPTAKESO * s.NTRANSLOCATABLEST / s.NTRANSLOCATABLE
            r.RNTRANSLOCATIONRT = k.RNUPTAKESO * s.NTRANSLOCATABLERT / s.NTRANSLOCATABLE
        else:
            r.RNTRANSLOCATIONLV = r.RNTRANSLOCATIONST = r.RNTRANSLOCATIONRT = 0.

        if s.PTRANSLOCATABLE > 0:
            r.RPTRANSLOCATIONLV = k.RPUPTAKESO * s.PTRANSLOCATABLELV / s.PTRANSLOCATABLE
            r.RPTRANSLOCATIONST = k.RPUPTAKESO * s.PTRANSLOCATABLEST / s.PTRANSLOCATABLE
            r.RPTRANSLOCATIONRT = k.RPUPTAKESO * s.PTRANSLOCATABLERT / s.PTRANSLOCATABLE
        else:
            r.RPTRANSLOCATIONLV = r.RPTRANSLOCATIONST = r.RPTRANSLOCATIONRT = 0.

        if s.KTRANSLOCATABLE > 0:
            r.RKTRANSLOCATIONLV = k.RKUPTAKESO * s.KTRANSLOCATABLELV / s.KTRANSLOCATABLE
            r.RKTRANSLOCATIONST = k.RKUPTAKESO * s.KTRANSLOCATABLEST / s.KTRANSLOCATABLE
            r.RKTRANSLOCATIONRT = k.RKUPTAKESO * s.KTRANSLOCATABLERT / s.KTRANSLOCATABLE
        else:
            r.RKTRANSLOCATIONLV = r.RKTRANSLOCATIONST = r.RKTRANSLOCATIONRT = 0.

    @prepare_states
    def integrate(self, day:date, delt:float=1.0):
        """Integrate state rates
        """
        p = self.params
        s = self.states
        k = self.kiosk
        
        # translocatable N amount in the organs [kg N ha-1]
        s.NTRANSLOCATABLELV = max(0., k.NAMOUNTLV - k.WLV * p.NRESIDLV)
        s.NTRANSLOCATABLEST = max(0., k.NAMOUNTST - k.WST * p.NRESIDST)
        s.NTRANSLOCATABLERT = max(0., k.NAMOUNTRT - k.WRT * p.NRESIDRT)

        # translocatable P amount in the organs [kg P ha-1]
        s.PTRANSLOCATABLELV = max(0., k.PAMOUNTLV - k.WLV * p.PRESIDLV)
        s.PTRANSLOCATABLEST = max(0., k.PAMOUNTST - k.WST * p.PRESIDST)
        s.PTRANSLOCATABLERT = max(0., k.PAMOUNTRT - k.WRT * p.PRESIDRT)

        # translocatable K amount in the organs [kg K ha-1]
        s.KTRANSLOCATABLELV = max(0., k.KAMOUNTLV - k.WLV * p.KRESIDLV)
        s.KTRANSLOCATABLEST = max(0., k.KAMOUNTST - k.WST * p.KRESIDST)
        s.KTRANSLOCATABLERT = max(0., k.KAMOUNTRT - k.WRT * p.KRESIDRT)

        # total translocatable NPK amount in the organs [kg N ha-1]
        if k.DVS > p.DVS_NPK_TRANSL:
            s.NTRANSLOCATABLE = s.NTRANSLOCATABLELV + s.NTRANSLOCATABLEST + s.NTRANSLOCATABLERT
            s.PTRANSLOCATABLE = s.PTRANSLOCATABLELV + s.PTRANSLOCATABLEST + s.PTRANSLOCATABLERT
            s.KTRANSLOCATABLE = s.KTRANSLOCATABLELV + s.KTRANSLOCATABLEST + s.KTRANSLOCATABLERT
        else:
            s.NTRANSLOCATABLE = s.PTRANSLOCATABLE = s.KTRANSLOCATABLE = 0

    def reset(self):
        """Reset states and rates
        """ 
        s = self.states
        r = self.rates

        r.RNTRANSLOCATIONLV = r.RNTRANSLOCATIONST = r.RNTRANSLOCATIONRT = r.RPTRANSLOCATIONLV \
            = r.RPTRANSLOCATIONST = r.RPTRANSLOCATIONRT = r.RKTRANSLOCATIONLV \
            = r.RKTRANSLOCATIONST = r.RKTRANSLOCATIONRT = 0

        s.NTRANSLOCATABLELV = s.NTRANSLOCATABLEST = s.NTRANSLOCATABLERT = s.PTRANSLOCATABLELV \
            = s.PTRANSLOCATABLEST = s.PTRANSLOCATABLERT = s.KTRANSLOCATABLELV \
            = s.KTRANSLOCATABLEST = s.KTRANSLOCATABLERT = s.NTRANSLOCATABLE \
            = s.PTRANSLOCATABLE = s.KTRANSLOCATABLE = 0
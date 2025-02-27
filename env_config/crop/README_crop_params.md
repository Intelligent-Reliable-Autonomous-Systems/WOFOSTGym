# README_crop_params.md
# An overview of all the available crop 
# parameters for output to the simulation model

**############################################################################**
# WOFOST Parameters
**############################################################################**
**Simulation parameters:** (To be provided in cropdata dictionary):
======== =============================================== =======  ==========
 Name     Description                                     Type     Unit
======== =============================================== =======  ==========
CVL      Conversion factor for assimilates to leaves       SCr     -
CVO      Conversion factor for assimilates to storage      SCr     -
            organs
CVR      Conversion factor for assimilates to roots        SCr     -
CVS      Conversion factor for assimilates to stems        SCr     -
======== =============================================== =======  ==========

**############################################################################**
# Assimilation Parameters
**############################################################################**
**Simulation parameters** (To be provided in cropdata dictionary):
=========  ============================================= =======  ============
 Name       Description                                   Type     Unit
=========  ============================================= =======  ============
AMAXTB     Max leaf |CO2| assim. rate as a function of    TCr     |kg ha-1 hr-1|
            of DVS
EFFTB      Light use effic. single leaf as a function     TCr     |kg ha-1 hr-1 /(J m-2 s-1)|
            of daily mean temperature
KDIFTB     Extinction coefficient for diffuse visible     TCr      -
            as function of DVS
TMPFTB     Reduction factor of AMAX as function of        TCr      -
            daily mean temperature.
TNPFTB     Reduction factor of AMAX as function of        TCr      -
            daily minimum temperature.
CO2AMAXTB  Correction factor for AMAX given atmos-        TCr      -
            pheric CO2 concentration.
CO2EFFTB   Correction factor for EFF given atmos-         TCr      -
            pheric CO2 concentration.
CO2        Atmopheric CO2 concentration                   SCr      ppm
=========  ============================================= =======  ============

**############################################################################**
# Evapotranspiration Parameters
**############################################################################**
**Simulation parameters** (To be provided in cropdata dictionary):
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
            atmospheric CO2 concentration                T       -
======== ============================================= =======  ============

**############################################################################**
# Leaf Dynamics Parameters
**############################################################################**
**Simulation parameters** (provide in cropdata dictionary)
=======  ============================================= =======  ============
 Name     Description                                   Type     Unit
=======  ============================================= =======  ============
RGRLAI   Maximum relative increase in LAI.              SCr     ha ha-1 d-1
SPAN     Life span of leaves growing at 35 Celsius      SCr     |d|
TBASE    Lower threshold temp for ageing of leaves      SCr     |C|
PERDL    Max relative death rate of leaves due to       SCr
            water stress
TDWI     Initial total crop dry weight                  SCr     |kg ha-1|
KDIFTB   Extinction coefficient for diffuse visible     TCr
            light as function of DVS
SLATB    Specific leaf area as a function of DVS        TCr     |ha kg-1|
RDRNS    max. relative death rate of leaves due to      TCr         -
            nutrient NPK stress
NLAI     coefficient for the reduction due to           TCr         -
            nutrient NPK stress of the LAI increase
            (during juvenile phase).
NSLA     Coefficient for the effect of nutrient NPK     TCr         -
            stress on SLA reduction
RDRNS    Max. relative death rate of leaves due to      TCr         -
            nutrient NPK stress
=======  ============================================= =======  ============

**############################################################################**
# NPK Dynamics Parameters
**############################################################################**
**Simulation parameters** (To be provided in cropdata dictionary):
=============  ================================================= =======================
 Name           Description                                        Unit
=============  ================================================= =======================
NMAXLV_TB      Maximum N concentration in leaves as               kg N kg-1 dry biomass
                function of dvs
PMAXLV_TB      Maximum P concentration in leaves as               kg N kg-1 dry biomass
                function of dvs
KMAXLV_TB      Maximum K concentration in leaves as               kg N kg-1 dry biomass
                function of dvs

NMAXRT_FR      Maximum N concentration in roots as fraction       -
                of maximum N concentration in leaves
PMAXRT_FR      Maximum P concentration in roots as fraction       -
                of maximum P concentration in leaves
KMAXRT_FR      Maximum K concentration in roots as fraction       -
                of maximum K concentration in leaves

NMAXST_FR      Maximum N concentration in stems as fraction       -
                of maximum N concentration in leaves
PMAXST_FR      Maximum P concentration in stems as fraction       -
                of maximum P concentration in leaves
KMAXST_FR      Maximum K concentration in stems as fraction       -
                of maximum K concentration in leaves

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

**############################################################################**
# Partioning Parameters
**############################################################################**
**Simulation parameters** (To be provided in cropdata dictionary):
=======  ============================================= =======  ============
 Name     Description                                   Type     Unit
=======  ============================================= =======  ============
FRTB     Partitioning to roots as a function of          TCr       -
            development stage.
FSTB     Partitioning to stems as a function of          TCr       -
            development stage.
FLTB     Partitioning to leaves as a function of         TCr       -
            development stage.
FOTB     Partitioning to starge organs as a function     TCr       -
            of development stage.
NPART    Coefficient for the effect of N stress on       SCR       -
            leaf biomass allocation
NTHRESH  Threshold above which surface nitrogen          TCr       |kg ha-1|
             induces stress
PTHRESH  Threshold above which surface phosphorous       TCr       |kg ha-1|
             induces stress
KTHRESH  Threshold above which surface potassium         TCr       |kg ha-1|
             induces stress
=======  ============================================= =======  ============

**############################################################################**
# Vernalization Parameters
**############################################################################**
**Simulation parameters** (To be provided in cropdata dictionary):
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

**############################################################################**
# Phenology Parameters
**############################################################################**
**Simulation parameters** (To be provided in cropdata dictionary):
=======  ============================================= =======  ============
 Name     Description                                   Type     Unit
=======  ============================================= =======  ============
DTBEM    Consecutive days required above temperature    Scr        day
          emergence for germination
TSUMEM   Temperature sum from sowing to emergence       SCr        |C| day
TBASEM   Base temperature for emergence                 SCr        |C|
TEFFMX   Maximum effective temperature for emergence    SCr        |C|
TSUM1    Temperature sum from emergence to anthesis     SCr        |C| day
TSUM2    Temperature sum from anthesis to maturity      SCr        |C| day
TSUM3    Temperature sum from maturity to death         Scr        |C| day
IDSL     Switch for phenological development options    SCr        -
            temperature only (IDSL=0), including        SCr
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
DVSM     Mature development stage, usually 2.0          Scr        - 
DVSEND   Final development stage                        SCr        -
DTSMTB   Daily increase in temperature sum as a         TCr        |C|
            function of daily mean temperature.
DORM     Dormancy threshold after which the plant       Scr        day 
             enters dormancy (perennial only)    
DORMCD   The number of days a plant will stay dormant   Scr        day
          (perennial only)
AGEI     The initial age of the crop in years           Scr        year
          (perennial only)

=======  ============================================= =======  ============

**############################################################################**
# Respiration Parameters
**############################################################################**
**Simulation parameters** (To be provided in cropdata dictionary):
=======  ============================================= =======  ============
 Name     Description                                   Type     Unit
=======  ============================================= =======  ============
Q10      Relative increase in maintenance repiration    SCr       -
        rate with each 10 degrees increase in
        temperature
RMR      Relative maintenance respiration rate for
        roots                                          SCr     |kg CH2O kg-1 d-1|
RMS      Relative maintenance respiration rate for
        stems                                          SCr     |kg CH2O kg-1 d-1|
RML      Relative maintenance respiration rate for
        leaves                                         SCr     |kg CH2O kg-1 d-1|
RMO      Relative maintenance respiration rate for
        storage organs                                 SCr     |kg CH2O kg-1 d-1|
=======  ============================================= =======  ============

**############################################################################**
# Root Dynamics Parameters
**############################################################################**
**Simulation parameters** (To be provided in cropdata dictionary):
=======  ============================================= =======  ============
 Name     Description                                   Type     Unit
=======  ============================================= =======  ============
RDI      Initial rooting depth                          SCr      cm
RRI      Daily increase in rooting depth                SCr      |cm day-1|
RDMCR    Maximum rooting depth of the crop              SCR      cm
RDMSOL   Maximum rooting depth of the soil              SSo      cm
TDWI     Initial total crop dry weight                  SCr      |kg ha-1|
IAIRDU   Presence of air ducts in the root (1) or       SCr      -
            not (0)
RDRRTB   Relative death rate of roots as a function     TCr      -
            of development stage
RDRROS   Relative death rate of roots as a function     TCr      -
            of oxygen stress
RDRRNPK  Relative rate of root death due to NPK excess  SCr      - 
=======  ============================================= =======  ============

**############################################################################**
# Stem Dynamics Parameters
**############################################################################**
**Simulation parameters** (To be provided in cropdata dictionary):
=======  ============================================= =======  ============
 Name     Description                                   Type     Unit
=======  ============================================= =======  ============
TDWI     Initial total crop dry weight                  SCr       |kg ha-1|
RDRSTB   Relative death rate of stems as a function     TCr       -
            of development stage
SSATB    Specific Stem Area as a function of            TCr       |ha kg-1|
            development stage
=======  ============================================= =======  ============

**############################################################################**
# Storage Organs Dynamics Parameters
**############################################################################**
**Simulation parameters** (To be provided in cropdata dictionary):
=======  ============================================= =======  ============
 Name     Description                                   Type     Unit
=======  ============================================= =======  ============
TDWI     Initial total crop dry weight                  SCr      |kg ha-1|
RDRSOB   Relative Death rate of storage organs as a     Scr      |kg ha-1|
            function of development stage               
SPA      Specific Pod Area                              SCr      |ha kg-1|
RDRSOB   Relative Death rate of storage organs as a     Scr      |kg ha-1|
            function of frost kill   
=======  ============================================= =======  ============    

**############################################################################**
# NPK Demand Uptake Parameters
**############################################################################**
**Simulation parameters** (To be provided in cropdata dictionary):
============  =============================================  ======================
 Name          Description                                    Unit
============  =============================================  ======================
NMAXLV_TB      Maximum N concentration in leaves as          kg N kg-1 dry biomass
                function of DVS
PMAXLV_TB      Maximum P concentration in leaves as          kg N kg-1 dry biomass
                function of DVS
KMAXLV_TB      Maximum K concentration in leaves as          kg N kg-1 dry biomass
                function of DVS

NMAXRT_FR      Maximum N concentration in roots as fraction  -
                of maximum N concentration in leaves
PMAXRT_FR      Maximum P concentration in roots as fraction  -
                of maximum P concentration in leaves
KMAXRT_FR      Maximum K concentration in roots as fraction  -
                of maximum K concentration in leaves

NMAXST_FR      Maximum N concentration in stems as fraction  -
                of maximum N concentration in leaves
PMAXST_FR      Maximum P concentration in stems as fraction  -
                of maximum P concentration in leaves
KMAXST_FR      Maximum K concentration in stems as fraction  -
                of maximum K concentration in leaves

NMAXSO         Maximum N concentration in storage organs     kg N kg-1 dry biomass
PMAXSO         Maximum P concentration in storage organs     kg N kg-1 dry biomass
KMAXSO         Maximum K concentration in storage organs     kg N kg-1 dry biomass

NCRIT_FR       Critical N concentration as fraction of       -
                maximum N concentration for vegetative
                plant organs as a whole (leaves + stems)
PCRIT_FR        Critical P concentration as fraction of       -
                maximum P concentration for vegetative
                plant organs as a whole (leaves + stems)
KCRIT_FR        Critical K concentration as fraction of       -
                maximum K concentration for vegetative
                plant organs as a whole (leaves + stems)

TCNT           Time coefficient for N translation to         days
                storage organs
TCPT           Time coefficient for P translation to         days
                storage organs
TCKT           Time coefficient for K translation to         days
                storage organs

NFIX_FR        fraction of crop nitrogen uptake by           kg N kg-1 dry biomass
                biological fixation
RNUPTAKEMAX    Maximum rate of N uptake                      |kg N ha-1 d-1|
RPUPTAKEMAX    Maximum rate of P uptake                      |kg N ha-1 d-1|
RKUPTAKEMAX    Maximum rate of K uptake                      |kg N ha-1 d-1|
    ============  =============================================  ======================

**############################################################################**
# NPK Stress Parameters
**############################################################################**
**Simulation parameters** (To be provided in cropdata dictionary):
============  ============================================= ======================
  Name          Description                                   Unit
============  ============================================= ======================
NMAXLV_TB      Maximum N concentration in leaves as         kg N kg-1 dry biomass
                function of DVS
PMAXLV_TB      Maximum P concentration in leaves as         kg N kg-1 dry biomass
                function of DVS
KMAXLV_TB      Maximum K concentration in leaves as         kg N kg-1 dry biomass
                function of DVS

NMAXRT_FR      Maximum N concentration in roots as fraction -
                of maximum N concentration in leaves
PMAXRT_FR      Maximum P concentration in roots as fraction -
                of maximum P concentration in leaves
KMAXRT_FR      Maximum K concentration in roots as fraction -
                of maximum K concentration in leaves

NMAXST_FR      Maximum N concentration in stems as fraction -
                of maximum N concentration in leaves
PMAXST_FR      Maximum P concentration in stems as fraction -
                of maximum P concentration in leaves
KMAXST_FR      Maximum K concentration in stems as fraction -
                of maximum K concentration in leaves

NCRIT_FR       Critical N concentration as fraction of      -
                maximum N concentration for vegetative
                plant organs as a whole (leaves + stems)
PCRIT_FR       Critical P concentration as fraction of      -
                maximum P concentration for vegetative
                plant organs as a whole (leaves + stems)
KCRIT_FR       Critical K concentration as fraction of      -
                maximum L concentration for vegetative
                plant organs as a whole (leaves + stems)
NRESIDLV       Residual N fraction in leaves                kg N kg-1 dry biomass
PRESIDLV       Residual P fraction in leaves                kg P kg-1 dry biomass
KRESIDLV       Residual K fraction in leaves                kg K kg-1 dry biomass

NRESIDST       Residual N fraction in stems                 kg N kg-1 dry biomass
PRESIDST       Residual P fraction in stems                 kg P kg-1 dry biomass
KRESIDST       Residual K fraction in stems                 kg K kg-1 dry biomass

NLUE_NPK       Coefficient for the reduction of RUE due     -
                to nutrient (N-P-K) stress
============  ============================================= ======================

**############################################################################**
# NPK Translocation Parameters
**############################################################################**
**Simulation parameters** (To be provided in cropdata dictionary):
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
===============  =============================================  ======================

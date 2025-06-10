# README_crop_params.md
# An overview of all the available crop 
# State and Rate values for output to the simulation model

**############################################################################**
# WOFOST States and Rates
**############################################################################**
**State variables:** (For output to observation space):
============  ================================================= ==== ===============
 Name          Description                                      Pbl      Unit
============  ================================================= ==== ===============
TAGP          Total above-ground Production                      N    |kg ha-1|
GASST         Total gross assimilation                           N    |kg CH2O ha-1|
MREST         Total gross maintenance respiration                N    |kg CH2O ha-1|
CTRAT         Total crop transpiration accumulated over the
                crop cycle                                       N    cm
CEVST         Total soil evaporation accumulated over the
                crop cycle                                       N    cm
HI            Harvest Index (only calculated during              N    -
                finalize())
DOF           Date representing the day of finish of the crop    N    -
                simulation.
FINISH_TYPE   String representing the reason for finishing the   N    -
                simulation: maturity, harvest, leave death, etc.
============  ================================================= ==== ===============
**Rate variables:** (For output to observation space):
=======  ================================================ ==== =============
 Name     Description                                      Pbl      Unit
=======  ================================================ ==== =============
GASS     Assimilation rate corrected for water stress       N  |kg CH2O ha-1 d-1|
PGASS    Potential assimilation rate                        N  |kg CH2O ha-1 d-1|
MRES     Actual maintenance respiration rate, taking into
            account that MRES <= GASS.                      N  |kg CH2O ha-1 d-1|
PMRES    Potential maintenance respiration rate             N  |kg CH2O ha-1 d-1|
ASRC     Net available assimilates (GASS - MRES)            N  |kg CH2O ha-1 d-1|
DMI      Total dry matter increase, calculated as ASRC
            times a weighted conversion efficieny.          Y  |kg ha-1 d-1|
ADMI     Aboveground dry matter increase                    Y  |kg ha-1 d-1|
=======  ================================================ ==== =============

**############################################################################**
# Assimilation States and Rates
**############################################################################**

**############################################################################**
# Evapotranspiration States and Rates
**############################################################################**
**State variables** (For output to observation space):
=======  ================================================= ==== ============
 Name     Description                                      Pbl      Unit
=======  ================================================= ==== ============
IDWST     Nr of days with water stress.                     N    -
IDOST     Nr of days with oxygen stress.                    N    -
=======  ================================================= ==== ============
**Rate variables** (For output to observation space):
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

**############################################################################**
# Leaf Dynamics States and Rates
**############################################################################**
**State variables** (For output to observation space):
=======  ================================================= ==== ============
 Name     Description                                      Pbl      Unit
=======  ================================================= ==== ============
LV       Leaf biomass per leaf class                        N    |kg ha-1|
SLA      Specific leaf area per leaf class                  N    |ha kg-1|
LVAGE    Leaf age per leaf class                            N    |d|
LVSUM    Sum of LV                                          N    |kg ha-1|
LAIEM    LAI at emergence                                   N    -
LASUM    Total leaf area as sum of LV*SLA,                  N    -
            not including stem and pod area                 
LAIEXP   LAI value under theoretical exponential growth     N    -
LAIMAX   Maximum LAI reached during growth cycle            N    -
LAI      Leaf area index, including stem and pod area       Y    -
WLV      Dry weight of living leaves                        Y    |kg ha-1|
DWLV     Dry weight of dead leaves                          N    |kg ha-1|
TWLV     Dry weight of total leaves (living + dead)         Y    |kg ha-1|
=======  ================================================= ==== ============
**Rate variables** (For output to observation space):
=======  ================================================= ==== ============
 Name     Description                                      Pbl      Unit
=======  ================================================= ==== ============
GRLV     Growth rate leaves                                 N   |kg ha-1 d-1|
DSLV1    Death rate leaves due to water stress              N   |kg ha-1 d-1|
DSLV2    Death rate leaves due to self-shading              N   |kg ha-1 d-1|
DSLV3    Death rate leaves due to frost kill                N   |kg ha-1 d-1|
DSLV4    Death rate leaves due to nutrient stress           N   |kg ha-1 d-1|
DSLV     Maximum of DLSV1, DSLV2, DSLV3                     N   |kg ha-1 d-1|
DALV     Death rate leaves due to aging.                    N   |kg ha-1 d-1|
DRLV     Death rate leaves as a combination of DSLV and     N   |kg ha-1 d-1|
            DALV
SLAT     Specific leaf area for current time step,          N   |ha kg-1|
            adjusted for source/sink limited leaf expansion
            rate.
FYSAGE   Increase in physiological leaf age                 N   -
GLAIEX   Sink-limited leaf expansion rate (exponential      N   |ha ha-1 d-1|
            curve)
GLASOL   Source-limited leaf expansion rate (biomass        N   |ha ha-1 d-1|
            increase)
=======  ================================================= ==== ============

**############################################################################**
# NPK Dynamics States and Rates
**############################################################################**
**State variables** (For output to observation space):
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
**Rate variables** (For output to observation space):
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
RPDEATHLV      Rate of P loss in leaves                         |kg N ha-1 d-1|
RKDEATHLV      Rate of K loss in leaves                         |kg N ha-1 d-1|

RNDEATHST      Rate of N loss in roots                          |kg N ha-1 d-1|
RPDEATHST      Rate of P loss in roots                          |kg N ha-1 d-1|
RKDEATHST      Rate of K loss in roots                          |kg N ha-1 d-1|

RNDEATHRT      Rate of N loss in stems                          |kg N ha-1 d-1|
RPDEATHRT      Rate of P loss in stems                          |kg N ha-1 d-1|
RKDEATHRT      Rate of K loss in stems                          |kg N ha-1 d-1|

RNLOSS         N loss due to senescence                         |kg N ha-1 d-1|
RPLOSS         P loss due to senescence                         |kg P ha-1 d-1|
RKLOSS         K loss due to senescence                         |kg K ha-1 d-1|
===========  =================================================  ================

**############################################################################**
# Partitioning States and Rates
**############################################################################**
**State variables** (For output to observation space):
=======  ================================================= ==== ============
 Name     Description                                      Pbl      Unit
=======  ================================================= ==== ============
FR        Fraction partitioned to roots.                     Y    -
FS        Fraction partitioned to stems.                     Y    -
FL        Fraction partitioned to leaves.                    Y    -
FO        Fraction partitioned to storage orgains            Y    -
=======  ================================================= ==== ============

**############################################################################**
# Vernalization States and Rates
**############################################################################**
**State variables** (For output to observation space):
============ ================================================= ==== ========
 Name        Description                                       Pbl   Unit
============ ================================================= ==== ========
VERN         Vernalisation state                                N    days
DOV          Day when vernalisation requirements are            N    -
                fulfilled.
ISVERNALISED Flag indicated that vernalisation                  Y    -
                requirement has been reached
============ ================================================= ==== ========
**Rate variables** (For output to observation space):
=======  ================================================= ==== ============
 Name     Description                                      Pbl      Unit
=======  ================================================= ==== ============
VERNR    Rate of vernalisation                              N     -
VERNFAC  Reduction factor on development rate due to        Y     -
            vernalisation effect.
=======  ================================================= ==== ============

**############################################################################**
# Phenology States and Rates
**############################################################################**
**State variables** (For output to observation space):
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
            emerging|vegetative|reproductive|mature
DSNG     Days since no crop growth (perennial only)         Y    day
DSD      Days since dormancy started (perennial only)       Y    day
AGE      Age of the crop in years (perennial only)          Y    year
DOP      Day of Planting                                    Y    -
DATBE    Number of consecutive days above temperature sum   Y    day
          for emergence
=======  ================================================= ==== ============
**Rate variables** (For output to observation space):
=======  ================================================= ==== ============
 Name     Description                                      Pbl      Unit
=======  ================================================= ==== ============
DTSUME   Increase in temperature sum for emergence          N    |C|
DTSUM    Increase in temperature sum for anthesis or        N    |C|
            maturity
DVR      Development rate                                   Y    |day-1|
RDEM     Day increase when day temp is above TSUMEM         Y    day
=======  ================================================= ==== ============

**############################################################################**
# Respiration Dynamics States and Rates
**############################################################################**
**Rate variables:** (For output to observation space):
=======  ================================================ ==== =============
 Name     Description                                      Pbl      Unit
=======  ================================================ ==== =============
PMRES    Potential maintenance respiration rate             N  |kg CH2O ha-1 d-1|
=======  ================================================ ==== =============

**############################################################################**
# Root Dynamics States and Rates
**############################################################################**
**State variables** (For output to observation space):
=======  ================================================= ==== ============
 Name     Description                                      Pbl      Unit
=======  ================================================= ==== ============
RD       Current rooting depth                              Y     cm
RDM      Maximum attainable rooting depth at the minimum    N     cm
            of the soil and crop maximum rooting depth
WRT      Weight of living roots                             Y     |kg ha-1|
DWRT     Weight of dead roots                               N     |kg ha-1|
TWRT     Total weight of roots                              Y     |kg ha-1|
=======  ================================================= ==== ============
**Rate variables** (For output to observation space):
=======  ================================================= ==== ============
 Name     Description                                      Pbl      Unit
=======  ================================================= ==== ============
RR       Growth rate root depth                             N    cm
GRRT     Growth rate root biomass                           N   |kg ha-1 d-1|
DRRT1    Death rate of roots due to aging                   N   |kg ha-1 d-1|
DRRT2    Death rate of roots due to excess water            N   |kg ha-1 d-1|
DRRT3    Death rate of roots due to excess NPK              N   |kg ha-1 d-1|
DRRT     Death rate root biomass                            N   |kg ha-1 d-1|
GWRT     Net change in root biomass                         N   |kg ha-1 d-1|
=======  ================================================= ==== ============

**############################################################################**
# Stem Dynamics States and Rates
**############################################################################**
**State variables** (For output to observation space):
=======  ================================================= ==== ============
 Name     Description                                      Pbl      Unit
=======  ================================================= ==== ============
SAI      Stem Area Index                                    Y     -
WST      Weight of living stems                             Y     |kg ha-1|
DWST     Weight of dead stems                               N     |kg ha-1|
TWST     Total weight of stems                              Y     |kg ha-1|
=======  ================================================= ==== ============
**Rate Variables** (For output to observation space):
=======  ================================================= ==== ============
 Name     Description                                      Pbl      Unit
=======  ================================================= ==== ============
GRST     Growth rate stem biomass                           N   |kg ha-1 d-1|
DRST     Death rate stem biomass                            N   |kg ha-1 d-1|
GWST     Net change in stem biomass                         N   |kg ha-1 d-1|
=======  ================================================= ==== ============

**############################################################################**
# Storage Organs Dynamics States and Rates
**############################################################################**
**State variables** (For output to observation space):
=======  ================================================= ==== ============
 Name     Description                                      Pbl      Unit
=======  ================================================= ==== ============
PAI      Pod Area Index                                     Y     -
WSO      Weight of living storage organs                    Y     |kg ha-1|
DWSO     Weight of dead storage organs                      N     |kg ha-1|
TWSO     Total weight of storage organs                     Y     |kg ha-1|
HWSO     Harvestable weight of storage organs               Y     |kg ha-1|
LHW      Last harvest weight of storage organs              Y     |kg ha-1|
=======  ================================================= ==== ============
**Rate variables** (For output to observation space):
=======  ================================================= ==== ============
 Name     Description                                      Pbl      Unit
=======  ================================================= ==== ============
GRSO     Growth rate storage organs                         N   |kg ha-1 d-1|
DRSO     Death rate storage organs                          N   |kg ha-1 d-1|
DHSO     Death rate of harvestable storage organs           N   |kg ha-1 d-1|
GWSO     Net change in storage organ biomass                N   |kg ha-1 d-1|
=======  ================================================= ==== ============

**############################################################################**
# NPK Demand Uptake States and Rates
**############################################################################**
**State variables** (For output to observation space):
=============  ================================================= ==== ============
 Name           Description                                      Pbl      Unit
=============  ================================================= ==== ============
NUPTAKETOTAL     Total N uptake by the crop                        N   |kg N ha-1|
PUPTAKETOTAL     Total P uptake by the crop                        N   |kg N ha-1|
KUPTAKETOTAL     Total K uptake by the crop                        N   |kg N ha-1|
NFIXTOTAL        Total N fixated by the crop                       N   |kg N ha-1|

NDEMANDST        N Demand in living stems                          N   |kg N ha-1|
NDEMANDRT        N Demand in living roots                          N   |kg N ha-1|
NDEMANDSO        N Demand in storage organs                        N   |kg N ha-1|

PDEMANDLV        P Demand in living leaves                         N   |kg P ha-1|
PDEMANDST        P Demand in living stems                          N   |kg P ha-1|
PDEMANDRT        P Demand in living roots                          N   |kg P ha-1|
PDEMANDSO        P Demand in storage organs                        N   |kg P ha-1|

KDEMANDLV        K Demand in living leaves                         N   |kg K ha-1|
KDEMANDST        K Demand in living stems                          N   |kg K ha-1|
KDEMANDRT        K Demand in living roots                          N   |kg K ha-1|
KDEMANDSO        K Demand in storage organs                        N   |kg K ha-1|
==========  ================================================= ==== ============
**Rate variables** (For output to observation space):
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
**############################################################################**
# NPK Stress States and Rates
**############################################################################**
**Rate variables** (For output to observation space):
=======  ================================================= ==== ==============
 Name     Description                                      Pbl      Unit
=======  ================================================= ==== ==============
NNI       Nitrogen nutrition index                          Y     -
PNI       Phosphorous nutrition index                       N     -
KNI       Potassium nutrition index                         N     -
NPKI      Minimum of NNI, PNI, KNI                          Y     -
RFNPK     Reduction factor for |CO2| assimlation            N     -
            based on NPKI and the parameter NLUE_NPK
=======  ================================================= ==== ==============

**############################################################################**
# NPK Dynamics States and Rates
**############################################################################**
 **State variables** (For output to observation space):
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
**Rate variables** (For output to observation space):
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

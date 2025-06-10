# README_site_params.md
# An overview of all the available soil 
# State and Rate values for output to the simulation model


**############################################################################**
# NPK Soil Dynamics States and Rates
**############################################################################**
**State variables** (For output to observation space):
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
**Rate variables** (For output to observation space):
==============  ================================================= ==== =============
 Name            Description                                       Pbl      Unit
==============  ================================================= ==== =============
RNSOIL           Rate of change on total soil mineral N            N   |kg ha-1 d-1|
RPSOIL           Rate of change on total soil mineral P            N   |kg ha-1 d-1|
RKSOIL           Rate of change on total soil mineral K            N   |kg ha-1 d-1|

RNAVAIL          Total change in N availability                    N   |kg ha-1 d-1|
RPAVAIL          Total change in P availability                    N   |kg ha-1 d-1|
RKAVAIL          Total change in K availability                    N   |kg ha-1 d-1|

FERT_N_SUPPLY    Rate of supply of fertilizer N                    N   |kg ha-1 d-1|            
FERT_P_SUPPLY    Rate of Supply of fertilizer P                    N   |kg ha-1 d-1|
FERT_K_SUPPLY    Rate of Supply of fertilizer K                    N   |kg ha-1 d-1|

RRUNOFF_N        Rate of N runoff                                  N   |kg ha-1 d-1|
RRUNOFF_P        Rate of P runoff                                  N   |kg ha-1 d-1|
RRUNOFF_K        Rate of K runoff                                  N   |kg ha-1 d-1|

RNSUBSOIL        Rate of N from surface to subsoil                 N   |kg ha-1 d-1|
RPSUBSOIL        Rate of N from surface to subsoil                 N   |kg ha-1 d-1|
RKSUBSOIL        Rate of N from surface to subsoil                 N   |kg ha-1 d-1|
==============  ================================================= ==== =============

**############################################################################**
# Soil Dynamics States and Rates
**############################################################################**
**State variables:** (For output to observation space):
=======  ================================================= ==== ============
 Name     Description                                      Pbl      Unit
=======  ================================================= ==== ============
SM        Volumetric moisture content in root zone          Y    -
SS        Surface storage (layer of water on surface)       N    cm
SSI       Initial urface storage                            N    cm
WC        Amount of water in root zone                      N    cm
WI        Initial amount of water in the root zone          N    cm
WLOW      Amount of water in the subsoil (between current   N    cm
            rooting depth and maximum rootable depth)
WLOWI     Initial amount of water in the subsoil                 cm
WWLOW     Total amount of water in the  soil profile        N    cm
            WWLOW = WLOW + W
WTRAT     Total water lost as transpiration as calculated   N    cm
            by the water balance. This can be different 
            from the CTRAT variable which only counts
            transpiration for a crop cycle.
EVST      Total evaporation from the soil surface           N    cm
EVWT      Total evaporation from a water surface            N    cm
TSR       Total surface runoff                              N    cm
RAINT     Total amount of rainfall (eff + non-eff)          N    cm
WART      Amount of water added to root zone by increase    N    cm
            of root growth
TOTINF    Total amount of infiltration                      N    cm
TOTIRRIG  Total amount of irrigation                        N    cm
TOTIRR    Total amount of effective irrigation              N    cm
PERCT     Total amount of water percolating from rooted     N    cm
            zone to subsoil
LOSST     Total amount of water lost to deeper soil         N    cm
DSOS      Days since oxygen stress, accumulates the number  Y     -
            of consecutive days of oxygen stress
WBALRT    Checksum for root zone waterbalance               N    cm
WBALTT    Checksum for total waterbalance                   N    cm
=======  ================================================= ==== ============
**Rate variables:** (For output to observation space):
=========== ================================================= ==== ============
 Name        Description                                      Pbl      Unit
=========== ================================================= ==== ============
EVS         Actual evaporation rate from soil                  N    |cmday-1|
EVW         Actual evaporation rate from water surface         N    |cmday-1|
WTRA        Actual transpiration rate from plant canopy,       N    |cmday-1|
            is directly derived from the variable "TRA" in
            the evapotranspiration module
RAIN_INF    Infiltrating rainfall rate for current day         N    |cmday-1|
RAIN_NOTINF Non-infiltrating rainfall rate for current day     N    |cmday-1|
RIN         Infiltration rate for current day                  N    |cmday-1|
RIRR        Effective irrigation rate for current day,         N    |cmday-1|
            computed as irrigation amount * efficiency.
PERC        Percolation rate to non-rooted zone                N    |cmday-1|
LOSS        Rate of water loss to deeper soil                  N    |cmday-1|
DW          Change in amount of water in rooted zone as a      N    |cmday-1|
            result of infiltration, transpiration and
            evaporation.
DWLOW       Change in amount of water in subsoil               N    |cmday-1|
DTSR        Change in surface runoff                           N    |cmday-1|
DSS         Change in surface storage                          N    |cmday-1|
=========== ================================================= ==== ============

# README_crop_params.md
# An overview of all the available soil 
# parameters for output to the simulation model

**############################################################################**
# NPK Soil Parameters
**############################################################################**
**Simulation parameters** (To be provided in cropdata dictionary):
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
RNPKRUNOFF    Relative rate of NPK runoff as a function      SSi      - 
                  surface water runoff
============  ============================================= =======  ==============

**############################################################################**
# Soil Dynamics Parameters
**############################################################################**
**Simulation parameters** (To be provided in cropdata dictionary):
======== =============================================== =======  ==========
 Name     Description                                     Type     Unit
======== =============================================== =======  ==========
SMFCF     Field capacity of the soil                       SSo     -
SM0       Porosity of the soil                             SSo     -
SMW       Wilting point of the soil                        SSo     -
CRAIRC    Soil critical air content (waterlogging)         SSo     -
SOPE      maximum percolation rate root zone               SSo    |cmday-1|
KSUB      maximum percolation rate subsoil                 SSo    |cmday-1|
RDMSOL    Soil rootable depth                              SSo     cm
IFUNRN    Indicates whether non-infiltrating fraction of   SSi     -
            rain is a function of storm size (1)
            or not (0)                                      
SSMAX     Maximum surface storage                          SSi     cm
SSI       Initial surface storage                          SSi     cm
WAV       Initial amount of water in total soil            SSi     cm
            profile
NOTINF    Maximum fraction of rain not-infiltrating into   SSi     -
            the soil
SMLIM     Initial maximum moisture content in initial      SSi     -
            rooting depth zone.
======== =============================================== =======  ==========


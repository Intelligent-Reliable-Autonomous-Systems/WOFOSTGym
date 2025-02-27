
"""Utils file for making model configurations and setting parameters from arguments
"""
import gymnasium as gym
from datetime import datetime
from pcse_gym.args import WOFOST_Args, Agro_Args
import yaml
import numpy as np


from pcse.soil.soil_wrappers import BaseSoilModuleWrapper, SoilModuleWrapper_LNPKW
from pcse.crop.wofost8 import BaseCropModel, Wofost80
from pcse.agromanager import BaseAgroManager, AgroManagerAnnual

def make_config(soil: BaseSoilModuleWrapper=SoilModuleWrapper_LNPKW, crop: BaseCropModel=Wofost80, \
                agro: BaseAgroManager=AgroManagerAnnual):
    """Makes the configuration dictionary to be used to set various values of
    the model.
    
    Further modified in the WOFOST Gym delcaration.
    
    Args:
        None
    """

    # Module to be used for water balance
    SOIL = soil

    # Module to be used for the crop simulation itself
    CROP = crop

    # Module to use for AgroManagement actions
    AGROMANAGEMENT = agro

    # interval for OUTPUT signals, either "daily"|"dekadal"|"monthly"
    # For daily output you change the number of days between successive
    # outputs using OUTPUT_INTERVAL_DAYS. For dekadal and monthly
    # output this is ignored.
    OUTPUT_INTERVAL = "daily"
    OUTPUT_INTERVAL_DAYS = 1
    # Weekday: Monday is 0 and Sunday is 6
    OUTPUT_WEEKDAY = 0

    # variables to save at OUTPUT signals
    # Set to an empty list if you do not want any OUTPUT
    OUTPUT_VARS = [ 
        # WOFOST STATES 
        "TAGP", "GASST", "MREST", "CTRAT", "CEVST", "HI", "DOF", "FINISH_TYPE", "FIN",
        # WOFOST RATES 
        "GASS", "PGASS", "MRES", "ASRC", "DMI", "ADMI",
        # EVAPOTRANSPIRATION STATES
        "IDOST", "IDWST",
        # EVAPOTRANSPIRATION RATES  
        "EVWMX", "EVSMX", "TRAMX", "TRA", "IDOS", "IDWS", "RFWS", "RFOS", 
        "RFTRA",
        # LEAF DYNAMICS STATES
        "LV", "SLA", "LVAGE", "LAIEM", "LASUM", "LAIEXP", "LAIMAX", "LAI", "WLV", 
        "DWLV", "TWLV",
        # LEAF DYNAMICS RATES
        "GRLV", "DSLV1", "DSLV2", "DSLV3", "DSLV4", "DSLV", "DALV", "DRLV", "SLAT", 
        "FYSAGE", "GLAIEX", "GLASOL",
        # NPK DYNAMICS STATES
        "NAMOUNTLV", "PAMOUNTLV", "KAMOUNTLV", "NAMOUNTST", "PAMOUNTST", "KAMOUNTST",
        "NAMOUNTSO", "PAMOUNTSO", "KAMOUNTSO", "NAMOUNTRT", "PAMOUNTRT", "KAMOUNTRT",
        "NUPTAKETOTAL", "PUPTAKETOTAL", "KUPTAKETOTAL", "NFIXTOTAL", "NLOSSESTOTAL", 
        "PLOSSESTOTAL", "KLOSSESTOTAL", 
        # NPK DYNAMICS RATES
        "RNAMOUNTLV", "RPAMOUNTLV", "RKAMOUNTLV", 
        "RNAMOUNTST", "RPAMOUNTST", "RKAMOUNTST", "RNAMOUNTRT", "RPAMOUNTRT",  
        "RKAMOUNTRT", "RNAMOUNTSO", "RPAMOUNTSO", "RKAMOUNTSO", "RNDEATHLV", 
        "RNDEATHST", "RNDEATHRT", "RPDEATHLV", "RPDEATHST", "RPDEATHRT", "RKDEATHLV",
        "RKDEATHST", "RKDEATHRT", "RNLOSS", "RPLOSS", "RKLOSS", 
        # PARTIONING STATES
        "FR", "FL", "FS", "FO", 
        # PARTIONING RATES
            # NONE
        # VERNALIZATION STATES
        "VERN", "ISVERNALISED",
        # VERNALIZATION RATES
        "VERNR", "VERNFAC",   
        # PHENOLOGY STATES
        "DVS", "TSUM", "TSUME", "STAGE", "DSNG",
        "DSD", "AGE", "DOP", "DATBE", "DOC", "DON", "DOB", "DOV", "DOR", "DOL",
        # PHENOLOGY RATES
        "DTSUME", "DTSUM", "DVR", "RDEM",
        # RESPIRATION STATES
            # NONE
        # RESPIRATION RATES
        "PMRES",
        # ROOT DYNAMICS STATES
        "RD", "RDM", "WRT", "DWRT", "TWRT", 
        # ROOT DYNAMICS RATES
        "RR", "GRRT", "DRRT1", "DRRT2", "DRRT3", "DRRT", "GWRT", 
        # STEM DYNAMICS STATES
        "WST", "DWST", "TWST", "SAI", 
        # STEM DYNAMICS RATES
        "GRST", "DRST", "GWST",
        # STORAGE ORGAN DYNAMICS STATES
        "WSO", "DWSO", "TWSO", "HWSO", "PAI","LHW",
        # STORAGE ORGAN DYNAMICS RATES
        "GRSO", "DRSO", "GWSO", "DHSO",
        # NPK NUTRIENT DEMAND UPTAKE STATES
            # NONE
        # NPK NUTRIENT DEMAND UPTAKE RATES
        "RNUPTAKELV", "RNUPTAKEST", "RNUPTAKERT", "RNUPTAKESO", "RPUPTAKELV", 
        "RPUPTAKEST", "RPUPTAKERT", "RPUPTAKESO", "RKUPTAKELV", "RKUPTAKEST", 
        "RKUPTAKERT", "RKUPTAKESO", "RNUPTAKE", "RPUPTAKE", "RKUPTAKE", "RNFIXATION",
        "NDEMANDLV", "NDEMANDST", "NDEMANDRT", "NDEMANDSO", "PDEMANDLV", "PDEMANDST", 
        "PDEMANDRT", "PDEMANDSO", "KDEMANDLV", "KDEMANDST", "KDEMANDRT","KDEMANDSO", 
        "NDEMAND", "PDEMAND", "KDEMAND", 
        # NPK STRESS STATES
            # NONE
        # NPK STRESS RATES
        "NNI", "PNI", "KNI", "NPKI", "RFNPK", 
        # NPK TRANSLOCATION STATES
        "NTRANSLOCATABLELV", "NTRANSLOCATABLEST", "NTRANSLOCATABLERT", "PTRANSLOCATABLELV",
        "PTRANSLOCATABLEST", "PTRANSLOCATABLERT", "KTRANSLOCATABLELV", "KTRANSLOCATABLEST",
        "KTRANSLOCATABLERT", "NTRANSLOCATABLE", "PTRANSLOCATABLE", "KTRANSLOCATABLE", 
        # NPK TRANSLOCATION RATES
        "RNTRANSLOCATIONLV", "RNTRANSLOCATIONST", "RNTRANSLOCATIONRT", "RPTRANSLOCATIONLV",
        "RPTRANSLOCATIONST", "RPTRANSLOCATIONRT", "RKTRANSLOCATIONLV", "RKTRANSLOCATIONST",
        "RKTRANSLOCATIONRT",
        # SOIL STATES
        "SM", "SS", "SSI", "WC", "WI", "WLOW", "WLOWI", "WWLOW", "WTRAT", "EVST", 
        "EVWT", "TSR", "RAINT", "WART", "TOTINF", "TOTIRR", "PERCT", "LOSST", "WBALRT", 
        "WBALTT", "DSOS", "TOTIRRIG",
        # SOIL RATES
        "EVS", "EVW", "WTRA", "RIN", "RIRR", "PERC", "LOSS", "DW", "DWLOW", "DTSR", 
        "DSS", "DRAINT", 
        # NPK SOIL DYNAMICS STATES
        "NSOIL", "PSOIL", "KSOIL", "NAVAIL", "PAVAIL", "KAVAIL", "TOTN", "TOTP", "TOTK",
        "SURFACE_N", "SURFACE_P", "SURFACE_K", "TOTN_RUNOFF", "TOTP_RUNOFF", "TOTK_RUNOFF",
        # NPK SOIL DYNAMICS RATES
        "RNSOIL", "RPSOIL", "RKSOIL", "RNAVAIL", "RPAVAIL", "RKAVAIL", "FERT_N_SUPPLY",
        "FERT_P_SUPPLY", "FERT_K_SUPPLY", "RNSUBSOIL", "RPSUBSOIL", "RKSUBSOIL",
        "RRUNOFF_N", "RRUNOFF_P", "RRUNOFF_K",
        ]

    # Summary variables to save at CROP_FINISH signals
    # Set to an empty list if you do not want any SUMMARY_OUTPUT
    SUMMARY_OUTPUT_VARS = OUTPUT_VARS

    # Summary variables to save at TERMINATE signals
    # Set to an empty list if you do not want any TERMINAL_OUTPUT
    TERMINAL_OUTPUT_VARS = OUTPUT_VARS

    return {'SOIL': SOIL, 'CROP': CROP, 'AGROMANAGEMENT': AGROMANAGEMENT, 'OUTPUT_INTERVAL': OUTPUT_INTERVAL, \
            'OUTPUT_INTERVAL_DAYS':OUTPUT_INTERVAL_DAYS, 'OUTPUT_WEEKDAY': OUTPUT_WEEKDAY, \
                'OUTPUT_VARS': OUTPUT_VARS, 'SUMMARY_OUTPUT_VARS': SUMMARY_OUTPUT_VARS, \
                    'TERMINAL_OUTPUT_VARS': TERMINAL_OUTPUT_VARS}

def set_params(env: gym.Env, args: WOFOST_Args):
    """Sets editable WOFOST Model parameters by overriding the value
    in the configuration .yaml file
    
    Args:
        args - WOFOST_Args dataclass
    """

    # NPK Soil Dynamics params
    """Base soil supply of N available through mineralization kg/ha"""
    if args.NSOILBASE is not None:
        env.parameterprovider.set_override("NSOILBASE", args.NSOILBASE, check=False)  
    """Fraction of base soil N that comes available every day"""    
    if args.NSOILBASE_FR is not None:     
        env.parameterprovider.set_override("NSOILBASE_FR", args.NSOILBASE_FR, check=False)  
    """Base soil supply of P available through mineralization kg/ha"""
    if args.PSOILBASE is not None:
        env.parameterprovider.set_override("PSOILBASE", args.PSOILBASE, check=False)
    """Fraction of base soil P that comes available every day"""         
    if args.PSOILBASE_FR is not None:
        env.parameterprovider.set_override("PSOILBASE_FR", args.PSOILBASE_FR, check=False)
    """Base soil supply of K available through mineralization kg/ha"""
    if args.KSOILBASE is not None:
        env.parameterprovider.set_override("KSOILBASE", args.KSOILBASE, check=False)
    """Fraction of base soil K that comes available every day""" 
    if args.KSOILBASE_FR is not None:        
        env.parameterprovider.set_override("KSOILBASE_FR", args.KSOILBASE_FR, check=False)
    """Initial N available in the N pool (kg/ha)"""
    if args.NAVAILI is not None:
        env.parameterprovider.set_override("NAVAILI", args.NAVAILI, check=False)
    """Initial P available in the P pool (kg/ha)"""
    if args.PAVAILI is not None:
        env.parameterprovider.set_override("PAVAILI", args.PAVAILI, check=False)
    """Initial K available in the K pool (kg/ha)"""
    if args.KAVAILI is not None:
        env.parameterprovider.set_override("KAVAILI", args.KAVAILI, check=False)
    """Maximum N available in the N pool (kg/ha)"""
    if args.NMAX is not None:
        env.parameterprovider.set_override("NMAX", args.NMAX, check=False)
    """Maximum P available in the P pool (kg/ha)"""
    if args.PMAX is not None:
        env.parameterprovider.set_override("PMAX", args.PMAX, check=False)
    """Maximum K available in the K pool (kg/ha)"""
    if args.KMAX is not None:
        env.parameterprovider.set_override("KMAX", args.KMAX, check=False)
    """Background supply of N through atmospheric deposition (kg/ha/day)"""
    if args.BG_N_SUPPLY is not None:
        env.parameterprovider.set_override("BG_N_SUPPLY", args.BG_N_SUPPLY, check=False)
    """Background supply of P through atmospheric deposition (kg/ha/day)"""
    if args.BG_P_SUPPLY is not None:
        env.parameterprovider.set_override("BG_P_SUPPLY", args.BG_P_SUPPLY, check=False)
    """Background supply of K through atmospheric deposition (kg/ha/day)"""
    if args.BG_K_SUPPLY is not None:
        env.parameterprovider.set_override("BG_K_SUPPLY", args.BG_K_SUPPLY, check=False)
    """Maximum rate of surface N to subsoil"""
    if args.RNSOILMAX is not None:
        env.parameterprovider.set_override("RNSOILMAX", args.RNSOILMAX, check=False)
    """Maximum rate of surface P to subsoil"""
    if args.RPSOILMAX is not None:
        env.parameterprovider.set_override("RPSOILMAX", args.RPSOILMAX, check=False)  
    """Maximum rate of surface K to subsoil"""
    if args.RKSOILMAX is not None:
        env.parameterprovider.set_override("RKSOILMAX", args.RKSOILMAX, check=False)     
    """Relative rate of N absorption from surface to subsoil"""
    if args.RNABSORPTION is not None:
        env.parameterprovider.set_override("RNABSORPTION", args.RNABSORPTION, check=False)     
    """Relative rate of P absorption from surface to subsoil"""
    if args.RPABSORPTION is not None:
        env.parameterprovider.set_override("RPABSORPTION", args.RPABSORPTION, check=False)     
    """Relative rate of K absorption from surface to subsoil"""
    if args.RKABSORPTION is not None:
        env.parameterprovider.set_override("RKABSORPTION", args.RKABSORPTION, check=False) 
    """Relative rate of NPK runoff as a function of surface water runoff"""
    if args.RNPKRUNOFF is not None:
         env.parameterprovider.set_override("RNPKRUNOFF", args.RNPKRUNOFF, check=False) 
    # Waterbalance soil dynamics params
    """Field capacity of the soil"""
    if args.SMFCF is not None:
        env.parameterprovider.set_override("SMFCF", args.SMFCF, check=False)             
    """Porosity of the soil"""
    if args.SM0 is not None:
        env.parameterprovider.set_override("SM0", args.SM0, check=False)                            
    """Wilting point of the soil"""
    if args.SMW is not None:    
        env.parameterprovider.set_override("SMW", args.SMW, check=False)                  
    """Soil critical air content (waterlogging)"""
    if args.CRAIRC is not None:
        env.parameterprovider.set_override("CRAIRC", args.CRAIRC, check=False)
    """maximum percolation rate root zone (cm/day)"""
    if args.SOPE is not None:
        env.parameterprovider.set_override("SOPE", args.SOPE, check=False)
    """maximum percolation rate subsoil (cm/day)"""
    if args.KSUB is not None:
        env.parameterprovider.set_override("KSUB", args.KSUB, check=False)
    """Soil rootable depth (cm)"""
    if args.RDMSOL is not None:
        env.parameterprovider.set_override("RDMSOL", args.RDMSOL, check=False)                     
    """Indicates whether non-infiltrating fraction of rain is a function of storm size (1) or not (0)"""
    if args.IFUNRN is not None:
        env.parameterprovider.set_override("IFUNRN", args.IFUNRN, check=False)
    """Maximum surface storage (cm)"""                               
    if args.SSMAX is not None:
        env.parameterprovider.set_override("SSMAX", args.SSMAX, check=False)               
    """Initial surface storage (cm)"""
    if args.SSI is not None:
        env.parameterprovider.set_override("SSI", args.SSI, check=False)   
    """Initial amount of water in total soil profile (cm)"""
    if args.WAV is not None:
        env.parameterprovider.set_override("WAV", args.WAV, check=False)
    """Maximum fraction of rain not-infiltrating into the soil"""
    if args.NOTINF is not None:   
        env.parameterprovider.set_override("NOTINF", args.NOTINF, check=False)
    """Initial maximum moisture content in initial rooting depth zone"""
    if args.SMLIM is not None:
        env.parameterprovider.set_override("SMLIM", args.SMLIM, check=False)


    # WOFOST Parameters
    """Conversion factor for assimilates to leaves"""
    if args.CVL is not None:
        env.parameterprovider.set_override("CVL", args.CVL, check=False)
    """Conversion factor for assimilates to storage organs"""
    if args.CVO is not None:
        env.parameterprovider.set_override("CVO", args.CVO, check=False)
    """Conversion factor for assimilates to roots"""  
    if args.CVR is not None:
        env.parameterprovider.set_override("CVR", args.CVR, check=False)
    """Conversion factor for assimilates to stems"""
    if args.CVS is not None:
        env.parameterprovider.set_override("CVS", args.CVS, check=False)

    # Assimilation Parameters
    """ Max leaf |CO2| assim. rate as a function of of DVS (kg/ha/hr)"""
    if args.AMAXTB is not None:
        env.parameterprovider.set_override("AMAXTB", args.AMAXTB, check=False)
    """ Light use effic. single leaf as a function of daily mean temperature |kg ha-1 hr-1 /(J m-2 s-1)|"""
    if args.EFFTB is not None:
        env.parameterprovider.set_override("EFFTB", args.EFFTB, check=False)
    """Extinction coefficient for diffuse visible as function of DVS"""
    if args.KDIFTB is not None:
        env.parameterprovider.set_override("KDIFTB", args.KDIFTB, check=False)
    """Reduction factor of AMAX as function of daily mean temperature"""
    if args.TMPFTB is not None:
        env.parameterprovider.set_override("TMPFTB", args.TMPFTB, check=False)
    """Reduction factor of AMAX as function of daily minimum temperature"""
    if args.TMNFTB is not None:
        env.parameterprovider.set_override("TMNFTB", args.TMNFTB, check=False)
    """Correction factor for AMAX given atmospheric CO2 concentration.""" 
    if args.CO2AMAXTB is not None:
        env.parameterprovider.set_override("CO2AMAXTB", args.CO2AMAXTB, check=False)
    """Correction factor for EFF given atmospheric CO2 concentration."""
    if args.CO2EFFTB is not None:
        env.parameterprovider.set_override("CO2EFFTB", args.CO2EFFTB, check=False)
    """Atmopheric CO2 concentration (ppm)"""
    if args.CO2 is not None:
        env.parameterprovider.set_override("CO2", args.CO2, check=False)

    # Evapotranspiration Parameters
    """Correction factor for potential transpiration rate"""
    if args.CFET is not None:
        env.parameterprovider.set_override("CFET", args.CFET, check=False)
    """Dependency number for crop sensitivity to soil moisture stress."""  
    if args.DEPNR is not None:
        env.parameterprovider.set_override("DEPNR", args.DEPNR, check=False)
    """Extinction coefficient for diffuse visible as function of DVS.""" 
    if args.KDIFTB is not None:
        env.parameterprovider.set_override("KDIFTB", args.KDIFTB, check=False)
    """Switch oxygen stress on (1) or off (0)"""
    if args.IOX is not None:
        env.parameterprovider.set_override("IOX", args.IOX, check=False)
    """Switch airducts on (1) or off (0) """ 
    if args.IAIRDU is not None:   
        env.parameterprovider.set_override("IAIRDU", args.IAIRDU, check=False)
    """Critical air content for root aeration"""  
    if args.CRAIRC is not None:
        env.parameterprovider.set_override("CRAIRC", args.CRAIRC, check=False)
    """Soil porosity"""
    if args.SM0 is not None:
        env.parameterprovider.set_override("SM0", args.SM0, check=False)
    """Volumetric soil moisture content at wilting point"""
    if args.SMW is not None:   
        env.parameterprovider.set_override("SMW", args.SMW, check=False)
    """Volumetric soil moisture content at field capacity"""  
    if args.SMFCF is not None:   
        env.parameterprovider.set_override("SMFCF", args.SMFCF, check=False)
    """Soil porosity"""    
    if args.SM0 is not None:
        env.parameterprovider.set_override("SM0", args.SM0, check=False)
    """Atmospheric CO2 concentration (ppm)"""  
    if args.CO2 is not None:
        env.parameterprovider.set_override("CO2", args.CO2, check=False)
    """Reduction factor for TRAMX as function of atmospheric CO2 concentration"""   
    if args.CO2TRATB is not None:   
        env.parameterprovider.set_override("CO2TRATB", args.CO2TRATB, check=False)

    # Leaf Dynamics Parameters
    """Maximum relative increase in LAI (ha / ha d)"""
    if args.RGRLAI is not None:
        env.parameterprovider.set_override("RGRLAI", args.RGRLAI, check=False)
    """Life span of leaves growing at 35 Celsius (days)""" 
    if args.SPAN is not None:         
        env.parameterprovider.set_override("SPAN", args.SPAN, check=False)
    """Lower threshold temp for ageing of leaves (C)""" 
    if args.TBASE is not None: 
        env.parameterprovider.set_override("TBASE", args.TBASE, check=False)
    """Max relative death rate of leaves due to water stress"""  
    if args.PERDL is not None:
        env.parameterprovider.set_override("PERDL", args.PERDL, check=False)
    """Initial total crop dry weight (kg/ha)"""
    if args.TDWI is not None:
        env.parameterprovider.set_override("TDWI", args.TDWI, check=False)
    """Extinction coefficient for diffuse visible light as function of DVS"""
    if args.KDIFTB is not None:
        env.parameterprovider.set_override("KDIFTB", args.KDIFTB, check=False)
    """Specific leaf area as a function of DVS (ha/kg)"""
    if args.SLATB is not None:
        env.parameterprovider.set_override("SLATB", args.SLATB, check=False)
    """Maximum relative death rate of leaves due to nutrient NPK stress"""
    if args.RDRNS is not None:  
        env.parameterprovider.set_override("RDRNS", args.RDRNS, check=False)
    """coefficient for the reduction due to nutrient NPK stress of the LAI increas
            (during juvenile phase)"""
    if args.NLAI is not None:
        env.parameterprovider.set_override("NLAI", args.NLAI, check=False)
    """Coefficient for the effect of nutrient NPK stress on SLA reduction""" 
    if args.NSLA is not None:
        env.parameterprovider.set_override("NSLA", args.NSLA, check=False)
    """Max. relative death rate of leaves due to nutrient NPK stress"""   
    if args.RDRN is not None:
        env.parameterprovider.set_override("RDRN", args.RDRN, check=False)

    # NPK Dynamics Parameters
    """Maximum N concentration in leaves as function of DVS (kg N / kg dry biomass)"""
    if args.NMAXLV_TB is not None:
        env.parameterprovider.set_override("NMAXLV_TB", args.NMAXLV_TB, check=False)
    """Maximum P concentration in leaves as function of DVS (kg P / kg dry biomass)"""
    if args.PMAXLV_TB is not None:
        env.parameterprovider.set_override("PMAXLV_TB", args.PMAXLV_TB, check=False) 
    """Maximum K concentration in leaves as function of DVS (kg K / kg dry biomass)"""
    if args.KMAXLV_TB is not None:
        env.parameterprovider.set_override("KMAXLV_TB", args.KMAXLV_TB, check=False)
    """Maximum N concentration in roots as fraction of maximum N concentration in leaves"""
    if args.NMAXRT_FR is not None:
        env.parameterprovider.set_override("NMAXRT_FR", args.NMAXRT_FR, check=False)
    """Maximum P concentration in roots as fraction of maximum P concentration in leaves"""
    if args.PMAXRT_FR is not None:
        env.parameterprovider.set_override("PMAXRT_FR", args.PMAXRT_FR, check=False)
    """Maximum K concentration in roots as fraction of maximum K concentration in leaves"""
    if args.KMAXRT_FR is not None:
        env.parameterprovider.set_override("KMAXRT_FR", args.KMAXRT_FR, check=False)
    """Maximum N concentration in stems as fraction of maximum N concentration in leaves"""
    if args.NMAXST_FR is not None:
        env.parameterprovider.set_override("NMAXST_FR", args.NMAXST_FR, check=False)
    """Maximum P concentration in stems as fraction of maximum P concentration in leaves"""
    if args.PMAXST_FR is not None:
        env.parameterprovider.set_override("PMAXST_FR", args.PMAXST_FR, check=False)
    """Maximum K concentration in stems as fraction of maximum K concentration in leaves"""
    if args.KMAXST_FR is not None:
        env.parameterprovider.set_override("KMAXST_FR", args.KMAXST_FR, check=False)   
    
    """Residual N fraction in leaves (kg N / kg dry biomass)"""
    if args.NRESIDLV is not None:
        env.parameterprovider.set_override("NRESIDLV", args.NRESIDLV, check=False) 
    """Residual P fraction in leaves (kg P / kg dry biomass)"""
    if args.PRESIDLV is not None:
        env.parameterprovider.set_override("PRESIDLV", args.PRESIDLV, check=False)
    """Residual K fraction in leaves (kg K / kg dry biomass)"""
    if args.KRESIDLV is not None:
        env.parameterprovider.set_override("KRESIDLV", args.KRESIDLV, check=False)

    """Residual N fraction in roots (kg N / kg dry biomass)"""
    if args.NRESIDRT is not None:
        env.parameterprovider.set_override("NRESIDRT", args.NRESIDRT, check=False)              
    """Residual P fraction in roots (kg P / kg dry biomass)"""
    if args.PRESIDRT is not None:
        env.parameterprovider.set_override("PRESIDRT", args.PRESIDRT, check=False)
    """Residual K fraction in roots (kg K / kg dry biomass)"""
    if args.KRESIDRT is not None:
        env.parameterprovider.set_override("KRESIDRT", args.KRESIDRT, check=False)
    """Residual N fraction in stems (kg N / kg dry biomass)"""
    if args.NRESIDST is not None:
        env.parameterprovider.set_override("NRESIDST", args.NRESIDST, check=False)
    """Residual P fraction in stems (kg P / kg dry biomass)"""  
    if args.PRESIDST is not None:                      
        env.parameterprovider.set_override("PRESIDST", args.PRESIDST, check=False)
    """Residual K fraction in stems (kg K / kg dry biomass)"""
    if args.KRESIDST is not None:
        env.parameterprovider.set_override("KRESIDST", args.KRESIDST, check=False)

    # Partioning Parameters
    """Partitioning to roots as a function of development stage"""
    if args.FRTB is not None:
        env.parameterprovider.set_override("FRTB", args.FRTB, check=False)
    """Partitioning to stems as a function of development stage"""
    if args.FSTB is not None:
        env.parameterprovider.set_override("FSTB", args.FSTB, check=False)
    """Partitioning to leaves as a function of development stage"""
    if args.FLTB is not None:
        env.parameterprovider.set_override("FLTB", args.FLTB, check=False)
    """Partitioning to starge organs as a function of development stage"""
    if args.FOTB is not None:
        env.parameterprovider.set_override("FOTB", args.FOTB, check=False)
    """Coefficient for the effect of N stress on leaf biomass allocation"""
    if args.NPART is not None:
        env.parameterprovider.set_override("NPART", args.NPART, check=False)
    """Threshold above which surface nitrogen induces stress"""
    if args.NTHRESH is not None:
        env.parameterprovider.set_override("NTHRESH", args.NTHRESH, check=False)
    """Threshold above which surface phosphorous induces stress"""
    if args.PTHRESH is not None:
        env.parameterprovider.set_override("PTHRESH", args.PTHRESH, check=False)
    """Threshold above which surface potassium induces stress"""
    if args.KTHRESH is not None:
        env.parameterprovider.set_override("KTHRESH", args.KTHRESH, check=False)

    # Vernalization Parameters
    """Saturated vernalisation requirements (days)"""
    if args.VERNSAT is not None:
        env.parameterprovider.set_override("VERNSAT", args.VERNSAT, check=False)
    """Base vernalisation requirements (days)"""
    if args.VERNBASE is not None:
        env.parameterprovider.set_override("VERNBASE", args.VERNBASE, check=False)
    """Rate of vernalisation as a function of daily mean temperature"""
    if args.VERNRTB is not None:
        env.parameterprovider.set_override("VERNRTB", args.VERNRTB, check=False)
    """Critical development stage after which the effect of vernalisation is halted"""
    if args.VERNDVS is not None:
        env.parameterprovider.set_override("VERNDVS", args.VERNDVS, check=False)

    # Phenology Parameters
    """Number of days above TSUMEM for germination to occur"""
    if args.DTBEM is not None:
        env.parameterprovider.set_override("DTBEM", args.DTBEM, check=False)
    """Temperature sum from sowing to emergence (C day)"""
    if args.TSUMEM is not None:
        env.parameterprovider.set_override("TSUMEM", args.TSUMEM, check=False)
    """Base temperature for emergence (C)"""
    if args.TBASEM is not None:
        env.parameterprovider.set_override("TBASEM", args.TBASEM, check=False)
    """Maximum effective temperature for emergence (C day)"""
    if args.TEFFMX is not None:
        env.parameterprovider.set_override("TEFFMX", args.TEFFMX, check=False)
    """Temperature sum from emergence to anthesis (C day)"""
    if args.TSUM1 is not None:
        env.parameterprovider.set_override("TSUM1", args.TSUM1, check=False)
    """Temperature sum from anthesis to maturity (C day)"""
    if args.TSUM2 is not None:
        env.parameterprovider.set_override("TSUM2", args.TSUM2, check=False)
    """Switch for phenological development options temperature only (IDSL=0), 
    including daylength (IDSL=1) and including vernalization (IDSL>=2)"""
    if args.IDSL is not None:
        env.parameterprovider.set_override("IDSL", args.IDSL, check=False)
    """Optimal daylength for phenological development (hr)"""
    if args.DLO is not None:
        env.parameterprovider.set_override("DLO", args.DLO, check=False)
    """Critical daylength for phenological development (hr)"""
    if args.DLC is not None:
        env.parameterprovider.set_override("DLC", args.DLC, check=False)
    """Initial development stage at emergence. Usually this is zero, but it can 
    be higher or crops that are transplanted (e.g. paddy rice)"""
    if args.DVSI is not None:
        env.parameterprovider.set_override("DVSI", args.DVSI, check=False)
    """Mature Development Stage"""
    if args.DVSM is not None:
        env.parameterprovider.set_override("DVSM", args.DVSM, check=False)
    """Final development stage"""
    if args.DVSEND is not None:
        env.parameterprovider.set_override("DVSEND", args.DVSEND, check=False)
    """Daily increase in temperature sum as a function of daily mean temperature (C)"""  
    if args.DTSMTB is not None:             
        env.parameterprovider.set_override("DTSMTB", args.DTSMTB, check=False)
    """Dormancy threshold after which plant becomes dormant (days)"""
    if args.DORM is not None:
        env.parameterprovider.set_override("DORM", args.DORM, check=False)
    """Minimum length of dormancy state"""
    if args.DORMCD is not None:
        env.parameterprovider.set_override("DORMCD", args.DORMCD, check=False)  
    """Initial age of crop (years)"""
    if args.AGEI is not None:
        env.parameterprovider.set_override("AGEI", args.AGEI, check=False)  
    """Daylength dormancy threshold"""
    if args.MLDORM is not None:
        env.parameterprovider.set_override("MLDORM", args.MLDORM, check=False)  

    # Respiration Parameters
    """Relative increase in maintenance repiration rate with each 10 degrees increase in temperature"""
    if args.Q10 is not None:
        env.parameterprovider.set_override("Q10", args.Q10, check=False)
    """Relative maintenance respiration rate for roots |kg CH2O kg-1 d-1|"""
    if args.RMR is not None:
        env.parameterprovider.set_override("RMR", args.RMR, check=False)
    """ Relative maintenance respiration rate for stems |kg CH2O kg-1 d-1| """   
    if args.RMS is not None:
        env.parameterprovider.set_override("RMS", args.RMS, check=False)
    """Relative maintenance respiration rate for leaves |kg CH2O kg-1 d-1|""" 
    if args.RML is not None:
        env.parameterprovider.set_override("RML", args.RML, check=False)                              
    """Relative maintenance respiration rate for storage organs |kg CH2O kg-1 d-1|"""
    if args.RMO is not None:
        env.parameterprovider.set_override("RMO", args.RMO, check=False)
    """Reduction factor  for senescence as function of DVS"""
    if args.RFSETB is not None:
        env.parameterprovider.set_override("RFSETB", args.RFSETB, check=False)

    # Root Dynamics Parameters
    """Initial rooting depth (cm)"""
    if args.RDI is not None:
        env.parameterprovider.set_override("RDI", args.RDI, check=False)
    """Daily increase in rooting depth  |cm day-1|"""
    if args.RRI is not None:
        env.parameterprovider.set_override("RRI", args.RRI, check=False)
    """Maximum rooting depth of the crop (cm)""" 
    if args.RDMCR is not None:
        env.parameterprovider.set_override("RDMCR", args.RDMCR, check=False)
    """Maximum rooting depth of the soil (cm)"""
    if args.RDMSOL is not None:
        env.parameterprovider.set_override("RDMSOL", args.RDMSOL, check=False)
    """Initial total crop dry weight |kg ha-1|"""
    if args.TDWI is not None:
        env.parameterprovider.set_override("TDWI", args.TDWI, check=False)
    """Presence of air ducts in the root (1) or not (0)""" 
    if args.IAIRDU is not None:
        env.parameterprovider.set_override("IAIRDU", args.IAIRDU, check=False)
    """Relative death rate of roots as a function of development stage"""
    if args.RDRRTB is not None:
        env.parameterprovider.set_override("RDRRTB", args.RDRRTB, check=False)
    """Relative death rate of roots as a function of oxygen stress (over watering)"""
    if args.RDRROS is not None:
        env.parameterprovider.set_override("RDRROS", args.RDRROS, check=False)
    """Relative death rate of roots as a function of excess NPK on surface"""
    if args.RDRRNPK is not None:
        env.parameterprovider.set_override("RDRRNPK", args.RDRRNPK, check=False)

    # Stem Dynamics Parameters
    """Initial total crop dry weight (kg/ha)"""
    if args.TDWI is not None:
        env.parameterprovider.set_override("TDWI", args.TDWI, check=False)
    """Relative death rate of stems as a function of development stage"""
    if args.RDRSTB is not None:
        env.parameterprovider.set_override("RDRSTB", args.RDRSTB, check=False)
    """Specific Stem Area as a function of development stage (ha/kg)"""
    if args.SSATB is not None:
        env.parameterprovider.set_override("SSATB", args.SSATB, check=False)

    # Storage Organs Dynamics Parameters
    """Initial total crop dry weight (kg/ha)"""
    if args.TDWI is not None:
        env.parameterprovider.set_override("TDWI", args.TDWI, check=False)
    """Relative death rate of storage organs as a function of development stage"""
    if args.RDRSOB is not None:
        env.parameterprovider.set_override("RDRSOB", args.RDRSOB, check=False) 
    """Specific Pod Area (ha / kg)""" 
    if args.SPA is not None:
        env.parameterprovider.set_override("SPA", args.SPA, check=False)
    """Relative death rate of storage organs as a function of frost kill"""
    if args.RDRSOF is not None:
        env.parameterprovider.set_override("RDRSOF", args.RDRSOF, check=False) 
    
    # NPK Demand Uptake Parameters
    """DVS above which NPK uptake halts"""
    if args.DVS_NPK_STOP is not None:
        env.parameterprovider.set_override("DVS_NPK_STOP", args.DVS_NPK_STOP, check=False)
    """Maximum N concentration in leaves as function of DVS (kg N / kg dry biomass)"""
    if args.NMAXLV_TB is not None:
        env.parameterprovider.set_override("NMAXLV_TB", args.NMAXLV_TB, check=False)
    """Maximum P concentration in leaves as function of DVS (kg P / kg dry biomass)"""
    if args.PMAXLV_TB is not None:
        env.parameterprovider.set_override("PMAXLV_TB", args.PMAXLV_TB, check=False)
    """Maximum K concentration in leaves as function of DVS (kg K / kg dry biomass)"""
    if args.KMAXLV_TB is not None:
        env.parameterprovider.set_override("KMAXLV_TB", args.KMAXLV_TB, check=False)
    """ Maximum N concentration in roots as fraction of maximum N concentration in leaves"""
    if args.NMAXRT_FR is not None:
        env.parameterprovider.set_override("NMAXRT_FR", args.NMAXRT_FR, check=False)
    """Maximum P concentration in roots as fraction of maximum P concentration in leaves"""
    if args.PMAXRT_FR is not None:
        env.parameterprovider.set_override("PMAXRT_FR", args.PMAXRT_FR, check=False)   
    """Maximum K concentration in roots as fraction  of maximum K concentration in leaves"""
    if args.KMAXRT_FR is not None:
        env.parameterprovider.set_override("KMAXRT_FR", args.KMAXRT_FR, check=False)  
    """Maximum N concentration in stems as fraction of maximum N concentration in leaves"""
    if args.NMAXST_FR is not None:
        env.parameterprovider.set_override("NMAXST_FR", args.NMAXST_FR, check=False)
    """Maximum P concentration in stems as fraction of maximum P concentration in leaves"""
    if args.PMAXST_FR is not None:
        env.parameterprovider.set_override("PMAXST_FR", args.PMAXST_FR, check=False)
    """Maximum K concentration in stems as fraction of maximum K concentration in leaves"""
    if args.KMAXST_FR is not None:
        env.parameterprovider.set_override("KMAXST_FR", args.KMAXST_FR, check=False)
    """ Maximum N concentration in storage organs (kg N / kg dry biomass)"""
    if args.NMAXSO is not None:
        env.parameterprovider.set_override("NMAXSO", args.NMAXSO, check=False)
    """Maximum P concentration in storage organs (kg P / kg dry biomass)"""
    if args.PMAXSO is not None:  
        env.parameterprovider.set_override("PMAXSO", args.PMAXSO, check=False)
    """Maximum K concentration in storage organs (kg K / kg dry biomass)""" 
    if args.KMAXSO is not None:         
        env.parameterprovider.set_override("KMAXSO", args.KMAXSO, check=False)
    """Critical N concentration as fraction of maximum N concentration for vegetative
                    plant organs as a whole (leaves + stems)"""
    if args.NCRIT_FR is not None:
        env.parameterprovider.set_override("NCRIT_FR", args.NCRIT_FR, check=False)
    """Critical P concentration as fraction of maximum P concentration for vegetative
                    plant organs as a whole (leaves + stems)"""
    if args.PCRIT_FR is not None:
        env.parameterprovider.set_override("PCRIT_FR", args.PCRIT_FR, check=False)
    """Critical K concentration as fraction of maximum K concentration for vegetative
                    plant organs as a whole (leaves + stems)"""
    if args.KCRIT_FR is not None:
        env.parameterprovider.set_override("KCRIT_FR", args.KCRIT_FR, check=False)
    
    """Time coefficient for N translation to storage organs (days)"""
    if args.TCNT is not None:
        env.parameterprovider.set_override("TCNT", args.TCNT, check=False)
    """Time coefficient for P translation to storage organs (days)"""
    if args.TCPT is not None:
        env.parameterprovider.set_override("TCPT", args.TCPT, check=False)    
    """Time coefficient for K translation to storage organs (days)"""
    if args.TCKT is not None:
        env.parameterprovider.set_override("TCKT", args.TCKT, check=False)
    """fraction of crop nitrogen uptake by biological fixation (kg N / kg dry biomass)"""
    if args.NFIX_FR is not None:
        env.parameterprovider.set_override("NFIX_FR", args.NFIX_FR, check=False)
    """Maximum rate of N uptake (kg N / ha day)"""
    if args.RNUPTAKEMAX is not None:
        env.parameterprovider.set_override("RNUPTAKEMAX", args.RNUPTAKEMAX, check=False)
    """Maximum rate of P uptake (kg P / ha day)"""
    if args.RPUPTAKEMAX is not None:
        env.parameterprovider.set_override("RPUPTAKEMAX", args.RPUPTAKEMAX, check=False)
    """Maximum rate of K uptake (kg K / ha day)"""
    if args.RKUPTAKEMAX is not None:
        env.parameterprovider.set_override("RKUPTAKEMAX", args.RKUPTAKEMAX, check=False)     

    # NPK Stress Parameters
    """Maximum N concentration in leaves as function of DVS (kg N kg-1 dry biomass)"""
    if args.NMAXLV_TB is not None:
        env.parameterprovider.set_override("NMAXLV_TB", args.NMAXLV_TB, check=False)   
    """Maximum P concentration in leaves as function of DVS (kg N / kg dry biomass)"""
    if args.PMAXLV_TB is not None:
        env.parameterprovider.set_override("PMAXLV_TB", args.PMAXLV_TB, check=False)
    """Maximum K concentration in leaves as function of DVS (kg N / kg dry biomass)"""
    if args.KMAXLV_TB is not None:
        env.parameterprovider.set_override("KMAXLV_TB", args.KMAXLV_TB, check=False)
    """Maximum N concentration in roots as fraction of maximum N concentration in leaves"""
    if args.NMAXRT_FR is not None:
        env.parameterprovider.set_override("NMAXRT_FR", args.NMAXRT_FR, check=False)
    """Maximum P concentration in roots as fraction of maximum P concentration in leaves"""
    if args.PMAXRT_FR is not None:
        env.parameterprovider.set_override("PMAXRT_FR", args.PMAXRT_FR, check=False)
    """Maximum K concentration in roots as fraction of maximum K concentration in leaves"""
    if args.KMAXRT_FR is not None:
        env.parameterprovider.set_override("KMAXRT_FR", args.KMAXRT_FR, check=False)
    """Maximum N concentration in stems as fraction of maximum N concentration in leaves"""
    if args.NMAXST_FR is not None:
        env.parameterprovider.set_override("NMAXST_FR", args.NMAXST_FR, check=False)
    """Maximum P concentration in stems as fraction of maximum P concentration in leaves"""
    if args.PMAXST_FR is not None:
        env.parameterprovider.set_override("PMAXST_FR", args.PMAXST_FR, check=False)  
    """Maximum K concentration in stems as fraction of maximum K concentration in leaves"""
    if args.KMAXST_FR is not None:
        env.parameterprovider.set_override("KMAXST_FR", args.KMAXST_FR, check=False)
    """Critical N concentration as fraction of maximum N concentration for vegetative
                    plant organs as a whole (leaves + stems)"""
    if args.NCRIT_FR is not None:
        env.parameterprovider.set_override("NCRIT_FR", args.NCRIT_FR, check=False)  
    """Critical P concentration as fraction of maximum P concentration for vegetative
                    plant organs as a whole (leaves + stems)"""
    if args.PCRIT_FR is not None:
        env.parameterprovider.set_override("PCRIT_FR", args.PCRIT_FR, check=False)    
    """Critical K concentration as fraction of maximum L concentration for 
    vegetative plant organs as a whole (leaves + stems)"""
    if args.KCRIT_FR is not None:
        env.parameterprovider.set_override("KCRIT_FR", args.KCRIT_FR, check=False)
    """Residual N fraction in leaves (kg N / kg dry biomass)"""
    if args.NRESIDLV is not None:
        env.parameterprovider.set_override("NRESIDLV", args.NRESIDLV, check=False)
    """Residual P fraction in leaves (kg P / kg dry biomass)"""
    if args.PRESIDLV is not None:
        env.parameterprovider.set_override("PRESIDLV", args.PRESIDLV, check=False)
    """Residual K fraction in leaves (kg K / kg dry biomass)"""
    if args.KRESIDLV is not None:
        env.parameterprovider.set_override("KRESIDLV", args.KRESIDLV, check=False)               
    """Residual N fraction in stems (kg N / kg dry biomass)"""
    if args.NRESIDST is not None:
        env.parameterprovider.set_override("NRESIDST", args.NRESIDST, check=False)
    """Residual P fraction in stems (kg P/ kg dry biomass)"""
    if args.PRESIDST is not None:
        env.parameterprovider.set_override("PRESIDST", args.PRESIDST, check=False)
    """Residual K fraction in stems (kg K/ kg dry biomass)"""
    if args.KRESIDST is not None:
        env.parameterprovider.set_override("KRESIDST", args.KRESIDST, check=False)   
    """Coefficient for the reduction of RUE due to nutrient (N-P-K) stress"""
    if args.NLUE_NPK is not None:
        env.parameterprovider.set_override("NLUE_NPK", args.NLUE_NPK, check=False)

    # NPK Translocation Parameters
    """Residual N fraction in leaves (kg N / kg dry biomass)""" 
    if args.NRESIDLV is not None:
        env.parameterprovider.set_override("NRESIDLV", args.NRESIDLV, check=False)
    """Residual P fraction in leaves (kg P / kg dry biomass)""" 
    if args.PRESIDLV is not None:
        env.parameterprovider.set_override("PRESIDLV", args.PRESIDLV, check=False)
    """Residual K fraction in leaves (kg K / kg dry biomass)"""
    if args.KRESIDLV is not None: 
        env.parameterprovider.set_override("KRESIDLV", args.KRESIDLV, check=False)  
    """Residual N fraction in stems (kg N / kg dry biomass)""" 
    if args.NRESIDST is not None:
        env.parameterprovider.set_override("NRESIDST", args.NRESIDST, check=False)
    """Residual K fraction in stems (kg P / kg dry biomass)"""
    if args.PRESIDST is not None: 
        env.parameterprovider.set_override("PRESIDST", args.PRESIDST, check=False)
    """Residual P fraction in stems (kg K / kg dry biomass)"""
    if args.KRESIDST is not None: 
        env.parameterprovider.set_override("KRESIDST", args.KRESIDST, check=False)      
    """NPK translocation from roots as a fraction of resp. total NPK amounts translocated from leaves and stems"""
    if args.NPK_TRANSLRT_FR is not None:
        env.parameterprovider.set_override("NPK_TRANSLRT_FR", args.NPK_TRANSLRT_FR, check=False)
    """DVS above which translocation to storage organs occurs"""
    if args.DVS_NPK_TRANSL is not None:
        env.parameterprovider.set_override("DVS_NPK_TRANSL", args.DVS_NPK_TRANSL, check=False)

def set_agro_params(agromanagement: dict, args: Agro_Args):

    """Sets editable Agromanagement parameters by modifying the agromanagement
    dictionary before being passed to the AgroManager Module
    
    Args:
        args - Agro_Args dataclass
    """
    if args.latitude is not None:
        agromanagement['SiteCalendar']['latitude'] = args.latitude
    if args.longitude is not None: 
        agromanagement['SiteCalendar']['longitude'] = args.longitude
    if args.year is not None:
        agromanagement['SiteCalendar']['year'] = args.year
    if args.site_name is not None:
        agromanagement['SiteCalendar']['site_name'] = args.site_name
    if args.site_variation is not None:
        agromanagement['SiteCalendar']['site_variation'] = args.site_variation
    if args.site_start_date is not None:
        agromanagement['SiteCalendar']['site_start_date'] = datetime.strptime(args.site_start_date, '%Y-%m-%d').date()
    if args.site_end_date is not None:
        agromanagement['SiteCalendar']['site_end_date'] = datetime.strptime(args.site_end_date, '%Y-%m-%d').date()
    if args.crop_name is not None:
        agromanagement['CropCalendar']['crop_name'] = args.crop_name
    if args.crop_variety is not None:
        agromanagement['CropCalendar']['crop_variety'] = args.crop_variety
    if args.crop_start_date is not None:
        agromanagement['CropCalendar']['crop_start_date'] = datetime.strptime(args.crop_start_date, '%Y-%m-%d').date()
    if args.crop_start_type is not None:
        agromanagement['CropCalendar']['crop_start_type'] = args.crop_start_type
    if args.crop_end_date is not None:
        agromanagement['CropCalendar']['crop_end_date'] = datetime.strptime(args.crop_end_date, '%Y-%m-%d').date()
    if args.crop_end_type is not None:
        agromanagement['CropCalendar']['crop_end_type'] = args.crop_end_type
    if args.max_duration is not None:
        agromanagement['CropCalendar']['max_duration'] = args.max_duration

    return agromanagement

class ParamLoader():
    """
    Class to handle loading the parameter and state/rate names of all variables
    """
    def __init__(self, base_fpath:str=None, name_fpath:str=None, unit_fpath:str=None, range_fpath:str=None):
        """
        Initialize State by loading respective .yaml files as specified in utils.Args
        """
        try: 
            with open(f"{base_fpath}{name_fpath}", "rb") as f:
                self.state_names = yaml.safe_load(f) 
        except:
            msg = f"Error loading State Names file `{base_fpath}{name_fpath}`. Check correct path or that file exists."
            raise Exception(msg)
        
        try: 
            with open(f"{base_fpath}{unit_fpath}", "rb") as f:
                self.state_units = yaml.safe_load(f) 
        except:
            msg = f"Error loading State Names file `{base_fpath}{unit_fpath}`. Check correct path or that file exists."
            raise Exception(msg)
        
        try: 
            with open(f"{base_fpath}{range_fpath}", "rb") as f:
                self.state_range = yaml.safe_load(f) 
        except:
            msg = f"Error loading State Ranges file `{base_fpath}{range_fpath}`. Check correct path or that file exists."
            raise Exception(msg)
        
    def get_name(self, key:str):
        """
        Get the name of a specific key
        """
        try:
            return self.state_names[key]
        except:
            msg = f"`{key}` not found in State Names YAML file. Check that key exists in file."
            raise Exception(msg)
        
    def get_unit(self, key:str):
        """
        Get the unit of a specific key
        """
        try:
            return self.state_units[key]
        except:
            msg = f"`{key}` not found in State Units YAML file. Check that key exists in file."
            raise Exception(msg)
        
    def get_range(self, key:str):
        """
        Get the range of a specific key
        """
        try: 
            val = self.state_range[key]
            return np.array(list(val), dtype=np.float64)
        except:
            msg = f"`{key}` not found in State Range YAML file. Check that key exists in file."
            raise Exception(msg)
        
    def normalize(self, key:str, obs:float):
        """
        Get the range of a specific key and normalize
        """
        try: 
            range = np.array(list(self.state_range[key]), dtype=np.float64)
            return (obs - range[0]) / (range[1]-range[0] + 1e-12)
        except:
            msg = f"`{key}` not found in State Range YAML file. Check that key exists in file."
            raise Exception(msg)


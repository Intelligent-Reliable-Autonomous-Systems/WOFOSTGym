"""Args configurations file includes: 
    - PCSE configuration file for WOFOST 8.0 Water and NPK limited Production
    - WOFOST Gym parameter configurations
"""

from dataclasses import dataclass, field
from typing import Optional, List
import os

@dataclass
class WOFOST_Args:
    """Dataclass to be used for configuration WOFOST crop and soil model

    If left to default of None, values will be drawn from the .yaml files in 
    /env_config/crop_config/ and /env_config/soil_config/
    """

    # NPK Soil Dynamics params
    """Base soil supply of N available through mineralization kg/ha"""
    NSOILBASE: Optional[float] = None   
    """Fraction of base soil N that comes available every day"""         
    NSOILBASE_FR: Optional[float] = None 
    """Base soil supply of P available through mineralization kg/ha"""
    PSOILBASE: Optional[float] = None   
    """Fraction of base soil P that comes available every day"""         
    PSOILBASE_FR: Optional[float] = None 
    """Base soil supply of K available through mineralization kg/ha"""
    KSOILBASE: Optional[float] = None   
    """Fraction of base soil K that comes available every day"""         
    KSOILBASE_FR: Optional[float] = None 
    """Initial N available in the N pool (kg/ha)"""
    NAVAILI: Optional[float] = None
    """Initial P available in the P pool (kg/ha)"""
    PAVAILI: Optional[float] = None
    """Initial K available in the K pool (kg/ha)"""
    KAVAILI: Optional[float] = None
    """Maximum N available in the N pool (kg/ha)"""
    NMAX: Optional[float] = None
    """Maximum P available in the P pool (kg/ha)"""
    PMAX: Optional[float] = None
    """Maximum K available in the K pool (kg/ha)"""
    KMAX: Optional[float] = None
    """Background supply of N through atmospheric deposition (kg/ha/day)"""
    BG_N_SUPPLY: Optional[float] = None
    """Background supply of P through atmospheric deposition (kg/ha/day)"""
    BG_P_SUPPLY: Optional[float] = None
    """Background supply of K through atmospheric deposition (kg/ha/day)"""
    BG_K_SUPPLY: Optional[float] = None
    """Maximum rate of surface N to subsoil"""
    RNSOILMAX: Optional[float] = None
    """Maximum rate of surface P to subsoil"""
    RPSOILMAX: Optional[float] = None     
    """Maximum rate of surface K to subsoil"""
    RKSOILMAX: Optional[float] = None     
    """Relative rate of N absorption from surface to subsoil"""
    RNABSORPTION: Optional[float] = None  
    """Relative rate of P absorption from surface to subsoil"""
    RPABSORPTION: Optional[float] = None  
    """Relative rate of K absorption from surface to subsoil"""
    RKABSORPTION: Optional[float] = None 
    """Relative rate of NPK runoff as a function of surface water runoff"""
    RNPKRUNOFF: Optional[list] = None    

    # Waterbalance soil dynamics params
    """Field capacity of the soil"""
    SMFCF: Optional[float] = None                  
    """Porosity of the soil"""
    SM0: Optional[float] = None                                
    """Wilting point of the soil"""
    SMW: Optional[float] = None                          
    """Soil critical air content (waterlogging)"""
    CRAIRC: Optional[float] = None       
    """maximum percolation rate root zone (cm/day)"""
    SOPE: Optional[float] = None    
    """maximum percolation rate subsoil (cm/day)"""
    KSUB: Optional[float] = None                  
    """Soil rootable depth (cm)"""
    RDMSOL: Optional[float] = None                            
    """Indicates whether non-infiltrating fraction of rain is a function of storm size (1) or not (0)"""
    IFUNRN: Optional[float] = None    
    """Maximum surface storage (cm)"""                               
    SSMAX: Optional[float] = None                          
    """Initial surface storage (cm)"""
    SSI: Optional[float] = None                   
    """Initial amount of water in total soil profile (cm)"""
    WAV: Optional[float] = None 
    """Maximum fraction of rain not-infiltrating into the soil"""
    NOTINF: Optional[float] = None
    """Initial maximum moisture content in initial rooting depth zone"""
    SMLIM: Optional[float] = None  
    """CO2 in atmosphere (ppm)"""
    CO2: Optional[float] = None  
    """Reference CO2 Rate"""
    REFCO2L: Optional[float] = None


    # WOFOST Parameters
    """Conversion factor for assimilates to leaves"""
    CVL: Optional[List[float]] = None
    """Conversion factor for assimilates to storage organs"""
    CVO: Optional[List[float]] = None    
    """onversion factor for assimilates to roots"""  
    CVR: Optional[List[float]] = None     
    """Conversion factor for assimilates to stems"""
    CVS: Optional[List[float]] = None     

    # Assimilation Parameters
    """ Max leaf |CO2| assim. rate as a function of of DVS (kg/ha/hr)"""
    AMAXTB: Optional[list] = None   
    """ Light use effic. single leaf as a function of daily mean temperature |kg ha-1 hr-1 /(J m-2 s-1)|"""
    EFFTB: Optional[list] = None
    """Extinction coefficient for diffuse visible as function of DVS"""
    KDIFTB: Optional[list] = None    
    """Reduction factor of AMAX as function of daily mean temperature"""
    TMPFTB: Optional[list] = None
    """Reduction factor of AMAX as function of daily minimum temperature"""
    TMNFTB: Optional[list] = None  
    """Correction factor for AMAX given atmospheric CO2 concentration.""" 
    CO2AMAXTB: Optional[list] = None 
    """Correction factor for EFF given atmospheric CO2 concentration."""
    CO2EFFTB: Optional[list] = None   

    # Evapotranspiration Parameters
    """Correction factor for potential transpiration rate"""
    CFET: Optional[float] = None 
    """Dependency number for crop sensitivity to soil moisture stress."""  
    DEPNR: Optional[float] = None   
    """Extinction coefficient for diffuse visible as function of DVS.""" 
    KDIFTB: Optional[float] = None   
    """Switch oxygen stress on (1) or off (0)"""
    IOX: Optional[float] = None  
    """Switch airducts on (1) or off (0) """    
    IAIRDU: Optional[float] = None 
    """Reduction factor for TRAMX as function of atmospheric CO2 concentration"""      
    CO2TRATB: Optional[list] = None
   
    # Leaf Dynamics Parameters
    """Maximum relative increase in LAI (ha / ha d)"""
    RGRLAI: Optional[float] = None      
    """Life span of leaves growing at 35 Celsius (days)"""          
    SPAN: Optional[float] = None   
    """Lower threshold temp for ageing of leaves (C)"""  
    TBASE: Optional[float] = None  
    """Max relative death rate of leaves due to water stress"""  
    PERDL: Optional[float] = None    
    """Extinction coefficient for diffuse visible light as function of DVS"""
    KDIFTB: Optional[list] = None   
    """Specific leaf area as a function of DVS (ha/kg)"""
    SLATB: Optional[list] = None  
    """Maximum relative death rate of leaves due to nutrient NPK stress"""  
    RDRNS: Optional[list] = None    
    """coefficient for the reduction due to nutrient NPK stress of the LAI increas
            (during juvenile phase)"""
    NLAI: Optional[float] = None    
    """Coefficient for the effect of nutrient NPK stress on SLA reduction""" 
    NSLA: Optional[float] = None  
    """Max. relative death rate of leaves due to nutrient NPK stress"""   
    RDRN: Optional[float] = None    
   
    # NPK Dynamics Parameters  
    """Maximum N concentration in leaves as function of DVS (kg N / kg dry biomass)"""
    NMAXLV_TB: Optional[list] = None      
    """Maximum P concentration in leaves as function of DVS (kg P / kg dry biomass)"""
    PMAXLV_TB: Optional[list] = None     
    """Maximum K concentration in leaves as function of DVS (kg K / kg dry biomass)"""
    KMAXLV_TB: Optional[list] = None    
    """Maximum N concentration in roots as fraction of maximum N concentration in leaves"""
    NMAXRT_FR: Optional[float] = None      
    """Maximum P concentration in roots as fraction of maximum P concentration in leaves"""
    PMAXRT_FR: Optional[float] = None      
    """Maximum K concentration in roots as fraction of maximum K concentration in leaves"""
    KMAXRT_FR: Optional[float] = None      
    """Maximum N concentration in stems as fraction of maximum N concentration in leaves"""
    NMAXST_FR: Optional[float] = None      
    """Maximum P concentration in stems as fraction of maximum P concentration in leaves"""
    PMAXST_FR: Optional[float] = None     
    """Maximum K concentration in stems as fraction of maximum K concentration in leaves"""
    KMAXST_FR: Optional[float] = None   

    """Residual N fraction in leaves (kg N / kg dry biomass)""" 
    NRESIDLV: Optional[float] = None 
    """Residual P fraction in leaves (kg P / kg dry biomass)""" 
    PRESIDLV: Optional[float] = None
    """Residual K fraction in leaves (kg K / kg dry biomass)""" 
    KRESIDLV: Optional[float] = None    
    """Residual N fraction in stems (kg N / kg dry biomass)""" 
    NRESIDST: Optional[float] = None    
    """Residual K fraction in stems (kg P / kg dry biomass)""" 
    PRESIDST: Optional[float] = None 
    """Residual P fraction in stems (kg K / kg dry biomass)""" 
    KRESIDST: Optional[float] = None                 
    """NPK translocation from roots as a fraction of resp. total NPK amounts translocated
                        from leaves and stems"""     

    """Residual N fraction in roots (kg N / kg dry biomass)"""
    NRESIDRT: Optional[float] = None                              
    """Residual P fraction in roots (kg P / kg dry biomass)"""
    PRESIDRT: Optional[float] = None       
    """Residual K fraction in roots (kg K / kg dry biomass)"""
    KRESIDRT: Optional[float] = None              

    # Partioning Parameters
    """Coefficient for the effect of nutrient NPK stress on SLA reduction"""
    NSLA_NPK: Optional[float] = None
    """Coefficient for the reduction due to nutrient NPK stress of the LAI increase"""
    NLAI_NPK: Optional[float] = None
    """Maximum relative death rate of leaves due to nutrient NPK stress"""
    RDRLV_NPK: Optional[float] = None
    """Partitioning to roots as a function of development stage"""
    FRTB: Optional[list] = None     
    """Partitioning to stems as a function of development stage"""
    FSTB: Optional[list] = None     
    """Partitioning to leaves as a function of development stage"""
    FLTB: Optional[list] = None     
    """Partitioning to starge organs as a function of development stage"""
    FOTB: Optional[list] = None     
    """Coefficient for the effect of N stress on leaf biomass allocation"""
    NPART: Optional[float] = None   
    """Threshold above which surface nitrogen induces stress"""
    NTHRESH: Optional[float] = None
    """Threshold above which surface phosphorous induces stress"""
    PTHRESH: Optional[float] = None
    """Threshold above which surface potassium induces stress"""
    KTHRESH: Optional[float] = None

    # Vernalization Parameters
    """Saturated vernalisation requirements (days)"""
    VERNSAT: Optional[float] = None
    """Base vernalisation requirements (days)"""
    VERNBASE: Optional[float] = None
    """Rate of vernalisation as a function of daily mean temperature"""
    VERNRTB: Optional[list] = None
    """Critical development stage after which the effect of vernalisation is halted"""
    VERNDVS: Optional[float] = None

    # Phenology Parameters
    """Number of days above TSUMEM for germination to occur"""
    DTBEM: Optional[int] = None
    """Temperature sum from sowing to emergence (C day)"""
    TSUMEM: Optional[float] = None   
    """Base temperature for emergence (C)"""
    TBASEM: Optional[float] = None
    """Maximum effective temperature for emergence (C day)"""
    TEFFMX: Optional[float] = None
    """Temperature sum from emergence to anthesis (C day)"""
    TSUM1: Optional[float] = None
    """Temperature sum from anthesis to maturity (C day)"""
    TSUM2: Optional[float] = None
    """Temperature sum from maturity to death (C day)"""
    TSUM3: Optional[float] = None
    """Temperature sum from ripening onward (for grapes)"""
    TSUM4: Optional[float] = None
    """Switch for phenological development options temperature only (IDSL=0), 
    including daylength (IDSL=1) and including vernalization (IDSL>=2)"""
    IDSL: Optional[float] = None
    """Optimal daylength for phenological development (hr)"""
    DLO: Optional[float] = None  
    """Critical daylength for phenological development (hr)"""
    DLC: Optional[float] = None
    """Initial development stage at emergence. Usually this is zero, but it can 
    be higher or crops that are transplanted (e.g. paddy rice)"""
    DVSI: Optional[float] = None
    """Mature development stage"""
    DVSM: Optional[float] = None
    """Final development stage"""
    DVSEND: Optional[float] = None      
    """Daily increase in temperature sum as a function of daily mean temperature (C)"""               
    DTSMTB: Optional[List[float]] = None
    """Dormancy threshold after which plant becomes dormant (days)"""
    DORM: Optional[int] = None  
    """Minimum length of dormancy state"""  
    DORMCD: Optional[int] = None  
    """Initial age of crop (years)"""
    AGEI: Optional[int] = None
    """Daylength dormancy threshold"""
    MLDORM: Optional[float] = None
    """Maximum length of dormancy cycle"""
    DCYCLEMAX: Optional[int] = None
    """Regression factor for chilling units (grapes)"""
    Q10C: Optional[float] = None
    """Chilling units required for endodormancy break"""
    CSUMDB: Optional[float] = None

    # Cold hardiness (grapes)
    """Initial cold hardiness value"""
    HCINIT: Optional[float] = None 
    """Minimum cold hardiness"""
    HCMIN: Optional[float] = None   
    """Maximum cold hardiness"""
    HCMAX: Optional[float] = None 
    """Threshold for degree-days during endodormancy"""
    TENDO: Optional[float] = None
    """Threshold for degree-days during ecodormancy"""
    TECO: Optional[float] = None
    """Temperature threshold for ecodormancy transition"""     
    ECOBOUND: Optional[float] = None 
    """Acclimation rate during endodormancy"""
    ENACCLIM: Optional[float] = None
    """Acclimation rate during ecodormancy"""
    ECACCLIM: Optional[float] = None
    """Deacclimation rate during endodormancy"""
    ENDEACCLIM: Optional[float] = None
    """eacclimation rate during ecodormancy"""
    ECDEACCLIM: Optional[float] = None
    """Parameter for the cold hardiness model"""
    THETA: Optional[float] = None   

    # Respiration Parameters
    """Relative increase in maintenance repiration rate with each 10 degrees increase in temperature"""
    Q10: Optional[float] = None    
    """Relative maintenance respiration rate for roots |kg CH2O kg-1 d-1|"""
    RMR: Optional[List[float]] = None 
    """ Relative maintenance respiration rate for stems |kg CH2O kg-1 d-1| """   
    RMS: Optional[List[float]] = None 
    """Relative maintenance respiration rate for leaves |kg CH2O kg-1 d-1|""" 
    RML: Optional[List[float]] = None                                         
    """Relative maintenance respiration rate for storage organs |kg CH2O kg-1 d-1|"""
    RMO: Optional[List[float]] = None    
    """Reduction factor  for senescence as function of DVS"""
    RFSETB: Optional[List[float]] = None

    # Root Dynamics Parameters
    """Initial rooting depth (cm)"""
    RDI: Optional[float] = None
    """Daily increase in rooting depth  |cm day-1|"""
    RRI: Optional[float] = None   
    """Maximum rooting depth of the crop (cm)""" 
    RDMCR: Optional[float] = None
    """Maximum rooting depth of the soil (cm)"""
    RDMSOL: Optional[float] = None
    """Presence of air ducts in the root (1) or not (0)""" 
    IAIRDU: Optional[float] = None
    """Relative death rate of roots as a function of development stage"""
    RDRRTB: Optional[List[float]] = None
    """Relative death rate of roots as a function of oxygen stress (over watering)"""
    RDRROS: Optional[List[float]] = None
    """Relative death rate of roots due to excess NPK on surface"""
    RDRRNPK: Optional[List[float]] = None

    # Stem Dynamics Parameters   
    """Relative death rate of stems as a function of development stage"""
    RDRSTB: Optional[List[float]] = None   
    """Specific Stem Area as a function of development stage (ha/kg)"""
    SSATB: Optional[List[float]] = None   
   
    # Storage Organs Dynamics Parameters
    """Initial total crop dry weight (kg/ha)"""
    TDWI: Optional[List[float]] = None    
    """Relative death rate of storage organs as a function of development stage"""
    RDRSOB: Optional[List[float]] = None
    """Specific Pod Area (ha / kg)""" 
    SPA: Optional[List[float]] = None    
    """Relative death rate of storage organs as a function of frost kill"""
    RDRSOF: Optional[List[float]] = None
    
    # NPK Demand Uptake Parameters     
    NMAXSO: Optional[float] = None      
    """Maximum P concentration in storage organs (kg P / kg dry biomass)"""  
    PMAXSO: Optional[float] = None 
    """Maximum K concentration in storage organs (kg K / kg dry biomass)"""          
    KMAXSO: Optional[float] = None      
    """Critical N concentration as fraction of maximum N concentration for vegetative
                    plant organs as a whole (leaves + stems)"""
    NCRIT_FR: Optional[float] = None       
    """Critical P concentration as fraction of maximum P concentration for vegetative
                    plant organs as a whole (leaves + stems)"""
    PCRIT_FR: Optional[float] = None        
    """Critical K concentration as fraction of maximum K concentration for vegetative
                    plant organs as a whole (leaves + stems)"""
    KCRIT_FR: Optional[float] = None   
    """DVS above which NPK uptake stops"""
    DVS_NPK_STOP: Optional[float] = None     
    
    """Time coefficient for N translation to storage organs (days)"""
    TCNT: Optional[float] = None           
    """Time coefficient for P translation to storage organs (days)"""
    TCPT: Optional[float] = None           
    """Time coefficient for K translation to storage organs (days)"""
    TCKT: Optional[float] = None           
    """fraction of crop nitrogen uptake by biological fixation (kg N / kg dry biomass)"""
    NFIX_FR: Optional[float] = None        
    """Maximum rate of N uptake (kg N / ha day)"""
    RNUPTAKEMAX: Optional[float] = None   
    """Maximum rate of P uptake (kg P / ha day)"""
    RPUPTAKEMAX: Optional[float] = None   
    """Maximum rate of K uptake (kg K / ha day)"""
    RKUPTAKEMAX: Optional[float] = None          

    # NPK Stress Parameters         
    NCRIT_FR: Optional[float] = None       
    """Critical P concentration as fraction of maximum P concentration for vegetative
                    plant organs as a whole (leaves + stems)"""
    PCRIT_FR: Optional[float] = None       
    """Critical K concentration as fraction of maximum L concentration for 
    vegetative plant organs as a whole (leaves + stems)"""
    KCRIT_FR: Optional[float] = None                    
    """Coefficient for the reduction of RUE due to nutrient (N-P-K) stress"""
    NLUE_NPK: Optional[float] = None 
   
    # NPK Translocation Parameters
    """NPK Translocation from roots"""
    NPK_TRANSLRT_FR: Optional[float] = None 
    """DVS above which translocation to storage organs begins"""
    DVS_NPK_TRANSL: Optional[float] = None

@dataclass 
class Agro_Args:
    """Dataclass to be used for configuration WOFOST agromanagement file

    If left to default of None, values will be drawn from the .yaml files in 
    /env_config/agro_config
    """

    """Latitude for Weather Data"""
    latitude: Optional[float] = None
    """Longitude for Weather Data"""
    longitude: Optional[float] = None
    """Year for Weather Data"""
    year: Optional[int] = None
    """Site Name"""
    site_name: Optional[str] = None
    """Site Variation Name"""
    site_variation: Optional[str] = None
    "Site Start Date in YYYY-MM-DD"
    site_start_date: Optional[str] = None
    """Site End Date in YYYY-MM-DD"""
    site_end_date: Optional[str] = None
    """Crop Name"""
    crop_name: Optional[str] = None
    "Crop Variety Name"
    crop_variety: Optional[str] = None
    """Crop Start Date in YYYY-MM-DD"""
    crop_start_date: Optional[str] = None
    """Crop Start type (emergence/sowing)"""
    crop_start_type: Optional[str] = None
    """Crop End Date in YYYY-MM-DD"""
    crop_end_date: Optional[str] = None
    """Crop end type (harvest/maturity)"""
    crop_end_type: Optional[str] = None
    """Max duration of crop growth"""
    max_duration: Optional[int] = None

@dataclass
class NPK_Args:
    """
    Arguments for the WOFOST Gym environment
    """

    """Parameters for the WOFOST8 model"""
    wf: WOFOST_Args

    """Parameters for Agromanangement file"""
    ag: Agro_Args

    """Environment seed"""
    seed: int = 0
    """Randomization scale for domain randomization"""
    scale: float = 0.1
    """Number of farms for multi farm environment"""
    num_farms = 5

    """Output Variables"""
    output_vars: list = field(default_factory = lambda: ['FIN', 'DVS', 'WSO', 'NAVAIL', 'PAVAIL', 'KAVAIL', 'SM', 'TOTN', 'TOTP', 'TOTK', 'TOTIRRIG'])
    """Weather Variables"""
    weather_vars: list = field(default_factory = lambda: ['IRRAD', 'TEMP', 'RAIN'])

    """Intervention Interval"""
    intvn_interval: int = 1
    """Weather Forecast length in days (min 1)"""
    forecast_length: int = 1
    forecast_noise: list = field(default_factory = lambda: [0, 0.2])
    """Number of NPK Fertilization Actions"""
    """Total number of actions available will be 3*num_fert + num_irrig"""
    num_fert: int = 4
    """Number of Irrgiation Actions"""
    num_irrig: int = 4

    """Flag for resetting to random year"""
    random_reset: bool = False
    """Flag for resetting to a specified group of years"""
    train_reset: bool = False
    """Flag for randomizing a subset of the parameters each reset"""
    domain_rand: bool = False
    """Flag for randomizing a subset of the parameters on initialization - for data generation"""
    crop_rand: bool = False
    
    """Harvest Effiency in range (0,1)"""
    harvest_effec: float = 1.0
    """Irrigation Effiency in range (0,1)"""
    irrig_effec: float = 0.7

    """Coefficient for Nitrogen Recovery after fertilization"""
    n_recovery: float = 0.7
    """Coefficient for Phosphorous Recovery after fertilization"""
    p_recovery: float = 0.7
    """Coefficient for Potassium Recovery after fertilization"""
    k_recovery: float = 0.7
    """Amount of fertilizer coefficient in kg/ha"""
    fert_amount: float = 2
    """Amount of water coefficient in cm/water"""
    irrig_amount: float  = 0.5

    """Path to assets file"""
    assets_fpath: str = f"{os.getcwd()}/pcse_gym/pcse_gym/assets/"


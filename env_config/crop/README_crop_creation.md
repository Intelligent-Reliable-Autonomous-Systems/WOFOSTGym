### README_crop_creation.md 
# An overview of how to create a new crop for use in the WOFOST simulator

## Crop Creation
1. To create a new crop, copy the template below into a <crop_name>.yaml file
2. Fill out all fields marked with angle brackets < > 
3. Create at least one desired variety for the crop. Make sure it inherits 
<crop_name> in the <<: &<crop_name> field
4. Register the crop by adding another line in the crops.yaml file. Doing so will 
ensure that the crop is loaded when the simulator is run
5. Create an agromanagement file for your crop (see ../agro_config/README_agro_creation.md)
to run your crop. Test the rest with python3 test_wofost.py --agro_fpath <agromanagement_file_name>


Version: 1.0.0
Metadata: &meta
    Creator: <Name>
    Contributor: <Institution>
    Contact: <Email>
    Publisher: <Group>
    Title: 
    Date: 
    Language: 
    Format: YAML
    Subject: <A Generic Crop>
    Description: <A Generic Crop Description>
    Identifier:
    Relation:
    Source: 
    Type:
    Coverage:
       Region: <Oregon, Washington, etc> 
    Rights: <License> 
    Keyword: <Crop keyword>
CropParameters:
    GenericC3: &GenericC1
        CO2EFFTB:
         - < (2x5) array float >
         - multiplication factor for EFF to account for an increasing CO2 concentration
         - ['PPM', '-']
        CO2TRATB: 
         - < (2x5) array float here >
         - multiplication factor for maximum transpiration rate TRAMX to account for an increasing CO2 concentration
         - ['PPM', '-']
        CO2AMAXTB:
         - < (2x5) array float >
         - multiplication factor for AMAX to account for an increasing CO2 concentration
         - ['PPM', '-']

    EcoTypes:
        <crop name>: &<cropname>
            <<: *GenericC1
            #
            # EMERGENCE
            #
            TBASEM:
            - < float >
            - Lower threshold temperature for emergence
            - ['C']
            TEFFMX:
            - < float >
            - maximum effective temperature for emergence
            - ['C']
            TSUMEM:
            - < float >
            - temperature sum from sowing to emergence
            - ['C.d']
            #
            # PHENOLOGICAL DEVELOPMENT
            #
            IDSL:
            -  < Bool, 0 or 1> 
            - indicates whether pre-anthesis development depends on temperature (=0), plus daylength (=1) , plus vernalization (=2)
            - ['NA']
            DLO:
            -  < float >
            - optimum daylength for development
            - ['hr']
            DLC:
            -  < float >
            - critical daylength (lower threshold)
            - ['hr']
            TSUM1:
            -  < float >
            - temperature sum from emergence to anthesis
            - ['C.d']
            TSUM2:
            - 1481
            - temperature sum from anthesis to maturity
            - ['C.d']
            TSUM3:
            - 800
            - temperature sum from anthesis to maturity
            - ['C.d']
            DTSMTB:
            - < (2x4) array float >
            - daily increase in temperature sum as function of daily average temperature
            - ['C', 'C']
            DVSI:
            -  < float >
            - Initial development stage
            - ['-']
            DVSEND:
            -  < float >
            - development stage at harvest (= 2.0 at maturity)
            - ['-']
            VERNBASE:
            - < float >
            - Base vernalization requirement
            - ['d']
            VERNSAT:
            - < float >
            - Saturated vernalization requirement
            - ['d']
            VERNDVS:
            - < float >
            - Critical DVS for vernalization to switch off
            - ['-']
            VERNRTB:
            - < (2x6) array float >
            - Temperature response function for vernalization
            - ['C', '-']
            #
            # INITIAL STATES
            #
            TDWI:
            -   < float >
            - initial total crop dry weight
            - ['kg.ha-1']
            RGRLAI:
            - 0.0500
            - maximum relative increase in LAI
            - ['d-1']
            #
            # CROP GREEN AREA
            #
            SLATB:
            - < (2x3) array float > 
            - specific leaf area as a function of DVS
            - ['-', 'ha.kg-1']
            SPA:
            - < float >
            - specific pod area
            - ['ha.kg-1']
            SSATB:
            - < (2x2) array float > 
            - specific stem area as function of DVS
            - ['-', 'ha.kg-1']
            SPAN:
            - < float >
            - life span of leaves growing at 35 Celsius
            - ['d']
            TBASE:
            - < float >
            - lower threshold temperature for ageing of leaves
            - ['C']
            #
            # CO2 ASSIMILATION
            #
            KDIFTB:
            - < (2x2) array float > 
            - extinction coefficient for diffuse visible light as function of DVS
            - ['-', '-']
            EFFTB:
            - < (2x2) array float >
            - initial light-use efficiency single leaf as function of daily mean temperature
            - ['C', 'kg.ha-1.hr-1.J-1.m2.s1']
            AMAXTB:
            - < (2x3) array float > 
            - maximum leaf CO2 assimilation rate as function of DVS
            - ['-', 'kg.ha-1.hr-1']
            REFCO2L:
            - < float >
            - CO2 level at which AMAX and EFF were measured
            - ['PPM']
            TMPFTB:
            - < (2x5) array float > 
            - reduction factor of AMAX as function of average daytime (*not* daily)  temperature
            - ['C', '-']
            TMNFTB:
            - < (2x2) array float > 
            - reduction factor of gross assimilation rate as function of low minimum temperature
            - ['C', '-']
            #
            # CONVERSION EFFICIENCY OF ASSIMILATES
            #
            CVL:
            - < float >
            - efficiency of conversion into leaves
            - ['mass.mass-1']
            CVO:
            - < float >
            - efficiency of conversion into storage organs
            - ['mass.mass-1']
            CVR:
            - < float >
            - efficiency of conversion into roots
            - ['mass.mass-1']
            CVS:
            - < float >
            - efficiency of conversion into stems
            - ['mass.mass-1']
            #
            # RESPIRATION
            #
            Q10:
            -  < float >
            - relative increase in respiration rate per 10 degrees Celsius temperature increase
            - ['-']
            RML:
            - < float >
            - relative maintenance respiration rate of leaves
            - ['d-1']
            RMO:
            - < float >
            - relative maintenance respiration rate of storage organs
            - ['d-1']
            RMR:
            - < float >
            - relative maintenance respiration rate of roots
            - ['d-1']
            RMS:
            - < float >
            - relative maintenance respiration rate of stems
            - ['d-1']
            RFSETB:
            - < (2x2) array float > 
            - reduction factor for senescence as function of DVS
            - ['-', '-']
            #
            # PARTITIONING
            #
            FRTB:
            - < (2x3) array float > 
            - fraction of total dry matter to roots as a function of DVS
            - ['-', 'mass.mass-1']
            FLTB:
            - < (2x6) array float > 
            - fraction of total dry matter to leaves as a function of DVS
            - ['-', 'mass.mass-1']
            FSTB:
            - < (2x6) array float > 
            - fraction of total dry matter to stems as a function of DVS
            - ['-', 'mass.mass-1']
            FOTB:
            - < (2x6) array float > 
            - fraction of total dry matter to storage organs as a function of DVS
            - ['-', 'mass.mass-1']
            #
            # DEATH RATES
            # RDRROS:
            - [0.000, 0.020,
               0.250, 0.100,
               0.999, 0.001,
               1.000, 0.000]
            - Relative death rate of stems as a function of Oxygen stress
            - ['-', 'kg.kg-1.d-1']
            PERDL:
            - < float >
            - maximum relative death rate of leaves due to water stress
            - ['-']
            RDRRTB:
            - < (2x4) array float > 
            - Relative death rate of stems as a function of DVS
            - ['-', 'kg.kg-1.d-1']
            RDRSTB:
            - < (2x4) array float > 
            - relative death rate of roots as a function of DVS
            - ['-', 'kg.kg-1.d-1']
            #
            # WATER USE
            #
            CFET:
            - < float >
            - correction factor transpiration rate
            - ['-']
            DEPNR:
            - < float >
            - crop group number for soil water depletion
            - ['-']
            IAIRDU:
            -  < Bool, 0 or 1 >
            - air ducts in roots present (=1) or not (=0)
            - ['NA']
            IOX:
            -  < Bool, 0 or 1 > 
            - Oxygen stress effect enabled (=1) or not (=0)
            - ['NA']
            #
            # ROOTING DEPTH
            #
            RDI:
            -  < float >
            - initial rooting depth
            - ['cm']
            RRI:
            - < float >
            - maximum daily increase in rooting depth
            - ['cm.d-1']
            RDMCR:
            - < float >
            - maximum rooting depth
            - ['cm']
            #
            # MAXIMUM, CRITICAL AND RESIDUAL NITROGEN CONCENTRATION IN DIFFERENT ORGANS
            #
            NMAXLV_TB:
            - < (2x6) array float > 
            - maximum N concentration in leaves as function of development stage in kg N kg-1 dry biomass
            - ['-', 'mass.mass-1']
            NMAXRT_FR:
            - < float >
            - maximum N concentration in roots as fraction of maximum N concentration in leaves
            - ['-']
            NMAXST_FR:
            - < float >
            - maximum N concentration in stems as fraction of maximum N concentration in leaves
            - ['-']
            NMAXSO:
            - < float >
            - maximum P concentration in storage organs [kg N kg-1 dry biomass]
            - ['mass.mass-1']
            NCRIT_FR:
            - < float >
            - Critical N concentration as fraction of maximum N concentration
            - ['-']
            NRESIDLV:
            - < float >
            - residual N fraction in leaves [kg N kg-1 dry biomass]
            - ['mass.mass-1']
            NRESIDST:
            - < float >
            - residual N fraction in stems [kg N kg-1 dry biomass]
            - ['mass.mass-1']
            NRESIDRT:
            - < float >
            - residual N fraction in roots [kg N kg-1 dry biomass]
            - ['mass.mass-1']
            TCNT:
            -  < float >
            - time coefficient for N translocation to storage organs
            - ['d']
            NFIX_FR:
            - < float >
            - fraction of crop nitrogen uptake by biological fixation
            - ['-']
            #
            # MAXIMUM, CRITICAL AND RESIDUAL PHOSPHORUS CONCENTRATION IN DIFFERENT ORGANS
            #
            PMAXLV_TB:
            - < (2x6) array float > 
            - maximum P concentration in leaves as function of development stage in kg P kg-1 dry biomass
            - ['-', 'mass.mass-1']
            PMAXRT_FR:
            - < float >
            - maximum P concentration in roots as fraction of maximum P concentration in leaves
            - ['-']
            PMAXST_FR:
            - < float >
            - maximum P concentration in stems as fraction of maximum P concentration in leaves
            - ['-']
            PMAXSO:
            - < float >
            - maximum P concentration in storage organs [kg P kg-1 dry biomass]
            - ['mass.mass-1']
            PCRIT_FR:
            - < float >
            - Critical P concentration as fraction of maximum P concentration
            - ['-']
            PRESIDLV:
            - < float >
            - residual P fraction in leaves [kg P kg-1 dry biomass]
            - ['mass.mass-1']
            PRESIDST:
            - < float >
            - residual P fraction in stems [kg P kg-1 dry biomass]
            - ['mass.mass-1']
            PRESIDRT:
            - < float >
            - residual P fraction in roots [kg P kg-1 dry biomass]
            - ['mass.mass-1']
            TCPT:
            -  < float >
            - time coefficient for P translocation to storage organs
            - ['d']
            #
            # MAXIMUM, CRITICAL AND RESIDUAL POTASSIUM CONCENTRATION IN DIFFERENT ORGANS
            #
            KMAXLV_TB:
            - < (2x6) array float > 
            - maximum K concentration in leaves as function of development stage in kg K kg-1 dry biomass
            - ['-', 'mass.mass-1']
            KMAXRT_FR:
            - < float >
            - maximum K concentration in roots as fraction of maximum K concentration in leaves
            - ['-']
            KMAXST_FR:
            - < float >
            - maximum K concentration in stems as fraction of maximum K concentration in leaves
            - ['-']
            KMAXSO:
            - < float >
            - maximum K concentration in storage organs [kg K kg-1 dry biomass]
            - ['mass.mass-1']
            KCRIT_FR:
            - < float >
            - Critical K concentration as fraction of maximum K concentration
            - ['-']
            KRESIDLV:
            - < float >
            - residual K fraction in leaves [kg K kg-1 dry biomass]
            - ['mass.mass-1']
            KRESIDST:
            - < float >
            - residual K fraction in stems [kg K kg-1 dry biomass]
            - ['mass.mass-1']
            KRESIDRT:
            - < float >
            - residual K fraction in roots [kg K kg-1 dry biomass]
            - ['mass.mass-1']
            TCKT:
            -  < float >
            - time coefficient for K translocation to storage organs
            - ['d']
            #
            # IMPORT DVS RELATED TO N/P/K UPTAKE AND TRANSLOCATION
            #
            DVS_NPK_STOP:
            - < float >
            - development stage above which no crop N/P/K uptake occurs
            - ['-']
            DVS_NPK_TRANSL:
            - < float >
            - development stage above which N/P/K translocation to storage organs does occur
            - ['-']
            #
            # IMPACT OF N/P/K STRESS ON PROCESSES
            #
            NLAI_NPK:
            - < float >
            - coefficient for the reduction due to nutrient NPK stress of the LAI increase (during juvenile phase)
            - ['-']
            NSLA_NPK:
            - < float >
            - coefficient for the effect of nutrient NPK stress on SLA reduction
            - ['-']
            NPART:
            - < float >
            - coefficient for the effect of nutrient N stress on leaf allocation
            - ['-']
            NLUE_NPK:
            - < float >
            - coefficient for the reduction of gross CO2 assimilation rate due to nutrient (N-P-K) stress
            - ['-']
            NPK_TRANSLRT_FR:
            - < float >
            - NPK translocation from roots as a fraction of total NPK amounts translocated from leaves and stems
            - ['-']
            RDRLV_NPK:
            - < float >
            - maximum relative death rate of leaves due to nutrient NPK stress
            - ['-']
            #
            # Maximum N/P/K uptake rates, see changelog.txt
            #
            RNUPTAKEMAX:
             - < float >
             - Maximum rate of daily nitrogen uptake
             - ['kg.ha-1.d-1']
            RPUPTAKEMAX:
             - < float >
             - Maximum rate of daily phosphorus uptake
             - ['kg..ha-1.d-1']
            RKUPTAKEMAX:
             - 7.4
             - Maximum rate of daily potassium uptake
             - ['kg.ha-1.d-1']
    Varieties:
        <crop variety here>:
            <<: *<cropname>
            Metadata:
                <<: *meta
            <PARAMETER TO CHANGE>:
            -  < float >
            - description
            - ['unit']
            

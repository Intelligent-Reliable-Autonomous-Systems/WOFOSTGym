### README_site_creation.md 
# An overview of how to create a new site for use in the WOFOST simulator

## Site Creation
1. To create a new site, copy the template below into a <site_name>.yaml file
2. Fill out all fields marked with angle brackets < > 
3. Create at least one desired variety for the site. Make sure it inherits 
<site_name> in the <<: &<site_name> field
4. Register the site by adding another line in the sites.yaml file. Doing so will 
ensure that the site is loaded when the simulator is run
5. Create an agromanagement file for your site (see ../agro_config/README_agro_creation.md)
to run your site. Test the rest with python3 test_wofost.py --agro_fpath <agromanagement_file_name>


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
    Subject: <A Generic Site>
    Description: <A Generic Site Description>
    Identifier:
    Relation:
    Source: 
    Type:
    Coverage:
       Region: <Oregon, Washington, etc> 
    Rights: <License> 
    Keyword: <Site keyword>

   EcoTypes:
     <site name>: &<site_name>
       #
       # NPK SOIL DYNAMICS
       # 
       BG_N_SUPPLY:
       - < float > 
       - background supply of N through atmospheric deposition
       - ['kg ha-1 d-1']
       BG_P_SUPPLY:
       - < float > 
       - background supply of P through atmospheric deposition
       - ['kg ha-1 d-1']
       BG_K_SUPPLY:
       - < float > 
       - background supply of K through atmospheric deposition
       - ['kg ha-1 d-1']
       NAVAILI:
       - < float > 
       - initial N available in the N pool     
       - ['kg ha-1']
       PAVAILI:
       - < float > 
       - initial P available in the P pool     
       - ['kg ha-1']
       KAVAILI:
       - < float > 
       - initial K available in the K pool     
       - ['kg ha-1']
       NSOILBASE:
       - < float > 
       - base soil supply of N available through mineralisation
       - ['kg ha-1']
       NSOILBASE_FR:
       - < float > 
       - Fraction of base soil N that comes available every day
       - ['-']
       PSOILBASE:
       - < float > 
       - base soil supply of P available through mineralisation
       - ['kg ha-1']
       PSOILBASE_FR:
       - < float > 
       - Fraction of base soil P that comes available every day
       - ['-']
       KSOILBASE:
       - < float > 
       - base soil supply of K available through mineralisation
       - ['kg ha-1']
       KSOILBASE_FR:
       - < float > 
       - Fraction of base soil K that comes available every day
       - ['-'] 
       #
       # WATER BALANCE
       # 
       SMFCF:
       - < float > 
       - soil moisture content at field capacity
       - ['cm3/cm3']
       SM0:
       - < float > 
       - soil moisture content at saturation
       - ['cm3/cm3']  
       SMW:
       - < float > 
       - soil moisture content at wilting point
       - ['cm3/cm3']
       CRAIRC:
       - < float >  
       - critical soil air content for aeration
       - ['cm3/cm3']
       SOPE:
       - < float > 
       - maximum percolation rate root zone  
       - ['cmday-1']
       KSUB:
       - < float > 
       - maximum percolation rate subsoil  
       - ['cmday-1']
       RDMSOL: 
       - < float > 
       - soil maximum rootable depth
       - ['cm']
       IFUNRN: 
       - < Bool, 0 or 1 > 
       - indicates whether non-infiltrating fraction of rain is a function of storm size (1) or not (0)
       - ['-']
       SSMAX: 
       - < float > 
       - maximum surface storage
       - ['cm']
       SSI:
       - < float > 
       - initial surface storage   
       - ['cm']
       WAV:
       - < float > 
       - initial amount of water in total soil profile
       - ['cm']
       NOTINF:
       - < float > 
       - maximum fraction of rain not-infiltrating into the soil
       - ['-']
       SMLIM:     
       - < float > 
       - limiting amount of volumetric moisture in upper soil layer 
       - ['-']
       #
       # EVAPOTRANSPIRATION
       # 
       CO2:
       - < float > 
       - atmospheric CO2 concentration
       - ['ppm']
   Variations:
     <variation name>:
        <<: *<parent_site_name> 
        Metadata:
           <<: *meta
           Description: 
        <PARAMETER TO CHANGE:
        - < float > 
        - atmospheric CO2 concentration
        - ['ppm']







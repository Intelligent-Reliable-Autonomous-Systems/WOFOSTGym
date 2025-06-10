### Python Crop Simulation Environment (PCSE) README.md 
## Written by Will Solow

PCSE was developed by the research group in Wageningen led by Allard de Wit. Please
see [pcse](https://github.com/ajwdewit/pcse) for more information. This README
is written for the purpose of understanding PCSE/WOFOST8 simulator, and what
modifications have been made to support the WOFOST Gym environment and training
RL agents. 

## Important Files to be aware of 

** Agromanager.py - this file loads the agromanagement data and controls when the 
crop is started and finished. Any modifications to crop dates, rotations, or multi
year/multi farm support will be found here. 

** signals.py - this file contains all the possible signals that WOFOST can process. 
Signals are connected to a module by the _connect_signal() function and send to the 
model to be read by various subclasses with the send_signal() function. 

** engine.py - main base class for all models. Supports running the simulation through
the integration of state and rate variables and the handling of crop start and 
crop finish signals. Contains registry for crop models as well.

** /base/ - folder for abstract classes such as parameter providers and weather
provider. No modifications here should be needed. 

** /conf/ - location for all model configuration files. If a new model needs to be
created, it will need a .conf file which should be located here. See the following
section for creating a new model.

** /crop/ - folder which contains all the parts of the crop. No files here should 
need to be modified, but we provide a concise description of each. 

* nutrients/npk_demand_update.py - computes the NPK nutrient demand of the crop.

* nutrients/npk_stress.py - computes the stress on the crop due to lack of available
NPK.

* nutrients/npk_translocation.py - calculates the translocation (rearrangmenet) of 
NPK between the roots, stems, leaves, and storage organs in the crop. 

* assimilation.py - computes the CO2 assimilation rate.

* evapotranspiration.py - calculates the evapotranspiration (water and soil) and
the resulting transpiration rates of the crop.

* leaf_dynamics.py - computes the leaf growth of the crop

* npk_dynamics.py - controls the NPK dynamics within the crop using the /nutrients/
objects 

* partitioning.py - computes the partitioning of absorbed NPK + water into various
parts of the crop 

* phenology.py - stores the vernalisation and phenology objects of the crop which
control emergence, maturity, etc. 

* root_dynamics.py - computes the root growth within the crop (ie rooting depth).

* storage_organ_dynamics.py - computes the growth of storage organs in the crop, 
ie the part of the crop that is harvested for food. 

* wofost8.py - main crop file. Brings all other objects together as part of a 
single crop organism and does bookkeeping for the entire crop state. 

** /soil/ - folder which contains all parts of the soil. No need to modify but
we provide a concise description of each file. 

* classic_waterbalance.py - controls the amount of available water in the soil as 
a result of rainfall and irrigation. We provide soil water models for limited water
and abundant water. 

* npk_soil_dynamics.py - a bookkeeping class for the amount of NPK available in the 
soil as a result of fertilization, crop uptake, and background production. We provide
soil models for limited NPK, limited N, and abundant NPK.

* soil_wrappers.py - the most important file in the class. Contains soil wrappers
for the soil and water balance to enable usability in a general model. We provide
6 possible soils (which correspond to the 6 WOFOST Gym environments): Limited NPK
and water, Limited NPK, Limited Water, Limited N, Limited N and Water, and abundant
NPK and water. 

** /db/ - connection to the NASA Power weather database. No changes needed here.

** /fileinput/ - folder for YAML file loaders for the crop, soil, and agromanagement
.yaml files. There are additional file loaders that can load in a single crop as 
opposed to all crops at once. We recommend that no changes are made here. 

** /pydipatch/ - folder for classes that provide error checking. No modifications
should be needed here.

** /settings/ - folder for some default settings. No modifications should be needed
here

## Model Creation

It is possible that the user may way to use a different crop model for simulating
the growth of a crop. To do so:

1. Create a new crop model in the /crop/ folder. If it uses different parameters
than the default ones used in WOFOST8, be sure to create the appropriate .yaml file
in the ../env_config/crop_config/ folder and register it in the crops.yaml file. 
Also, register it in the __init__.py file in /crop/

2. Register the model in the models.py file as shown for the WOFOST8 model.

3. Create a new soil water model in the /soil/classic_waterbalance.py file. If is uses
different parameters than the default ones used in WaterBalanceFD, be sure to 
create the appropriate .yaml file in the ../env_config/site_config/ folder 
and register it in the sites.yaml file. Also, register it in the __init__.py file
in /soil/

4. Create a new NPK soil model in the /soil/npk_soil_dynamics.py file. If is uses
different parameters than the default ones used in NPK_Soil_Dynamics, be sure to 
create the appropriate .yaml file in the ../env_config/site_config/ folder 
and register it in the sites.yaml file. Also, register it in the __init__.py file
in /soil/

5. Create a new soil wrapper in the /soil/soil_wrappers.py file. Register this
wrapper in the __init__.py file. 

6. Copy one of the .conf files in the /conf/ folder. Input the names of the crop
model and soil wrapper model into the CROP and SOIL locations. If the output
variables (states) do not match those of WOFOST8, WaterbalanceFD, and NPK_Soil_Dynamics,
be sure to change them.
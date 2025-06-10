# -*- coding: utf-8 -*-
# Copyright (c) 2004-2018 Alterra, Wageningen-UR
# All files in pcse directory fall under this license
# Even if modified/created by Will Solow at OSU
"""
Initial entry point for the PCSE package. Handles all requisite
imports and making the Weather cache directory

The Python Crop Simulation Environment (PCSE) has been developed
to facilitate implementing crop simulation models that were 
developed in Wageningen. PCSE provides a set of building blocks
that on the one hand facilitates implementing the crop simulation
models themselves and other hand allows to interface these models with
external inputs and outputs (files, databases, webservers) 

PCSE builds on existing ideas implemented in the FORTRAN
Translator (FST) and its user interface FSE. It inherits ideas
regarding the rigid distinction between rate calculation
and state integration and the initialization of parameters
in a PCSE model. Moreover PCSE provides support for reusing
input files and weather files that are used by FST models.

PCSE currently provides an implementation of the WOFOST and LINTUL crop
simulation models and variants of WOFOST with extended
capabilities.

See Also
--------
* http://www.wageningenur.nl/wofost
* http://github.com/ajwdewit/pcse
* http://pcse.readthedocs.org

Allard de Wit (allard.dewit@wur.nl), April 2018
Modified by Will Solow, 2024
"""
from __future__ import print_function
__author__ = "Allard de Wit <allard.dewit@wur.nl>"
__license__ = "European Union Public License"
__stable__ = True
__version__ = "5.5.6"

import os
import pathlib

# Import first to avoid circular imports
from . import util
from .utils import exceptions, decorators, traitlets, signals

import logging.config
from .base import ParameterProvider
from .nasapower import NASAPowerWeatherDataProvider
from . import fileinput
from . import agromanager
from . import soil
from . import crop

user_path = pathlib.Path(__file__).parent.resolve()

# Make .pcse cache folder in the current working directory
pcse_user_home = os.path.join(user_path, ".pcse")
os.makedirs(pcse_user_home,exist_ok=True)

# Make folder in .pcse for weather data
meteo_cache_dir = os.path.join(pcse_user_home, "meteo_cache")
os.makedirs(meteo_cache_dir,exist_ok=True)




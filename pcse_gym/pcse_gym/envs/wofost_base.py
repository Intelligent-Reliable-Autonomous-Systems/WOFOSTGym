"""Main API for the WOFOST Gym environment. All other environments inherit
from the NPK_Env Gym Environment

Written by Will Solow, 2024"""

import os
import datetime
from datetime import date
from collections import deque
import numpy as np
import yaml, copy
import gymnasium as gym

from pcse_gym.args import NPK_Args
from pcse_gym import exceptions as exc
from pcse_gym import utils
import pygame

import pcse
from pcse.engine import Wofost8Engine
from pcse import NASAPowerWeatherDataProvider
from pcse_gym.envs.render import render as render_env

class NPK_Env(gym.Env):
    """Base Gym Environment for simulating crop growth
    
    Relies on the PCSE package (in base folder) and the WOFOST80 crop model. 
    """

    # Env Constants
    NUM_ACT = 4
    N = 0 # Nitrogen action
    P = 1 # Phosphorous action
    K = 2 # Potassium action
    I = 3 # Irrigation action 

    WEATHER_YEARS = [1984, 2019]
    MISSING_YEARS = []
    grape_env = False

    TRAIN_YEARS = [1990, 1994]

    def __init__(self, args: NPK_Args, base_fpath: str, agro_fpath:str, \
                 site_fpath:str, crop_fpath:str, name_fpath:str, unit_fpath:str, 
                 range_fpath:str, render_mode:str=None, config:dict=None):
        """Initialize the :class:`NPK_Env`.

        Args: 
            NPK_Args: The environment parameterization
            config: Agromanagement configuration dictionary
        """
        # Args
        self.args = args
        self.base_fpath = base_fpath
        self.agro_fpath = agro_fpath
        self.site_fpath = site_fpath
        self.crop_fpath = crop_fpath
        self.name_fpath = name_fpath
        self.unit_fpath = unit_fpath
        self.range_fpath = range_fpath
        self.render_mode = render_mode
        self.config = config

        self.ploader = utils.ParamLoader(base_fpath, name_fpath, unit_fpath, range_fpath)
        # Arguments
        self.seed(args.seed)
        self.scale = args.scale
        self.wofost_params = args.wf
        self.agro_params = args.ag

        # Forecasting and action frequency
        self.intervention_interval = args.intvn_interval
        self.forecast_length = args.forecast_length
        self.forecast_noise = args.forecast_noise
        self.random_reset = args.random_reset
        self.crop_rand = args.crop_rand
        self.domain_rand = args.domain_rand
        self.train_reset = args.train_reset

        # Get the weather and output variables
        self.weather_vars = args.weather_vars
        self.output_vars = args.output_vars

        self.log = self._init_log()
        # Load all model parameters from .yaml files
        self.crop = pcse.fileinput.YAMLCropDataProvider(fpath=os.path.join(base_fpath, crop_fpath))
        self.site = pcse.fileinput.YAMLSiteDataProvider(fpath=os.path.join(base_fpath, site_fpath))
        self.parameterprovider = pcse.base.ParameterProvider(sitedata=self.site, cropdata=self.crop)
        self.agromanagement = self._load_agromanagement_data(os.path.join(base_fpath, agro_fpath))

        # Get information from the agromanagement file
        self.location, self.year = self._load_site_parameters(self.agromanagement)
        self.crop_start_date = self.agromanagement['CropCalendar']['crop_start_date']
        self.crop_end_date = self.agromanagement['CropCalendar']['crop_end_date']
        self.site_start_date = self.agromanagement['SiteCalendar']['site_start_date']
        self.site_end_date = self.agromanagement['SiteCalendar']['site_end_date'] 
        self.year_difference = self.crop_start_date.year - self.site_start_date.year     
        self.max_site_duration = self.site_end_date - self.site_start_date
        self.max_crop_duration = self.crop_end_date - self.crop_start_date

        self.weatherdataprovider = NASAPowerWeatherDataProvider(*self.location)

        if self.train_reset:
            self.train_weather_data = self._get_train_weather_data(year_range=self.TRAIN_YEARS)
        else:
            self.train_weather_data = self._get_train_weather_data()

        self._validate()

        # Initialize crop engine
        self.model = Wofost8Engine(self.parameterprovider, self.weatherdataprovider,
                                         self.agromanagement, config=self.config)
        
        if self.crop_rand:
            self.domain_randomization_uniform(self.scale)
        
        # Override parameters - must then call reset 
        utils.set_params(self, self.wofost_params)

        self.date = self.site_start_date
        
        # NPK/Irrigation action amounts
        self.num_fert = args.num_fert
        self.num_irrig = args.num_irrig
        self.fert_amount = args.fert_amount
        self.irrig_amount = args.irrig_amount

        self.n_recovery = args.n_recovery
        self.p_recovery = args.p_recovery
        self.k_recovery = args.k_recovery
        self.harvest_effec = args.harvest_effec
        self.irrig_effec = args.irrig_effec

        # Create action and observation spaces
        self.action_space = gym.spaces.Discrete(1+3*self.num_fert + self.num_irrig)
        self.observation_space = gym.spaces.Box(low=-np.inf, high=np.inf, \
                                shape=(1+len(self.output_vars)+len(self.weather_vars)*self.forecast_length,))

        # Rendering params
        self.render_fps = 5
        self.screen_width = 800
        self.screen_height = 600
        self.screen = None
        self.clock = None
        self.state = None
        self.isopen = True
        self.assets = args.assets_fpath

    def get_output_vars(self):
        """Return a list of the output vars"""
        return self.output_vars + self.weather_vars + ["DAYS"]
    
    def seed(self, seed: int=None):
        """Set the seed for the environment using Gym seeding.
        Minimal impact - generally will only effect Gaussian noise for 
        weather predictions
        
        Args:
            seed: int - seed for the environment"""
        if seed is None:
            seed = np.random.randint(1000000)
        np.random.seed(seed)
        return [seed]
        
    def render(self):
        """
        Render the environment into something a human can understand
        """
        render_env(self)

    def close(self):
        """
        Close the window
        """
        if self.screen is not None:
            pygame.display.quit()
            pygame.quit()
            self.isopen = False
    
    def reset(self, **kwargs):
        """Reset the environment to the initial state specified by the 
        agromanagement, crop, and soil files.
        
        Args:
            **kwargs:
                year: year to reset enviroment to for weather
                location: (latitude, longitude). Location to set environment to"""
        self.log = self._init_log()
        if 'year' in kwargs:
            self.year = kwargs['year']
            if self.year < self.WEATHER_YEARS[0] or self.year > self.WEATHER_YEARS[1] \
                or self.year in self.MISSING_YEARS:
                msg = f"Specified year {self.year} outside of range {self.WEATHER_YEARS}"
                raise exc.ResetException(msg)   
        else:
            if self.random_reset:
                self.year = self.np_random.choice(self.train_weather_data) 
            if self.train_reset:
                self.year = self.np_random.choice(self.TRAIN_YEARS)

            if self.domain_rand:
                self.domain_randomization_normal(self.scale)

        if 'location' in kwargs:
            self.location = kwargs['location']
            if self.location[0] <= -90 or self.location[0] >= 90:
                msg = f"Latitude {self.location[0]} outside of range (-90, 90)"
                raise exc.ResetException(msg)
            
            if self.location[1] <= -180 or self.location[1] >= 180:
                msg = f"Longitude {self.location[0]} outside of range (-180, 180)"
                raise exc.ResetException(msg)
            
            # Reset weather 
            self.weatherdataprovider = NASAPowerWeatherDataProvider(*self.location)
        
        self.site_start_date = self.site_start_date.replace(year=self.year)
        self.site_end_date = self.site_start_date + self.max_site_duration

        self.crop_start_date = self.crop_start_date.replace(year=self.year+self.year_difference)
        self.crop_end_date = self.crop_start_date + self.max_crop_duration
        
        self.date = self.site_start_date

        self.agromanagement['CropCalendar']['crop_start_date'] = self.crop_start_date
        self.agromanagement['CropCalendar']['crop_end_date'] = self.crop_end_date
        self.agromanagement['SiteCalendar']['site_start_date'] = self.site_start_date
        self.agromanagement['SiteCalendar']['site_end_date'] = self.site_end_date
        

        # Override parameters
        utils.set_params(self, self.wofost_params)
        
        # Reset model
        self.model = Wofost8Engine(self.parameterprovider, self.weatherdataprovider,
                                         self.agromanagement, config=self.config)
        
        output = self._run_simulation()
        observation = self._process_output(output)

        self.state = observation
        
        if self.render_mode == "human":
            self.render()

        return observation, self.log

    def domain_randomization_uniform(self, scale=0.1):
        """
        Apply a small randomization to the site and crop parameters
        """
        crop_kv = {k:v for k, v in self.parameterprovider._cropdata.items() if isinstance(v, float)}
        site_kv = {k:v for k,v in self.parameterprovider._sitedata.items() if isinstance(v, float)}

        for k, v in crop_kv.items():
            x = 1 if v == 0 else v
            self.parameterprovider.set_override(k, v+np.random.uniform(low=-x*scale,high=x*scale), check=False)
        for k, v in site_kv.items():
            x = 1 if v == 0 else v
            self.parameterprovider.set_override(k, v+np.random.uniform(low=-x*scale,high=x*scale), check=False)

    def domain_randomization_normal(self, scale=0.1):
        """
        Apply a small randomization to the site and crop parameters
        """
        crop_kv = {k:v for k, v in self.parameterprovider._cropdata.items() if isinstance(v, float)}
        site_kv = {k:v for k,v in self.parameterprovider._sitedata.items() if isinstance(v, float)}

        for k, v in crop_kv.items():
            x = 1 if v == 0 else v
            self.parameterprovider.set_override(k, v + x*np.random.normal(scale=scale), check=False)
        for k, v in site_kv.items():
            x = 1 if v == 0 else v
            self.parameterprovider.set_override(k, v + x*np.random.normal(scale=scale), check=False)
         
    def step(self, action:int):
        """Run one timestep of the environment's dynamics.

        Sends action to the WOFOST model and recieves the resulting observation
        which is then processed to the _get_reward() function and _process_output()
        function for a reward and observation

        Args:
            action: integer
        """
        if isinstance(action, dict):
            msg = f"Action must be of type `int` but is of type `dict`. Wrap environment in `pcse_gym.wrappers.NPKDictActionWrapper` before proceeding."
            raise Exception(msg)

        act_tuple = self._take_action(action)
        output = self._run_simulation()
        observation = self._process_output(output)
        
        reward = self._get_reward(output, act_tuple) 
        
        termination = output[-1]['FIN'] == 1.0 or output[-1]['FIN'] is None
        if output[-1]['FIN'] is None:
            observation = np.nan_to_num(observation)

        truncation = self.date >= self.site_end_date

        self._log(output[-1]['WSO'], act_tuple, reward)

        self.state = observation

        if self.render_mode == "human":
            self.render()
        return observation, reward, termination, truncation, self.log
    
    def _validate(self):
        """Validate that the configuration is correct """
        if self.config is None:
            msg = "Configuration Not Specified. Please use model"
            raise exc.WOFOSTGymError(msg)
        
        if 'WSO' not in self.output_vars:
            msg = 'Crop State \'WSO\' variable must be in output variables'
            raise exc.WOFOSTGymError(msg)

        if 'FIN' not in self.output_vars:
            msg = 'Crop State \'FIN\' variable must be in output variables'
            raise exc.WOFOSTGymError(msg)
        
        if self.year < self.WEATHER_YEARS[0] or self.year > self.WEATHER_YEARS[1] \
            or self.year in self.MISSING_YEARS:
            msg = f"Specified year {self.year} outside of range {self.WEATHER_YEARS}"
            raise exc.ResetException(msg) 

        if self.location[0] <= -90 or self.location[0] >= 90:
            msg = f"Latitude {self.location[0]} outside of range (-90, 90)"
            raise exc.ResetException(msg)
        
        if self.location[1] <= -180 or self.location[1] >= 180:
            msg = f"Longitude {self.location[0]} outside of range (-180, 180)"
            raise exc.ResetException(msg)
        
        if self.agromanagement["CropCalendar"]["crop_name"] == "jujube" or \
           self.agromanagement["CropCalendar"]["crop_name"] == "pear" or \
           self.agromanagement["CropCalendar"]["crop_name"] == "grape":
            if not self.perennial_env:
                msg = f"Incorrectly specified annual environment {self} with perennial crop {self.agromanagement['CropCalendar']['crop_name']}. Change environment with --env-id [env] or crop_name in agro_config.yaml"
                raise exc.ConfigFileException(msg)
            if self.agromanagement["CropCalendar"]["crop_name"] == "grape":
                if not self.grape_env:
                    msg = f"Incorrectly specified perennial environment {self} with grape variety {self.agromanagement['CropCalendar']['crop_variety']}. Change environment with --env-id [env] or crop_name in agro_config.yaml"
                    raise exc.ConfigFileException(msg)
        
    def _load_agromanagement_data(self, path: str):
        """Load the Agromanagement .yaml file
        
        Args:
            path: filepath string to agromanagement file
         """
        with open(os.path.join(path)) as file:
            agromanagement = yaml.load(file, Loader=yaml.SafeLoader)
        if "AgroManagement" in agromanagement:
            agromanagement = agromanagement["AgroManagement"]
        
        return utils.set_agro_params(agromanagement, self.agro_params)
    
    def _load_site_parameters(self, agromanagement: dict):
        """Load the site parameters from the agromanagement file. This is the
            SiteCalendar portion of the .yaml file

        Args:
            agromanagement: dictionary - see /env_config/README for information
        """
        try: 
            site_params = agromanagement['SiteCalendar']
            
            fixed_location = (site_params['latitude'], site_params['longitude'])
            fixed_year = site_params['year']
        except:
            msg = "Missing \'latitude\', \'longitude\' or \'year\' keys missing from config file"
            raise exc.ConfigFileException(msg)
        
        return fixed_location, fixed_year
    
    def _get_train_weather_data(self, year_range: list=WEATHER_YEARS, \
                                missing_years: list=MISSING_YEARS):
        """Return the valid years of historical weather data for use in the 
        NASA Weather Provider. Helpful for providing a cyclical list of data for 
        multi-year simulations.

        Generally do not need to specify these arguments, but some locations may
        not have the requisite data for that year.
        
        Args: 
            year_range: list of [low, high]
            missing_years: list of years that have missing data
        """
        valid_years = np.array([year for year in np.arange(year_range[0], year_range[1]+1) if year not in missing_years])

        leap_inds = np.argwhere(valid_years % 4 == 0).flatten()
        non_leap_inds = np.argwhere(valid_years % 4 != 0).flatten()
        leap_years = valid_years[valid_years % 4 == 0]
        non_leap_years = valid_years[valid_years % 4 != 0]

        np.random.shuffle(leap_years)
        np.random.shuffle(non_leap_years)

        valid_years[leap_inds] = leap_years
        valid_years[non_leap_inds] = non_leap_years

        return valid_years
    
    def _get_weather(self, date:date):
        """Get the weather for a range of days from the NASA Weather Provider.

        Handles weather forecasting by adding some amount of pre-specified Gaussian
        noise to the forecast. Increasing in strength as the forecast horizon
        increases.
        
        Args:
            date: datetime - day to start collecting the weather information
        """
        weather_vars = []
        noise_scale = np.linspace(start=self.forecast_noise[0], \
                                  stop=self.forecast_noise[1], num=self.forecast_length)
        
        for i in range(0, self.forecast_length):
            weather = self._get_weather_day(date + datetime.timedelta(i) )

            weather += np.random.normal(size=len(weather)) * weather * noise_scale[i] 
            weather_vars.append(weather)

        return np.array(weather_vars)

    def _get_weather_day(self, date: date):
        """Get the weather for a specific date based on the desired weather
        variables. Tracks and replaces year to ensure cyclic functionality of weather
        
        Args:
            date: datetime - day which to get weather information
        """
        site_start_ind = np.argwhere(self.train_weather_data == self.site_start_date.year).flatten()[0]
        try: 
            weather_year_ind = (site_start_ind+date.year-self.site_start_date.year) % len(self.train_weather_data)
            weatherdatacontainer = self.weatherdataprovider( 
                                date.replace(year=self.train_weather_data[weather_year_ind]))
        except:
            weatherdatacontainer = self.weatherdataprovider( 
                                date)
        return [getattr(weatherdatacontainer, attr) for attr in self.weather_vars]
    
    def _process_output(self, output: dict):
        """Process the output from the model into the observation required by
        the current environment
        
        Args:
            output: dictionary of model output variables
        """

        crop_observation = np.zeros(len(self.output_vars))
        for i,k in enumerate(self.output_vars):
            crop_observation[i] = output[-1][k]

        self.date = output[-1]["day"]

        weather_observation = self._get_weather(self.date)

        days_elapsed = self.date - self.site_start_date

        observation = np.concatenate([crop_observation, weather_observation.flatten(), [days_elapsed.days]])
        for i in range(len(observation)):
            if isinstance(observation[i], datetime.date):
                observation[i] = int(observation[i].strftime('%Y%m%d'))
            if isinstance(observation[i], deque):
                observation[i] = observation[i][0]
            if isinstance(observation[i], str):
                observation[i] = 0
        return observation.astype('float64')

    def _run_simulation(self):
        """Run the WOFOST model for the specified number of days
        """
        self.model.run(days=self.intervention_interval)

        return self.model.get_output()

    def _take_action(self, action: int):
        """Controls sending fertilization and irrigation signals to the model. 

        Converts the integer action to a signal and amount of NPK/Water to be applied.
        
        Args:
            action
        """
        msg = "\'Take Action\' method not yet implemented on %s" % self.__class__.__name__
        raise NotImplementedError(msg)

    def _get_reward(self, output: dict, act_tuple: tuple):
        """Convert the reward by applying a high penalty if a fertilization
        threshold is crossed
        
        Args:
            output     - of the simulator
            act_tuple  - amount of NPK/Water applied
        """
        return output[-1]['WSO'] if output[-1]['WSO'] is not None else 0
        
    def _init_log(self):
        """Initialize the log.
        """
        
        return {'growth': dict(), 'nitrogen': dict(), 'phosphorous': dict(), 'potassium': dict(), 'irrigation':dict(), 'reward': dict(), 'day':dict()}
    
    def _log(self, growth: float, action: int, reward: float):
        """Log the outputs into the log dictionary
        
        Args: 
            growth: float - Weight of Storage Organs
            action: int   - the action taken by the agent
            reward: float - the reward
        """

        self.log['growth'][self.date] = growth
        self.log['nitrogen'][self.date - datetime.timedelta(self.intervention_interval)] = \
            action[0]
        self.log['phosphorous'][self.date - datetime.timedelta(self.intervention_interval)] = \
            action[1]
        self.log['potassium'][self.date - datetime.timedelta(self.intervention_interval)] = \
            action[2]
        self.log['irrigation'][self.date - datetime.timedelta(self.intervention_interval)] = \
            action[3]
        self.log['reward'][self.date] = reward
        self.log['day'][self.date] = self.date  

    def _get_site_data(self):
        """
        Get the site data for a specific site and variation
        """
    
        site_data = copy.deepcopy(self.parameterprovider._sitedata)
        for k, v in self.parameterprovider._override.items():
            if k in site_data.keys():
                site_data[k] = v
        return site_data

    def _get_crop_data(self):
        """
        Get the crop data for a specific site and variation set by the agromanagment file
        """
        crop_data = copy.deepcopy(self.parameterprovider._cropdata)
        for k, v in self.parameterprovider._override.items():
            if k in crop_data.keys():
                crop_data[k] = v
        return crop_data

class Multi_NPK_Env(gym.Env):
    """Base Gym Environment for simulating crop growth
    
    Relies on the PCSE package (in base folder) and the WOFOST80 crop model. 
    """

    # Env Constants
    NUM_ACT = 4
    N = 0 # Nitrogen action
    P = 1 # Phosphorous action
    K = 2 # Potassium action
    I = 3 # Irrigation action 

    WEATHER_YEARS = [1984, 2023]
    MISSING_YEARS = []
    grape_env = False

    TRAIN_YEARS = [1990, 1994]

    SHARED_FEATURES = ["TOTN", "TOTP", "TOTK", "TOTIRRIG"]

    def __init__(self, args: NPK_Args, base_fpath: str, agro_fpath:str, \
                 site_fpath:str, crop_fpath:str, name_fpath:str, unit_fpath:str, 
                 range_fpath:str, render_mode:str=None, config:dict=None):
        """Initialize the :class:`NPK_Env`.

        Args: 
            NPK_Args: The environment parameterization
            config: Agromanagement configuration dictionary
        """
        # Args
        self.args = args
        self.base_fpath = base_fpath
        self.agro_fpath = agro_fpath
        self.site_fpath = site_fpath
        self.crop_fpath = crop_fpath
        self.name_fpath = name_fpath
        self.unit_fpath = unit_fpath
        self.range_fpath = range_fpath
        self.render_mode = render_mode
        self.config=config

        self.ploader = utils.ParamLoader(base_fpath, name_fpath, unit_fpath, range_fpath)
        # Arguments
        self.seed(args.seed)
        self.scale = args.scale
        self.wofost_params = args.wf
        self.agro_params = args.ag

        # Forecasting and action frequency
        self.intervention_interval = args.intvn_interval
        self.forecast_length = args.forecast_length
        self.forecast_noise = args.forecast_noise
        self.random_reset = args.random_reset
        self.crop_rand = args.crop_rand
        self.domain_rand = args.domain_rand
        self.train_reset = args.train_reset
        self.num_farms = args.num_farms

        # Get the weather and output variables
        self.weather_vars = args.weather_vars
        self.output_vars = args.output_vars
        self.individual_vars = [c for c in self.output_vars if c not in self.SHARED_FEATURES]
        self.shared_vars = [c for c in self.output_vars if c in self.SHARED_FEATURES]
        self.crop_vars = self.individual_vars*self.num_farms+self.shared_vars

        self.log = self._init_log()
        # Load all model parameters from .yaml files
        self.crop = pcse.fileinput.YAMLCropDataProvider(fpath=os.path.join(base_fpath, crop_fpath))
        self.site = pcse.fileinput.YAMLSiteDataProvider(fpath=os.path.join(base_fpath, site_fpath))
        self.parameterproviders = [pcse.base.ParameterProvider(sitedata=self.site, cropdata=self.crop) \
                                   for _ in range(self.num_farms)]
        self.agromanagement = self._load_agromanagement_data(os.path.join(base_fpath, agro_fpath))

        # Get information from the agromanagement file
        self.location, self.year = self._load_site_parameters(self.agromanagement)
        self.crop_start_date = self.agromanagement['CropCalendar']['crop_start_date']
        self.crop_end_date = self.agromanagement['CropCalendar']['crop_end_date']
        self.site_start_date = self.agromanagement['SiteCalendar']['site_start_date']
        self.site_end_date = self.agromanagement['SiteCalendar']['site_end_date'] 
        self.year_difference = self.crop_start_date.year - self.site_start_date.year     
        self.max_site_duration = self.site_end_date - self.site_start_date
        self.max_crop_duration = self.crop_end_date - self.crop_start_date

        self.weatherdataprovider = NASAPowerWeatherDataProvider(*self.location)

        if self.train_reset:
            self.train_weather_data = self._get_train_weather_data(year_range=self.TRAIN_YEARS)
        else:
            self.train_weather_data = self._get_train_weather_data()

        # Check that the configuration is valid
        self._validate()

        # Initialize crop engine
        self.models = [Wofost8Engine(self.parameterproviders[i], self.weatherdataprovider,
                                         self.agromanagement, config=self.config) for i in range(self.num_farms)]
        if self.crop_rand:
            self.crop_randomization(self.scale)
        
        # Override parameters - must then call reset 
        utils.set_params(self, self.wofost_params)

        self.date = self.site_start_date
        
        # NPK/Irrigation action amounts
        self.num_fert = args.num_fert
        self.num_irrig = args.num_irrig
        self.fert_amount = args.fert_amount
        self.irrig_amount = args.irrig_amount

        self.n_recovery = args.n_recovery
        self.p_recovery = args.p_recovery
        self.k_recovery = args.k_recovery
        self.harvest_effec = args.harvest_effec
        self.irrig_effec = args.irrig_effec

        # Create action and observation spaces
        self.action_space = gym.spaces.Discrete(1+3*self.num_fert + self.num_irrig)
        self.observation_space = gym.spaces.Box(low=-np.inf, high=np.inf, \
                                shape=(1+len(self.individual_vars)*self.num_farms+len(self.shared_vars)+len(self.weather_vars)*self.forecast_length,))

        # Rendering params
        self.render_fps = 5
        self.screen_width = 800
        self.screen_height = 600
        self.screen = None
        self.clock = None
        self.state = None
        self.isopen = True
        self.assets = args.assets_fpath

    def get_output_vars(self):
        """Return a list of the output vars"""
        return self.crop_vars + self.weather_vars + ["DAYS"]
    
    def seed(self, seed: int=None):
        """Set the seed for the environment using Gym seeding.
        Minimal impact - generally will only effect Gaussian noise for 
        weather predictions
        
        Args:
            seed: int - seed for the environment"""
        if seed is None:
            seed = np.random.randint(1000000)
        np.random.seed(seed)
        return [seed]
        
    def render(self):
        """
        Render the environment into something a human can understand
        """
        render_env(self)

    def close(self):
        """
        Close the window
        """
        if self.screen is not None:
            pygame.display.quit()
            pygame.quit()
            self.isopen = False
    
    def reset(self, **kwargs):
        """Reset the environment to the initial state specified by the 
        agromanagement, crop, and soil files.
        
        Args:
            **kwargs:
                year: year to reset enviroment to for weather
                location: (latitude, longitude). Location to set environment to"""
        self.log = self._init_log()
        if 'year' in kwargs:
            self.year = kwargs['year']
            if self.year < self.WEATHER_YEARS[0] or self.year > self.WEATHER_YEARS[1] \
                or self.year in self.MISSING_YEARS:
                msg = f"Specified year {self.year} outside of range {self.WEATHER_YEARS}"
                raise exc.ResetException(msg)   
        else:
            if self.random_reset:
                self.year = self.np_random.choice(self.train_weather_data) 
            if self.train_reset:
                self.year = self.np_random.choice(self.TRAIN_YEARS)

            if self.domain_rand:
                self.domain_randomization(self.scale)

        if 'location' in kwargs:
            self.location = kwargs['location']
            if self.location[0] <= -90 or self.location[0] >= 90:
                msg = f"Latitude {self.location[0]} outside of range (-90, 90)"
                raise exc.ResetException(msg)
            
            if self.location[1] <= -180 or self.location[1] >= 180:
                msg = f"Longitude {self.location[0]} outside of range (-180, 180)"
                raise exc.ResetException(msg)
            
            # Reset weather 
            self.weatherdataprovider = NASAPowerWeatherDataProvider(*self.location)
        
        self.site_start_date = self.site_start_date.replace(year=self.year)
        self.site_end_date = self.site_start_date + self.max_site_duration

        self.crop_start_date = self.crop_start_date.replace(year=self.year+self.year_difference)
        self.crop_end_date = self.crop_start_date + self.max_crop_duration

        self.date = self.site_start_date

        self.agromanagement['CropCalendar']['crop_start_date'] = self.crop_start_date
        self.agromanagement['CropCalendar']['crop_end_date'] = self.crop_end_date
        self.agromanagement['SiteCalendar']['site_start_date'] = self.site_start_date
        self.agromanagement['SiteCalendar']['site_end_date'] = self.site_end_date
        
        # Override parameters
        utils.set_params(self, self.wofost_params)
        
        # Reset model
        self.models = [Wofost8Engine(self.parameterproviders[i], self.weatherdataprovider,
                                         self.agromanagement, config=self.config) for i in range(self.num_farms)]
        
        output = self._run_simulation()
        observation = self._process_output(output)
        self.state = observation
        
        if self.render_mode == "human":
            self.render()

        return observation, self.log

    def crop_randomization(self, scale=0.1):
        """
        Apply a small randomization to the site and crop parameters
        """
        crop_kv = [{k:v for k, v in self.parameterproviders[i]._cropdata.items() if isinstance(v, float)} for i in range(self.num_farms)]
        site_kv = [{k:v for k,v in self.parameterproviders[i]._sitedata.items() if isinstance(v, float)} for i in range(self.num_farms)]
        
        self.cropdata = []
        self.sitedata = []

        for i in range(self.num_farms):
            self.cropdata.append({})
            self.sitedata.append({})
            for k, v in crop_kv[i].items():
                x = 1 if v == 0 else v
                self.cropdata[i][k] = v+np.random.uniform(low=-x*scale,high=x*scale)
                self.parameterproviders[i].set_override(k, self.cropdata[i][k], check=False)
            for k, v in site_kv[i].items():
                x = 1 if v == 0 else v
                self.sitedata[i][k] = v+np.random.uniform(low=-x*scale,high=x*scale)
                self.parameterproviders[i].set_override(k, self.sitedata[i][k], check=False)

    def domain_randomization(self, scale=0.1):
        """
        Apply a small randomization to the site and crop parameters
        """

        for i in range(self.num_farms):
            for k, v in self.cropdata[i].items():
                x = 1 if v == 0 else v
                self.parameterproviders[i].set_override(k, v + x*np.random.normal(scale=scale), check=False)
            for k, v in self.sitedata[i].items():
                x = 1 if v == 0 else v
                self.parameterproviders[i].set_override(k, v + x*np.random.normal(scale=scale), check=False)
            
    def step(self, action:int):
        """Run one timestep of the environment's dynamics.

        Sends action to the WOFOST model and recieves the resulting observation
        which is then processed to the _get_reward() function and _process_output()
        function for a reward and observation

        Args:
            action: integer
        """
        if isinstance(action, dict):
            msg = f"Action must be of type `int` but is of type `dict`. Wrap environment in `pcse_gym.wrappers.NPKDictActionWrapper` before proceeding."
            raise Exception(msg)

        act_tuple = self._take_action(action)
        output = self._run_simulation()
        observation = self._process_output(output)
        
        reward = self._get_reward(output, act_tuple) 
        

        termination = np.prod([output[i][-1]['FIN'] == 1.0 or output[i][-1]['FIN'] is None for i in range(self.num_farms)])
        if np.any([output[i][-1]['FIN'] is None for i in range(self.num_farms)]):
            observation = np.nan_to_num(observation)

        truncation = self.date >= self.site_end_date

        self._log([output[i][-1]['WSO'] for i in range(self.num_farms)], act_tuple, reward)

        self.state = observation

        if self.render_mode == "human":
            self.render()
        return observation, reward, termination, truncation, self.log
    
    def _validate(self):
        """
        Validate that the configuration is correct 
        """
        if self.config is None:
            msg = "Configuration Not Specified. Please use model"
            raise exc.WOFOSTGymError(msg)
        
        if 'WSO' not in self.output_vars:
            msg = 'Crop State \'WSO\' variable must be in output variables'
            raise exc.WOFOSTGymError(msg)

        if 'FIN' not in self.output_vars:
            msg = 'Crop State \'FIN\' variable must be in output variables'
            raise exc.WOFOSTGymError(msg)
        
        if self.year < self.WEATHER_YEARS[0] or self.year > self.WEATHER_YEARS[1] \
            or self.year in self.MISSING_YEARS:
            msg = f"Specified year {self.year} outside of range {self.WEATHER_YEARS}"
            raise exc.ResetException(msg) 

        if self.location[0] <= -90 or self.location[0] >= 90:
            msg = f"Latitude {self.location[0]} outside of range (-90, 90)"
            raise exc.ResetException(msg)
        
        if self.location[1] <= -180 or self.location[1] >= 180:
            msg = f"Longitude {self.location[0]} outside of range (-180, 180)"
            raise exc.ResetException(msg)
        
        if self.agromanagement["CropCalendar"]["crop_name"] == "jujube" or \
           self.agromanagement["CropCalendar"]["crop_name"] == "pear" or \
           self.agromanagement["CropCalendar"]["crop_name"] == "grape":
            if not self.perennial_env:
                msg = f"Incorrectly specified annual environment {self} with perennial crop {self.agromanagement['CropCalendar']['crop_name']}. Change environment with --env-id [env] or crop_name in agro_config.yaml"
                raise exc.ConfigFileException(msg)
            if self.agromanagement["CropCalendar"]["crop_name"] == "grape":
                if not self.grape_env:
                    msg = f"Incorrectly specified perennial environment {self} with grape variety {self.agromanagement['CropCalendar']['crop_variety']}. Change environment with --env-id [env] or crop_name in agro_config.yaml"
                    raise exc.ConfigFileException(msg)
        
    def _load_agromanagement_data(self, path: str):
        """Load the Agromanagement .yaml file
        
        Args:
            path: filepath string to agromanagement file
         """
        with open(os.path.join(path)) as file:
            agromanagement = yaml.load(file, Loader=yaml.SafeLoader)
        if "AgroManagement" in agromanagement:
            agromanagement = agromanagement["AgroManagement"]
        
        return utils.set_agro_params(agromanagement, self.agro_params)
    
    def _load_site_parameters(self, agromanagement: dict):
        """Load the site parameters from the agromanagement file. This is the
            SiteCalendar portion of the .yaml file

        Args:
            agromanagement: dictionary - see /env_config/README for information
        """
        try: 
            site_params = agromanagement['SiteCalendar']
            
            fixed_location = (site_params['latitude'], site_params['longitude'])
            fixed_year = site_params['year']
        except:
            msg = "Missing \'latitude\', \'longitude\' or \'year\' keys missing from config file"
            raise exc.ConfigFileException(msg)
        
        return fixed_location, fixed_year
    
    def _get_train_weather_data(self, year_range: list=WEATHER_YEARS, \
                                missing_years: list=MISSING_YEARS):
        """Return the valid years of historical weather data for use in the 
        NASA Weather Provider. Helpful for providing a cyclical list of data for 
        multi-year simulations.

        Generally do not need to specify these arguments, but some locations may
        not have the requisite data for that year.
        
        Args: 
            year_range: list of [low, high]
            missing_years: list of years that have missing data
        """
        valid_years = np.array([year for year in np.arange(year_range[0], year_range[1]+1) if year not in missing_years])

        leap_inds = np.argwhere(valid_years % 4 == 0).flatten()
        non_leap_inds = np.argwhere(valid_years % 4 != 0).flatten()
        leap_years = valid_years[valid_years % 4 == 0]
        non_leap_years = valid_years[valid_years % 4 != 0]

        np.random.shuffle(leap_years)
        np.random.shuffle(non_leap_years)

        valid_years[leap_inds] = leap_years
        valid_years[non_leap_inds] = non_leap_years

        return valid_years
    
    def _get_weather(self, date:date):
        """Get the weather for a range of days from the NASA Weather Provider.

        Handles weather forecasting by adding some amount of pre-specified Gaussian
        noise to the forecast. Increasing in strength as the forecast horizon
        increases.
        
        Args:
            date: datetime - day to start collecting the weather information
        """
        weather_vars = []
        noise_scale = np.linspace(start=self.forecast_noise[0], \
                                  stop=self.forecast_noise[1], num=self.forecast_length)
        
        for i in range(0, self.forecast_length):
            weather = self._get_weather_day(date + datetime.timedelta(i) )

            weather += np.random.normal(size=len(weather)) * weather * noise_scale[i] 
            weather_vars.append(weather)

        return np.array(weather_vars)

    def _get_weather_day(self, date: date):
        """Get the weather for a specific date based on the desired weather
        variables. Tracks and replaces year to ensure cyclic functionality of weather
        
        Args:
            date: datetime - day which to get weather information
        """

        site_start_ind = np.argwhere(self.train_weather_data == self.site_start_date.year).flatten()[0]
        weather_year_ind = (site_start_ind+date.year-self.site_start_date.year) % len(self.train_weather_data)
        weatherdatacontainer = self.weatherdataprovider( 
                            date.replace(year=self.train_weather_data[weather_year_ind]))

        return [getattr(weatherdatacontainer, attr) for attr in self.weather_vars]
    
    def _process_output(self, output: dict):
        """Process the output from the model into the observation required by
        the current environment
        
        Args:
            output: dictionary of model output variables
        """

        crop_observation = np.zeros(self.num_farms*len(self.individual_vars)+len(self.shared_vars))
        for i in range(self.num_farms):
            for j,k in enumerate(self.individual_vars):
                crop_observation[i*len(self.individual_vars)+j] = output[i][-1][k]
        for i,k in enumerate(self.shared_vars):
            crop_observation[self.num_farms*len(self.individual_vars)+i] = output[-1][-1][k]
        self.date = output[0][-1]["day"]

        weather_observation = self._get_weather(self.date)

        days_elapsed = self.date - self.site_start_date

        observation = np.concatenate([crop_observation, weather_observation.flatten(), [days_elapsed.days]])
        for i in range(len(observation)):
            if isinstance(observation[i], datetime.date):
                observation[i] = int(observation[i].strftime('%Y%m%d'))
            if isinstance(observation[i], deque):
                observation[i] = observation[i][0]
            if isinstance(observation[i], str):
                observation[i] = 0
        return observation.astype('float64')

    def _run_simulation(self):
        """Run the WOFOST model for the specified number of days
        """
        [self.models[i].run(days=self.intervention_interval) for i in range(self.num_farms)]

        return [self.models[i].get_output() for i in range(self.num_farms)]

    def _take_action(self, action: int):
        """Controls sending fertilization and irrigation signals to the model. 

        Converts the integer action to a signal and amount of NPK/Water to be applied.
        
        Args:
            action
        """
        msg = "\'Take Action\' method not yet implemented on %s" % self.__class__.__name__
        raise NotImplementedError(msg)

    def _get_reward(self, output: dict, act_tuple: tuple):
        """Convert the reward by applying a high penalty if a fertilization
        threshold is crossed
        
        Args:
            output     - of the simulator
            act_tuple  - amount of NPK/Water applied
        """
        reward = 0
        for i in range(self.num_farms):
            reward += output[i][-1]['WSO'] if output[i][-1]['WSO'] is not None else 0
        return reward
        
    def _init_log(self):
        """Initialize the log.
        """
        
        return {'growth': dict(), 'nitrogen': dict(), 'phosphorous': dict(), 'potassium': dict(), 'irrigation':dict(), 'reward': dict(), 'day':dict()}
    
    def _log(self, growth: float, action: int, reward: float):
        """Log the outputs into the log dictionary
        
        Args: 
            growth: float - Weight of Storage Organs
            action: int   - the action taken by the agent
            reward: float - the reward
        """

        self.log['growth'][self.date] = growth
        self.log['nitrogen'][self.date - datetime.timedelta(self.intervention_interval)] = \
            action[0]
        self.log['phosphorous'][self.date - datetime.timedelta(self.intervention_interval)] = \
            action[1]
        self.log['potassium'][self.date - datetime.timedelta(self.intervention_interval)] = \
            action[2]
        self.log['irrigation'][self.date - datetime.timedelta(self.intervention_interval)] = \
            action[3]
        self.log['reward'][self.date] = reward
        self.log['day'][self.date] = self.date  

    def _get_site_data(self, i):
        """
        Get the site data for a specific site and variation
        """
    
        site_data = copy.deepcopy(self.parameterproviders[i]._sitedata)
        for k, v in self.parameterproviders[i]._override.items():
            if k in site_data.keys():
                site_data[k] = v
        return site_data

    def _get_crop_data(self, i):
        """
        Get the crop data for a specific site and variation set by the agromanagment file
        """
        crop_data = copy.deepcopy(self.parameterproviders[i]._cropdata)
        for k, v in self.parameterproviders[i]._override.items():
            if k in crop_data.keys():
                crop_data[k] = v
        return crop_data
    
class Plant_NPK_Env(NPK_Env):

    """Base Gym Environment for simulating crop growth with planting and 
    harvesting actions. Does not automatically start crop
    
    Relies on the PCSE package (in base folder) and the WOFOST80 crop model. 
    """
    # Env Constants
    NUM_ACT = 6
    P = 0 # Plant action
    H = 1 # Harvest action
    N = 2 # Nitrogen action
    P = 3 # Phosphorous action
    K = 4 # Potassium action
    I = 5 # Irrigation action 

    def __init__(self, args: NPK_Args, base_fpath: str, agro_fpath:str, \
                 site_fpath:str, crop_fpath:str, name_fpath:str, unit_fpath:str, 
                 range_fpath:str, render_mode:str=None, config:dict=None):
        """Initialize the :class:`Plant_NPK_Env`.

        Args: 
            NPK_Args: The environment parameterization
            config: Agromanagement configuration dictionary
        """
        super().__init__(args, base_fpath, agro_fpath, site_fpath, crop_fpath, \
                         name_fpath, unit_fpath, range_fpath, render_mode, config=config)

        self.crop_name = self.agromanagement['CropCalendar']['crop_name']
        self.crop_variety = self.agromanagement['CropCalendar']['crop_variety']
        self.crop_start_type = self.agromanagement['CropCalendar']['crop_start_type']
        self.crop_end_type = self.agromanagement['CropCalendar']['crop_end_type']
        self.active_crop_flag = False

    def _take_action(self, action: int):
        """Sends action to the model
        """
        msg = "\'Take Action\' method not yet implemented on %s" % self.__class__.__name__
        raise NotImplementedError(msg)

    def _init_log(self):
        """Initialize the log.
        """
        return {'growth': dict(), 'plant': dict(), 'harvest': dict(), 'nitrogen': dict(), \
                'phosphorous': dict(), 'potassium': dict(), 'irrigation':dict(), 'reward': dict(), 'day':dict()}
    
    def _log(self, growth: float, action: int, reward: float):
        """Log the outputs into the log dictionary
        
        Args: 
            growth: float - Weight of Storage Organs
            action: int   - the action taken by the agent
            reward: float - the reward
        """
        self.log['growth'][self.date] = growth
        self.log['plant'][self.date] = action[0]
        self.log['harvest'][self.date] = action[1]
        self.log['nitrogen'][self.date - datetime.timedelta(self.intervention_interval)] = \
            action[2]
        self.log['phosphorous'][self.date - datetime.timedelta(self.intervention_interval)] = \
            action[3]
        self.log['potassium'][self.date - datetime.timedelta(self.intervention_interval)] = \
            action[4]
        self.log['irrigation'][self.date - datetime.timedelta(self.intervention_interval)] = \
            action[5]
        self.log['reward'][self.date] = reward
        self.log['day'][self.date] = self.date  

class Harvest_NPK_Env(NPK_Env):
    """Base Gym Environment for simulating crop growth with only 
    harvesting actions. Automatically starts crop but does not handle harvesting.
    Useful in perennial models
    
    Relies on the PCSE package (in base folder) and the WOFOST80 crop model. 
    """
    # Env Constants
    NUM_ACT = 5
    H = 0 # Harvest action
    N = 1 # Nitrogen action
    P = 2 # Phosphorous action
    K = 3 # Potassium action
    I = 4 # Irrigation action 

    def __init__(self, args: NPK_Args, base_fpath: str, agro_fpath:str, \
                 site_fpath:str, crop_fpath:str, name_fpath:str, unit_fpath:str, 
                 range_fpath:str, render_mode:str=None, config:dict=None):
        """Initialize the :class:`Plant_NPK_Env`.

        Args: 
            NPK_Args: The environment parameterization
            config: Agromanagement configuration dictionary
        """
        super().__init__(args, base_fpath, agro_fpath, site_fpath, crop_fpath, \
                         name_fpath, unit_fpath, range_fpath, render_mode, config=config)

        self.crop_name = self.agromanagement['CropCalendar']['crop_name']
        self.crop_variety = self.agromanagement['CropCalendar']['crop_variety']
        self.crop_start_type = self.agromanagement['CropCalendar']['crop_start_type']
        self.crop_end_type = self.agromanagement['CropCalendar']['crop_end_type']
        self.active_crop_flag = False

    def _take_action(self, action: int):
        """Sends action to the model
        """
        msg = "\'Take Action\' method not yet implemented on %s" % self.__class__.__name__
        raise NotImplementedError(msg)

    def _init_log(self):
        """Initialize the log.
        """
        return {'growth': dict(), 'harvest': dict(), 'nitrogen': dict(), \
                'phosphorous': dict(), 'potassium': dict(), 'irrigation':dict(), 'reward': dict(), 'day':dict()}
    
    def _log(self, growth: float, action: int, reward: float):
        """Log the outputs into the log dictionary
        
        Args: 
            growth: float - Weight of Storage Organs
            action: int   - the action taken by the agent
            reward: float - the reward
        """
        self.log['growth'][self.date] = growth
        self.log['harvest'][self.date] = action[0]
        self.log['nitrogen'][self.date - datetime.timedelta(self.intervention_interval)] = \
            action[1]
        self.log['phosphorous'][self.date - datetime.timedelta(self.intervention_interval)] = \
            action[2]
        self.log['potassium'][self.date - datetime.timedelta(self.intervention_interval)] = \
            action[3]
        self.log['irrigation'][self.date - datetime.timedelta(self.intervention_interval)] = \
            action[4]
        self.log['reward'][self.date] = reward
        self.log['day'][self.date] = self.date  

class LNPKW(gym.Env):
    """Limited N/P/K Water"""
    def __init__():
        pass

class PP(gym.Env):
    """Potential Production"""
    def __init__():
        pass

class LNPK(gym.Env):
    """Limited N/P/K """
    def __init__():
        pass

class LN(gym.Env):
    """Limited N"""
    def __init__():
        pass

class LNW(gym.Env):
    """Limited N and Water"""
    def __init__():
        pass

class LW(gym.Env):
    """Limited Water"""
    def __init__():
        pass
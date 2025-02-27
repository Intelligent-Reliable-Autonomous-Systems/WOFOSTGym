"""YAML File reader for the Crop Data file

Written by: Allard de Wit (allard.dewit@wur.nl), April 2014
Modified by Will Solow, 2024
"""
import logging
import os, sys

import logging
import os
import pickle
import yaml

from ..base import MultiCropDataProvider
from .. import exceptions as exc
from ..util import version_tuple, get_working_directory


class YAMLCropDataProvider(MultiCropDataProvider):
    """A crop data provider for reading crop parameter sets stored in the YAML format.

        :param fpath: full path to directory containing YAML files
        :param repository: URL to repository containg YAML files. This url should be
         the *raw* content (e.g. starting with 'https://raw.githubusercontent.com')
        :param force_reload: If set to True, the cache file is ignored and al
         parameters are reloaded (default False).

    This crop data provider can read and store the parameter sets for multiple
    crops which is different from most other crop data providers that only can
    hold data for a single crop. This crop data providers is therefore suitable
    for running crop rotations with different crop types as the data provider
    can switch the active crop.

    The most basic use is to call YAMLCropDataProvider with no parameters. It will
    than pull the crop parameters from my github repository at
    https://github.com/ajwdewit/WOFOST_crop_parameters::

        >>> from pcse.fileinput import YAMLCropDataProvider
        >>> p = YAMLCropDataProvider()
        >>> print(p)
        YAMLCropDataProvider - crop and variety not set: no activate crop parameter set!

    All crops and varieties have been loaded from the YAML file, however no activate
    crop has been set. Therefore, we need to activate a a particular crop and variety:

        >>> p.set_active_crop('wheat', 'Winter_wheat_101')
        >>> print(p)
        YAMLCropDataProvider - current active crop 'wheat' with variety 'Winter_wheat_101'
        Available crop parameters:
         {'DTSMTB': [0.0, 0.0, 30.0, 30.0, 45.0, 30.0], 'NLAI_NPK': 1.0, 'NRESIDLV': 0.004,
         'KCRIT_FR': 1.0, 'RDRLV_NPK': 0.05, 'TCPT': 10, 'DEPNR': 4.5, 'KMAXRT_FR': 0.5,
         ...
         ...
         'TSUM2': 1194, 'TSUM1': 543, 'TSUMEM': 120}

    Additionally, it is possible to load YAML parameter files from your local file system::

        >>> p = YAMLCropDataProvider(fpath=r"D:\\UserData\\sources\\WOFOST_crop_parameters")
        >>> print(p)
        YAMLCropDataProvider - crop and variety not set: no activate crop parameter set!

    Finally, it is possible to pull data from your fork of my github repository by specifying
    the URL to that repository::

        >>> p = YAMLCropDataProvider(repository=\"https://raw.githubusercontent.com/<your_account>/WOFOST_crop_parameters/master/\")

    To increase performance of loading parameters, the YAMLCropDataProvider will create a
    cache file that can be restored much quicker compared to loading the YAML files.
    When reading YAML files from the local file system, care is taken to ensure that the
    cache file is re-created when updates to the local YAML are made. However, it should
    be stressed that this is *not* possible when parameters are retrieved from a URL
    and there is a risk that parameters are loaded from an outdated cache file. In that
    case use `force_reload=True` to force loading the parameters from the URL.
    """

    current_crop_name = None
    current_crop_variety = None

    # Compatibility of data provider with YAML parameter file version
    compatible_version = "1.0.0"

    def __init__(self, fpath=None, force_reload=False):
        """Initialize the YAMLCropDataProivder class by first inheriting from the 
        MultiCropDataProvider class
        """
        MultiCropDataProvider.__init__(self)

        # either force a reload or load cache fails
        if force_reload is True or self._load_cache(fpath) is False:  
            # enforce a clear state
            self.clear()
            self._store.clear()

            if fpath is not None:
                self.read_local_repository(fpath)
            else:
                msg = f"No path or URL specified where to find YAML crop parameter files" 
                self.logger.info(msg)
                exc.PCSEError(msg)

            with open(self._get_cache_fname(fpath), "wb") as fp:
                pickle.dump((self.compatible_version, self._store), fp, pickle.HIGHEST_PROTOCOL)

    def read_local_repository(self, fpath):
        """Reads the crop YAML files on the local file system

        :param fpath: the location of the YAML files on the filesystem
        """
        yaml_file_names = self._get_yaml_files(fpath)
        for crop_name, yaml_fname in yaml_file_names.items():
            with open(yaml_fname) as fp:
                parameters = yaml.safe_load(fp)
            self._check_version(parameters, crop_fname=yaml_fname)
            self._add_crop(crop_name, parameters)

    def _get_cache_fname(self, fpath):
        """Returns the name of the cache file for the CropDataProvider.
        """
        cache_fname = "%s.pkl" % self.__class__.__name__
        if fpath is None:
            PCSE_USER_HOME = os.path.join(get_working_directory(), ".pcse")
            METEO_CACHE_DIR = os.path.join(PCSE_USER_HOME, "meteo_cache")
            cache_fname_fp = os.path.join(METEO_CACHE_DIR, cache_fname)
        else:
            cache_fname_fp = os.path.join(fpath, cache_fname)
        return cache_fname_fp

    def _load_cache(self, fpath):
        """Loads the cache file if possible and returns True, else False.
        """
        try:
            cache_fname_fp = self._get_cache_fname(fpath)
            if os.path.exists(cache_fname_fp):

                # First we check that the cache file reflects the contents of the YAML files.
                # This only works for files not for github repos
                if fpath is not None:
                    yaml_file_names = self._get_yaml_files(fpath)
                    yaml_file_dates = [os.stat(fn).st_mtime for crop,fn in yaml_file_names.items()]
                    # retrieve modification date of cache file
                    cache_date = os.stat(cache_fname_fp).st_mtime
                    # Ensure cache file is more recent then any of the YAML files
                    if any([d > cache_date for d in yaml_file_dates]):
                        return False

                # Now start loading the cache file
                with open(cache_fname_fp, "rb") as fp:
                    version, store = pickle.load(fp)
                if version_tuple(version) != version_tuple(self.compatible_version):
                    msg = "Cache file is from a different version of YAMLCropDataProvider"
                    raise exc.PCSEError(msg)
                self._store = store
                return True

        except Exception as e:
            msg = "%s - Failed to load cache file: %s" % (self.__class__.__name__, e)
            print(msg)

        return False

    def _check_version(self, parameters, crop_fname):
        """Checks the version of the parameter input with the version supported by this data provider.

        Raises an exception if the parameter set is incompatible.

        :param parameters: The parameter set loaded by YAML
        """
        try:
            v = parameters['Version']
            if version_tuple(v) != version_tuple(self.compatible_version):
                msg = "Version supported by %s is %s, while parameter set version is %s!"
                raise exc.PCSEError(msg % (self.__class__.__name__, self.compatible_version, parameters['Version']))
        except Exception as e:
            msg = f"Version check failed on crop parameter file: {crop_fname}"
            raise exc.PCSEError(msg)

    def _add_crop(self, crop_name, parameters):
        """Store the parameter sets for the different varieties for the given crop.
        """
        variety_sets = parameters["CropParameters"]["Varieties"]
        self._store[crop_name] = variety_sets

    def _get_yaml_files(self, fpath):
        """Returns all the files ending on *.yaml in the given path.
        """
        fname = os.path.join(fpath, "crops.yaml")
        if not os.path.exists(fname):
            msg = "Cannot find 'crops.yaml' at {f}".format(f=fname)
            raise exc.PCSEError(msg)
        crop_names = yaml.safe_load(open(fname))["available_crops"]
        crop_yaml_fnames = {crop: os.path.join(fpath, crop + ".yaml") for crop in crop_names}
        for crop, fname in crop_yaml_fnames.items():
            if not os.path.exists(fname):
                msg = f"Cannot find yaml file for crop '{crop}': {fname}"
                raise RuntimeError(msg)
        return crop_yaml_fnames

    def set_active_crop(self, crop_name, crop_variety):
        """Sets the parameters in the internal dict for given crop_name and crop_variety

        It first clears the active set of crop parameters in the internal dict.

        :param crop_name: the name of the crop
        :param crop_variety: the variety for the given crop
        """
        self.clear()
        if crop_name not in self._store:
            msg = "Crop name '%s' not available in %s " % (crop_name, self.__class__.__name__)
            raise exc.PCSEError(msg)
        variety_sets = self._store[crop_name]
        if crop_variety not in variety_sets:
            msg = "Variety name '%s' not available for crop '%s' in " \
                  "%s " % (crop_variety, crop_name, self.__class__.__name__)
            raise exc.PCSEError(msg)

        self.current_crop_name = crop_name
        self.current_crop_variety = crop_variety

        # Retrieve parameter name/values from input (ignore description and units)
        parameters = {k: v[0] for k, v in variety_sets[crop_variety].items() if k != "Metadata"}
        # update internal dict with parameter values for this variety
        self.update(parameters)

    def get_default_data(self, crop_name, crop_variety):
        """
        Gets the default crop set by the agromanagement file
        """
        variety_sets = self._store[crop_name]

        return {k: v[0] for k, v in variety_sets[crop_variety].items() if k != "Metadata"}

    def get_crops_varieties(self):
        """Return the names of available crops and varieties per crop.

        :return: a dict of type {'crop_name1': ['crop_variety1', 'crop_variety1', ...],
                                 'crop_name2': [...]}
        """
        return {k: v.keys() for k, v in self._store.items()}

    def print_crops_varieties(self):
        """Gives a printed list of crops and varieties on screen.
        """
        msg = ""
        for crop, varieties in self.get_crops_varieties().items():
            msg += "crop '%s', available varieties:\n" % crop
            for var in varieties:
                msg += (" - '%s'\n" % var)
        print(msg)

    def __str__(self):
        if not self:
            msg = "%s - crop and variety not set: no active crop parameter set!\n" % self.__class__.__name__
            return msg
        else:
            msg = "%s - current active crop '%s' with variety '%s'\n" % \
                  (self.__class__.__name__, self.current_crop_name, self.current_crop_variety)
            msg += "Available crop parameters:\n %s" % str(dict.__str__(self))
            return msg

    @property
    def logger(self):
        loggername = "%s.%s" % (self.__class__.__module__,
                                self.__class__.__name__)
        return logging.getLogger(loggername)
"""YAML File reader for the Soil Data file (also includes soil data parameters by default)

Written by: Allard de Wit (allard.dewit@wur.nl), April 2014
Modified by Will Solow, 2024
"""

import logging
import os
import pickle
import yaml

from pcse.base import MultiSoilDataProvider
from pcse.utils import exceptions as exc
from pcse.util import version_tuple, get_working_directory


class YAMLSoilDataProvider(MultiSoilDataProvider):
    """A soil data provider for reading soil and soil parameter sets stored in the YAML format.
       This directly extends the soil format by allowing multiple soils to be created
       with different parameters

        :param fpath: full path to directory containing YAML files
        :param force_reload: If set to True, the cache file is ignored and al
         parameters are reloaded (default False).

    This soil data provider can read and store the parameter sets for multiple
    soils which is different from most other soil data providers that only can
    hold data for a single soil/soil type.
    """

    current_soil_name = None
    current_soil_variation = None

    # Compatibility of data provider with YAML parameter file version
    compatible_version = "1.0.0"

    def __init__(self, fpath: str = None, force_reload: bool = False) -> None:
        """Initialize the YAMLSoilDataProivder class by first inheriting from the
        MultiSoilDataProvider class
        """
        MultiSoilDataProvider.__init__(self)

        # either force a reload or load cache fails
        if force_reload is True or self._load_cache(fpath) is False:
            # enforce a clear state
            self.clear()
            self._store.clear()

            if fpath is not None:
                self.read_local_repository(fpath)

            else:
                msg = f"No path or specified where to find YAML soil parameter files "
                self.logger.info(msg)
                exc.PCSEError(msg)

            with open(self._get_cache_fname(fpath), "wb") as fp:
                pickle.dump((self.compatible_version, self._store), fp, pickle.HIGHEST_PROTOCOL)

    def read_local_repository(self, fpath: str) -> None:
        """Reads the soil YAML files on the local file system

        :param fpath: the location of the YAML files on the filesystem
        """
        yaml_file_names = self._get_yaml_files(fpath)
        for soil_name, yaml_fname in yaml_file_names.items():
            with open(yaml_fname) as fp:
                parameters = yaml.safe_load(fp)
            self._check_version(parameters, soil_fname=yaml_fname)
            self._add_soil(soil_name, parameters)

    def _get_cache_fname(self, fpath: str) -> str:
        """Returns the name of the cache file for the SoilDataProvider."""
        cache_fname = "%s.pkl" % self.__class__.__name__
        if fpath is None:
            PCSE_USER_HOME = os.path.join(get_working_directory(), ".pcse")
            METEO_CACHE_DIR = os.path.join(PCSE_USER_HOME, "meteo_cache")
            cache_fname_fp = os.path.join(METEO_CACHE_DIR, cache_fname)
        else:
            cache_fname_fp = os.path.join(fpath, cache_fname)
        return cache_fname_fp

    def _load_cache(self, fpath: str) -> bool:
        """Loads the cache file if possible and returns True, else False."""
        try:
            cache_fname_fp = self._get_cache_fname(fpath)
            if os.path.exists(cache_fname_fp):

                # First we check that the cache file reflects the contents of the YAML files.
                # This only works for files not for github repos
                if fpath is not None:
                    yaml_file_names = self._get_yaml_files(fpath)
                    yaml_file_dates = [os.stat(fn).st_mtime for soil, fn in yaml_file_names.items()]
                    # retrieve modification date of cache file
                    cache_date = os.stat(cache_fname_fp).st_mtime
                    # Ensure cache file is more recent then any of the YAML files
                    if any([d > cache_date for d in yaml_file_dates]):
                        return False

                # Now start loading the cache file
                with open(cache_fname_fp, "rb") as fp:
                    version, store = pickle.load(fp)
                if version_tuple(version) != version_tuple(self.compatible_version):
                    msg = "Cache file is from a different version of YAMLSoilDataProvider"
                    raise exc.PCSEError(msg)
                self._store = store
                return True

        except Exception as e:
            msg = "%s - Failed to load cache file: %s" % (self.__class__.__name__, e)
            print(msg)

        return False

    def _check_version(self, parameters: dict, soil_fname: str) -> None:
        """Checks the version of the parameter input with the version supported by this data provider.

        Raises an exception if the parameter set is incompatible.

        :param parameters: The parameter set loaded by YAML
        """
        try:
            v = parameters["Version"]
            if version_tuple(v) != version_tuple(self.compatible_version):
                msg = "Version supported by %s is %s, while parameter set version is %s!"
                raise exc.PCSEError(msg % (self.__class__.__name__, self.compatible_version, parameters["Version"]))
        except Exception as e:
            msg = f"Version check failed on soil parameter file: {soil_fname}"
            raise exc.PCSEError(msg)

    def _add_soil(self, soil_name: str, parameters: dict) -> None:
        """Store the parameter sets for the different varieties for the given soil."""
        variation_sets = parameters["SoilParameters"]["Variations"]
        self._store[soil_name] = variation_sets

    def _get_yaml_files(self, fpath: str) -> list[str]:
        """Returns all the files ending on *.yaml in the given path."""
        fname = os.path.join(fpath, "soils.yaml")
        if not os.path.exists(fname):
            msg = "Cannot find 'soils.yaml' at {f}".format(f=fname)
            raise exc.PCSEError(msg)
        soil_names = yaml.safe_load(open(fname))["available_soils"]
        soil_yaml_fnames = {soil: os.path.join(fpath, soil + ".yaml") for soil in soil_names}
        for soil, fname in soil_yaml_fnames.items():
            if not os.path.exists(fname):
                msg = f"Cannot find yaml file for soil '{soil}': {fname}"
                raise RuntimeError(msg)
        return soil_yaml_fnames

    def set_active_soil(self, soil_name: str, soil_variation: str) -> None:
        """Sets the parameters in the internal dict for given soil_name and soil_variation

        It first clears the active set of soil/soil parameters in the internal dict.

        :param soil_name: the name of the soil
        :param soil_variation: the variation for the given soil
        """
        self.clear()
        if soil_name not in self._store:
            msg = "Soil name '%s' not available in %s " % (soil_name, self.__class__.__name__)
            raise exc.PCSEError(msg)
        variation_sets = self._store[soil_name]
        if soil_variation not in variation_sets:
            msg = "Variation name '%s' not available for soil '%s' in " "%s " % (
                soil_variation,
                soil_name,
                self.__class__.__name__,
            )
            raise exc.PCSEError(msg)

        self.current_soil_name = soil_name
        self.current_soil_variation = soil_variation

        # Retrieve parameter name/values from input (ignore description and units)
        parameters = {k: v[0] for k, v in variation_sets[soil_variation].items() if k != "Metadata"}
        # update internal dict with parameter values for this variety
        self.update(parameters)

    def get_default_data(self, soil_name: str, soil_variation: str) -> dict:
        """
        Gets the default soil set by the agromanagement file
        """
        variation_sets = self._store[soil_name]

        return {k: v[0] for k, v in variation_sets[soil_variation].items() if k != "Metadata"}

    def get_soil_variations(self) -> dict[str, str]:
        """Return the names of available soils and variations per soil.

        :return: a dict of type {'soil_name1': ['soil_variation1', 'soil_variation1', ...],
                                 'soil_name2': [...]}
        """
        return {k: v.keys() for k, v in self._store.items()}

    def print_soil_variations(self) -> None:
        """Gives a printed list of soils and variations on screen."""
        msg = ""
        for soil, variation in self.get_soil_variations().items():
            msg += "soil '%s', available varieties:\n" % soil
            for var in variation:
                msg += " - '%s'\n" % var
        print(msg)

    def __str__(self) -> str:
        if not self:
            msg = "%s - soil and variation not set: no active soil parameter set!\n" % self.__class__.__name__
            return msg
        else:
            msg = "%s - current active soil '%s' with variation '%s'\n" % (
                self.__class__.__name__,
                self.current_soil_name,
                self.current_soil_variation,
            )
            msg += "Available soil parameters:\n %s" % str(dict.__str__(self))
            return msg

    @property
    def logger(self) -> logging.Logger:
        loggername = "%s.%s" % (self.__class__.__module__, self.__class__.__name__)
        return logging.getLogger(loggername)

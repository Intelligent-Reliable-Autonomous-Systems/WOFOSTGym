"""Base classes Parameter Provider and includes parameter providers for crop
and soil modules

Written by: Allard de Wit (allard.dewit@wur.nl), April 2014
Modified by Will Solow, 2024
"""

import logging
from collections import Counter
from collections.abc import MutableMapping
from pcse.utils import exceptions as exc


class MultiCropDataProvider(dict):
    """Provides base class for Crop Data loading from .yaml files"""

    def __init__(self) -> None:
        """Initialize class `MultiCropDataProvider"""
        dict.__init__(self)
        self._store = {}

    def set_active_crop(self, crop_name: str, crop_variety: str) -> None:
        """Sets the crop parameters for the crop identified by crop_name and crop_variety.

        Needs to be implemented by each subclass of MultiCropDataProvider
        """
        msg = "'set_crop_type' method should be implemented specifically for each" "subclass of MultiCropDataProvider."
        raise NotImplementedError(msg)


class MultiSoilDataProvider(dict):
    """Provides base class for Soil Data loading from .yaml files"""

    def __init__(self) -> None:
        """Initialize class `MultiSoilDataProvider"""
        dict.__init__(self)
        self._store = {}

    def set_active_crop(self, soil_name: str, soil_variation: str) -> None:
        """Sets the crop parameters for the crop identified by soil_name and soil_variation.

        Needs to be implemented by each subclass of MultiSoilDataProvider
        """
        msg = "'set_crop_type' method should be implemented specifically for each" "subclass of MultiSoilDataProvider."
        raise NotImplementedError(msg)


class ParameterProvider(MutableMapping):
    """Class providing a dictionary-like interface over all parameter sets (crop, soil, soil).
    It acts very much like a ChainMap with some additional features.

    The idea behind this class is threefold. First of all by encapsulating the
    different parameter sets (agrodata, cropdata, soildata) into a single object,
    the signature of the `initialize()` method of each `SimulationObject` can be
    harmonized across all SimulationObjects. Second, the ParameterProvider itself
    can be easily adapted when different sets of parameter values are needed. For
    example when running PCSE with crop rotations, different sets of cropdata
    are needed, this can now be handled easily by enhancing
    ParameterProvider to rotate a new set of cropdata when the engine receives a
    CROP_START signal. Finally, specific parameter values can be easily changed
    by setting an `override` on that parameter.

    See also the `MultiCropDataProvider` and the `MultieSoilDataProvider`
    """

    _maps = list()
    _soildata = dict()
    _cropdata = dict()
    _timerdata = dict()
    _override = dict()
    _iter = 0  # Counter for iterator
    _ncrops_activated = 0  # Counts the number of times `set_crop_type()` has been called.
    _nsoils_activated = 0  # Counts the number of times `set_soil_type()` has been called.

    def __init__(
        self,
        soildata: MultiSoilDataProvider = None,
        timerdata: dict = None,
        cropdata: MultiCropDataProvider = None,
        override: dict = None,
    ) -> None:
        """Initializes class `ParameterProvider

        Args:
            soildata  - data for soil
            timerdata - data for timer
            cropdata  - data for crop
            override  - parameter overrides (useful for setting not .yaml configurations)
        """
        if soildata is not None:
            self._soildata = soildata
        else:
            self._soildata = {}
        if cropdata is not None:
            self._cropdata = cropdata
        else:
            self._cropdata = {}
        if timerdata is not None:
            self._timerdata = timerdata
        else:
            self._timerdata = {}
        if override is not None:
            self._override = override
        else:
            self._override = {}

        self._maps = [self._override, self._soildata, self._timerdata, self._cropdata]
        self._test_uniqueness()

    def set_active_crop(
        self, crop_name: str = None, crop_variety: str = None, crop_start_type: str = None, crop_end_type: str = None
    ) -> None:
        """Activate the crop parameters for the given crop_name and crop_variety.

        :param crop_name: string identifying the crop name, is ignored as only
               one crop is assumed to be here.
        :param crop_variety: string identifying the variety name, is ignored as only
               one crop is assumed to be here.
        :param crop_start_type: start type for the given crop: 'sowing'|'emergence'
        :param crop_end_type: end type for the given crop: 'maturity'|'harvest'

        Besides the crop parameters, this method also sets the `crop_start_type` and `crop_end_type` of the
        crop which is required for all crops by the phenology module.

        """
        self._timerdata["CROP_START_TYPE"] = crop_start_type
        self._timerdata["CROP_END_TYPE"] = crop_end_type
        if isinstance(self._cropdata, MultiCropDataProvider):
            # we have a MultiCropDataProvider, so set the active crop and variety
            self._cropdata.set_active_crop(crop_name, crop_variety)
        else:
            msg = f"Crop data provider {self._cropdata} is not of type {type(MultiCropDataProvider)}"
            raise exc.PCSEError(msg)

        self._ncrops_activated += 1
        self._test_uniqueness()

    def set_active_soil(self, soil_name: str = None, soil_variation: str = None) -> None:
        """Activate the soil parameters for the given soil_name and soil_variation.

        :param soil_name: string identifying the soil name, is ignored as only
               one soil is assumed to be here.
        :param soil_variation: string identifying the variety name, is ignored as only
               one variation is assumed to be here.
        """
        if isinstance(self._soildata, MultiSoilDataProvider):
            # we have a MultiCropDataProvider, so set the active crop and variety
            self._soildata.set_active_soil(soil_name, soil_variation)
        else:
            msg = f"Soil data provider {self._soildata} is not of type {type(MultiSoilDataProvider)}"
            raise exc.PCSEError(msg)

        self._nsoils_activated += 1
        self._test_uniqueness()

    @property
    def logger(self):
        loggername = "%s.%s" % (self.__class__.__module__, self.__class__.__name__)
        return logging.getLogger(loggername)

    def set_override(self, varname: str, value: object, check: bool = True) -> None:
        """ "Override the value of parameter varname in the parameterprovider.

        Overriding the value of particular parameter is often useful for example
        when running for different sets of parameters or for calibration
        purposes.

        Note that if check=True (default) varname should already exist in one of soil, timer,
        soil or cropdata.
        """

        if check:
            if varname in self:
                self._override[varname] = value
            else:
                msg = "Cannot override '%s', parameter does not already exist." % varname
                raise exc.PCSEError(msg)
        else:
            self._override[varname] = value

    def clear_override(self, varname: str = None) -> None:
        """Removes parameter varname from the set of overridden parameters.

        Without arguments all overridden parameters are removed.
        """

        if varname is None:
            self._override.clear()
        else:
            if varname in self._override:
                self._override.pop(varname)
            else:
                msg = "Cannot clear varname '%s' from override" % varname
                raise exc.PCSEError(msg)

    def _test_uniqueness(self) -> None:
        """Check if parameter names are unique and raise an error if duplicates occur.

        Note that the uniqueness is not tested for parameters in self._override as this
        is specifically meant for overriding parameters.
        """
        parnames = []
        for mapping in [self._soildata, self._timerdata, self._cropdata]:
            parnames.extend(mapping.keys())
        unique = Counter(parnames)
        for parname, count in unique.items():
            if count > 1:
                msg = "Duplicate parameter found: %s" % parname
                raise exc.PCSEError(msg)

    @property
    def _unique_parameters(self) -> list:
        """Returns a list of unique parameter names across all sets of parameters.

        This includes the parameters in self._override in order to be able to
        iterate over all parameters in the ParameterProvider.
        """
        s = []
        for mapping in self._maps:
            s.extend(mapping.keys())
        return sorted(list(set(s)))

    def __getitem__(self, key: str) -> object:
        """Returns the value of the given parameter (key).

        Note that the search order in self._map is such that self._override is tested first for the
        existence of the key. Thus ensuring that overridden parameters will be found first.

        :param key: parameter name to return
        """
        for mapping in self._maps:
            if key in mapping:
                return mapping[key]
        raise KeyError(key)

    def __contains__(self, key: str) -> bool:
        for mapping in self._maps:
            if key in mapping:
                return True
        return False

    def __str__(self) -> str:
        msg = "ParameterProvider providing %i parameters, %i parameters overridden: %s."
        return msg % (len(self), len(self._override), self._override.keys())

    def __setitem__(self, key: str, value: object) -> None:
        """Override an existing parameter (key) by value.

         The parameter that is overridden is added to self._override, note that only *existing*
         parameters may be overridden this way. If it is needed to really add a *new* parameter
         than use: ParameterProvider.set_override(key, value, check=False)

        :param key: The name of the parameter to override
        :param value: the value of the parameter
        """
        if key in self:
            self._override[key] = value
        else:
            msg = (
                "Cannot override parameter '%s', parameter does not exist. "
                "to bypass this check use: set_override(parameter, value, check=False)" % key
            )
            raise exc.PCSEError(msg)

    def __delitem__(self, key: str) -> None:
        """Deletes a parameter from self._override.

        Note that only parameters that exist in self._override can be deleted. This also means that
        if an parameter is overridden its original value will return after a parameter is deleted.

        :param key: The name of the parameter to delete
        """
        if key in self._override:
            self._override.pop(key)
        elif key in self:
            msg = "Cannot delete default parameter: %s" % key
            raise exc.PCSEError(msg)
        else:
            msg = "Parameter not found!"
            raise KeyError(msg)

    def __len__(self) -> int:
        return len(self._unique_parameters)

    def __iter__(self) -> MutableMapping:
        return self

    def next(self) -> object:
        i = self._iter
        if i < len(self):
            self._iter += 1
            return self._unique_parameters[self._iter - 1]
        else:
            self._iter = 0
            raise StopIteration

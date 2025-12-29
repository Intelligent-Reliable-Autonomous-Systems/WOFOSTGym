"""Implementation of AgroManager and related classes for agromanagement actions in PCSE.

Available classes:

  * CropCalendar: A class for handling cropping calendars
  * AgroManager: A class for handling all agromanagement events which encapsulates
    the CropCalendar and Timed/State events.
Written by: Allard de Wit (allard.dewit@wur.nl), April 2014
Modified by Will Solow, 2024
"""

from datetime import date, timedelta
import logging
from collections.abc import Iterable

from pcse.base import DispatcherObject, VariableKiosk, ParameterProvider, AncillaryObject
from pcse.utils.traitlets import HasTraits, Float, Int, Instance, Enum, Bool, Unicode
from pcse.utils import exceptions as exc
from pcse.util import ConfigurationLoader
from pcse.utils import signals
from pcse.nasapower import WeatherDataContainer


def check_date_range(day, start: date, end: date) -> bool:
    """returns True if start <= day < end

    Optionally, end may be None. in that case return True if start <= day

    :param day: the date that will be checked
    :param start: the start date of the range
    :param end: the end date of the range or None
    :return: True/False
    """

    if end is None:
        return start <= day
    else:
        return start <= day < end


def take_first(iterator: Iterable) -> object:
    """Return the first item of the given iterator."""
    for item in iterator:
        return item


class BaseSoilCalendar(HasTraits, DispatcherObject):
    """Placeholder class for the soil calendar. All SoilCalendar objects inherit
    from this class
    """

    # System parameters
    kiosk = Instance(VariableKiosk)
    parameterprovider = Instance(ParameterProvider)
    mconf = Instance(ConfigurationLoader)
    logger = Instance(logging.Logger)

    # Characteristics of the soil cycle
    soil_name = Unicode()
    soil_variation = Unicode()
    soil_start_date = Instance(date)
    soil_end_date = Instance(date)

    # Counter for duration of the soil cycle
    duration = Int(0)
    in_soil_cycle = Bool(False)

    def __init__(
        self,
        kiosk: VariableKiosk,
        soil_name: str = None,
        soil_variation: str = None,
        soil_start_date: date = None,
        soil_end_date: date = None,
    ) -> None:
        """Initialize the SoilCalendar Instance

        Args:
            param: soil_name       - string identifying the soil
            param: soil_variation  - string identifying the soil variation
            param: soil_start_date - date identifying soil start
            param: soil_end_date   - date identifying soil end
        """
        # set up logging
        loggername = "%s.%s" % (self.__class__.__module__, self.__class__.__name__)

        self.logger = logging.getLogger(loggername)
        self.kiosk = kiosk
        self.soil_name = soil_name
        self.soil_variation = soil_variation
        self.soil_start_date = soil_start_date
        self.soil_end_date = soil_end_date

        self._connect_signal(self._on_SOIL_FINISH, signal=signals.soil_finish)

    def reset(self) -> None:
        """
        Reset crop calendar
        """
        self.duration = 0

    def __call__(self, day: date) -> None:
        """Runs the soil calendar to determine if any actions are needed.

        :param day:  a date object for the current simulation day
        :param drv: the driving variables at this day
        :return: None
        """

        if self.in_soil_cycle:
            self.duration += 1

        # Start of the soil cycle
        if day == self.soil_start_date:
            msg = "Starting soil (%s) with variation (%s) on day %s" % (self.soil_name, self.soil_variation, day)
            # print(msg)
            self.logger.info(msg)
            self._send_signal(
                signal=signals.soil_start, day=day, soil_name=self.soil_name, soil_variation=self.soil_variation
            )

        if day == self.soil_end_date:
            self._send_signal(signal=signals.soil_finish, day=day, soil_delete=True)

    def validate(self):
        """Validate the crop calendar internally and against the interval for
        the agricultural campaign.

        :param campaign_start_date: start date of this campaign
        :param next_campaign_start_date: start date of the next campaign
        """

        # Check that crop_start_date is before crop_end_date
        if self.soil_start_date >= self.soil_end_date:
            msg = "soil_end_date before or equal to soil_start_date for crop '%s'!"
            raise exc.PCSEError(msg % (self.soil_start_date, self.soil_end_date))

    def _on_SOIL_FINISH(self) -> None:
        """Register that crop has reached the end of its cycle."""
        self.in_soil_cycle = False


class SoilCalendar(BaseSoilCalendar):
    """A soil calendar for managing the soil cycle.

    A `SoilCalendar` object is responsible for storing, checking, starting and ending
    the soil cycle. The soil calendar is initialized by providing the parameters needed
    for defining the soil cycle. At each time step the instance of `SoilCalendar` is called
    and at dates defined by its parameters it initiates the appropriate actions:

    :return: A SoilCalendar Instance
    """

    def __init__(
        self,
        kiosk: VariableKiosk,
        soil_name: str = None,
        soil_variation: str = None,
        soil_start_date: date = None,
        soil_end_date: date = None,
    ):
        super().__init__(kiosk, soil_name, soil_variation, soil_start_date, soil_end_date)


class PerennialSoilCalendar(BaseSoilCalendar):
    """A soil calendar for managing the soil cycle.

    A `SoilCalendar` object is responsible for storing, checking, starting and ending
    the soil cycle. The soil calendar is initialized by providing the parameters needed
    for defining the soil cycle. At each time step the instance of `SoilCalendar` is called
    and at dates defined by its parameters it initiates the appropriate actions:

    :return: A SoilCalendar Instance
    """

    def __init__(
        self,
        kiosk: VariableKiosk,
        soil_name: str = None,
        soil_variation: str = None,
        soil_start_date: date = None,
        soil_end_date: date = None,
    ) -> None:
        super().__init__(kiosk, soil_name, soil_variation, soil_start_date, soil_end_date)


class BaseCropCalendar(HasTraits, DispatcherObject):
    """Placeholder class for the crop calendar. All CropCalendar objects inherit
    from this class
    """

    # Characteristics of the crop cycle
    crop_name = Unicode()
    crop_variety = Unicode()
    soil_name = Unicode()
    variation = Unicode()
    crop_start_date = Instance(date)
    crop_start_type = Enum(["sowing", "emergence"])
    crop_end_date = Instance(date)
    crop_end_type = Enum(["emergence", "maturity", "harvest", "death", "max_duration"])
    max_duration = Int()

    # system parameters
    kiosk = Instance(VariableKiosk)
    parameterprovider = Instance(ParameterProvider)
    mconf = Instance(ConfigurationLoader)
    logger = Instance(logging.Logger)

    # Counter for duration of the crop cycle
    duration = Int(0)
    in_crop_cycle = Bool(False)

    def __init__(
        self,
        kiosk: VariableKiosk,
        crop_name: str = None,
        crop_variety: str = None,
        crop_start_date: date = None,
        crop_start_type: date = None,
        crop_end_date: date = None,
        crop_end_type: date = None,
        max_duration: int = None,
    ) -> None:
        """Initialize Crop Calendar Class

        Args:
            param kiosk: The PCSE VariableKiosk instance
            param crop_name: String identifying the crop
            param crop_variety: String identifying the variety
            param crop_start_date: Start date of the crop simulation
            param crop_start_type: Start type of the crop simulation ('sowing', 'emergence')
            param crop_end_date: End date of the crop simulation
            param crop_end_type: End type of the crop simulation ('harvest', 'maturity', 'death')
            param max_duration: Integer describing the maximum duration of the crop cycle
        """
        # set up logging
        loggername = "%s.%s" % (self.__class__.__module__, self.__class__.__name__)

        self.logger = logging.getLogger(loggername)
        self.kiosk = kiosk
        self.crop_name = crop_name
        self.crop_variety = crop_variety
        self.crop_start_date = crop_start_date
        self.crop_start_type = crop_start_type
        self.crop_end_date = crop_end_date
        self.crop_end_type = crop_end_type
        self.max_duration = max_duration

        self._connect_signal(self._on_CROP_FINISH, signal=signals.crop_finish)
        self._connect_signal(self._on_CROP_START, signal=signals.crop_start)

    def reset(self) -> None:
        """
        Reset crop calendar
        """
        self.duration = 0

    def validate(self, campaign_start_date: date, next_campaign_start_date: date) -> None:
        """Validate the crop calendar internally and against the interval for
        the agricultural campaign.

        :param campaign_start_date: start date of this campaign
        :param next_campaign_start_date: start date of the next campaign
        """

        # Check that crop_start_date is before crop_end_date
        crop_end_date = self.crop_end_date
        if self.crop_end_type == "maturity":
            crop_end_date = self.crop_start_date + timedelta(days=self.max_duration)
        if self.crop_start_date >= crop_end_date:
            msg = "crop_end_date before or equal to crop_start_date for crop '%s'!"
            raise exc.PCSEError(msg % (self.crop_start_date, self.crop_end_date))

        # check that crop_start_date is within the campaign interval
        r = check_date_range(self.crop_start_date, campaign_start_date, next_campaign_start_date)
        if r is not True:
            msg = "Start date (%s) for crop '%s' vareity '%s' not within campaign window (%s - %s)." % (
                self.crop_start_date,
                self.crop_name,
                self.crop_variety,
                campaign_start_date,
                next_campaign_start_date,
            )
            raise exc.PCSEError(msg)

    def __call__(self, day: date) -> None:
        """Runs the crop calendar to determine if any actions are needed.

        :param day:  a date object for the current simulation day
        :param drv: the driving variables at this day
        :return: None
        """

        if self.in_crop_cycle:
            self.duration += 1

        # Start of the crop cycle
        if day == self.crop_start_date:  # Start a new crop
            msg = "Starting crop (%s) with variety (%s) on day %s" % (self.crop_name, self.crop_variety, day)
            # print(msg)
            self.logger.info(msg)
            self._send_signal(
                signal=signals.crop_start,
                day=day,
                crop_name=self.crop_name,
                crop_variety=self.crop_variety,
                crop_start_type=self.crop_start_type,
                crop_end_type=self.crop_end_type,
            )

        # end of the crop cycle
        finish_type = None
        if self.in_crop_cycle:
            # Check if crop_end_date is reached for CROP_END_TYPE harvest
            if self.crop_end_type in ["harvest"]:
                if day == self.crop_end_date:
                    finish_type = "harvest"

            # Check for forced stop because maximum duration is reached
            if self.in_crop_cycle and self.duration == self.max_duration:
                finish_type = "max_duration"

        # If finish condition is reached send a signal to finish the crop
        if finish_type is not None:
            self.in_crop_cycle = False
            self._send_signal(signal=signals.crop_finish, day=day, finish_type=finish_type, crop_delete=True)

    def _on_CROP_FINISH(self) -> None:
        """Register that crop has reached the end of its cycle."""
        self.in_crop_cycle = False

    def _on_CROP_START(self) -> None:
        """Register that a crop has started"""
        self.in_crop_cycle = True
        self.duration = 0


class CropCalendar(BaseCropCalendar):
    """A crop calendar for managing the crop cycle.

    A `CropCalendar` object is responsible for storing, checking, starting and ending
    the crop cycle. The crop calendar is initialized by providing the parameters needed
    for defining the crop cycle. At each time step the instance of `CropCalendar` is called
    and at dates defined by its parameters it initiates the appropriate actions:

    - sowing/emergence: A `crop_start` signal is dispatched including the parameters needed to
      start the new crop simulation object
    - maturity/harvest: the crop cycle is ended by dispatching a `crop_finish` signal with the
      appropriate parameters.


    :return: A CropCalendar Instance
    """

    def __init__(
        self,
        kiosk: VariableKiosk,
        crop_name: str = None,
        crop_variety: str = None,
        crop_start_date: date = None,
        crop_start_type: date = None,
        crop_end_date: date = None,
        crop_end_type: date = None,
        max_duration: int = None,
    ):
        super().__init__(
            kiosk, crop_name, crop_variety, crop_start_date, crop_start_type, crop_end_date, crop_end_type, max_duration
        )


class CropCalendarHarvest(BaseCropCalendar):

    def __init__(
        self,
        kiosk: VariableKiosk,
        crop_name: str = None,
        crop_variety: str = None,
        crop_start_date: date = None,
        crop_start_type: str = None,
        crop_end_date: date = None,
        crop_end_type: str = None,
        max_duration: int = None,
    ):
        """Initialize Crop Calendar Harvest Class inherits from CropCalendar

        Args:
            param kiosk: The PCSE VariableKiosk instance
            param crop_name: String identifying the crop
            param crop_variety: String identifying the variety
            param crop_start_date: Start date of the crop simulation
            param crop_start_type: Start type of the crop simulation ('sowing', 'emergence')
            param crop_end_date: End date of the crop simulation
            param crop_end_type: End type of the crop simulation ('harvest', 'maturity', 'death')
            param max_duration: Integer describing the maximum duration of the crop cycle
        """
        super().__init__(
            kiosk,
            crop_name=crop_name,
            crop_variety=crop_variety,
            crop_start_date=crop_start_date,
            crop_start_type=crop_start_type,
            crop_end_date=crop_end_date,
            crop_end_type=crop_end_type,
            max_duration=max_duration,
        )

    def __call__(self, day: date) -> None:
        """Runs the crop calendar to determine if any actions are needed.

        :param day:  a date object for the current simulation day
        :param drv: the driving variables at this day
        :return: None
        """

        if self.in_crop_cycle:
            self.duration += 1

        # Start of the crop cycle
        if day == self.crop_start_date:  # Start a new crop
            msg = "Starting crop (%s) with variety (%s) on day %s" % (self.crop_name, self.crop_variety, day)
            # print(msg)
            self.logger.info(msg)
            self._send_signal(
                signal=signals.crop_start,
                day=day,
                crop_name=self.crop_name,
                crop_variety=self.crop_variety,
                crop_start_type=self.crop_start_type,
                crop_end_type=self.crop_end_type,
            )

        # end of the crop cycle
        finish_type = None
        if self.in_crop_cycle:
            # Check for forced stop because maximum duration is reached
            if self.in_crop_cycle and self.duration == self.max_duration:
                finish_type = "max_duration"

        # If finish condition is reached send a signal to finish the crop
        if finish_type is not None:
            self.in_crop_cycle = False
            self._send_signal(signal=signals.crop_finish, day=day, finish_type=finish_type, crop_delete=True)

    def _on_CROP_FINISH(self, day=date) -> None:
        """Register that crop has reached the end of its cycle."""
        self.in_crop_cycle = False

    def _on_CROP_START(self, day=date) -> None:
        """Register that a crop has started"""
        self.in_crop_cycle = True
        self.duration = 0


class CropCalendarPlant(BaseCropCalendar):

    def __init__(
        self,
        kiosk: VariableKiosk,
        crop_name: str = None,
        crop_variety: str = None,
        crop_start_date: date = None,
        crop_start_type: str = None,
        crop_end_date: date = None,
        crop_end_type: str = None,
        max_duration: int = None,
    ):
        """Initialize Crop Calendar Harvest Class inherits from CropCalendar

        Args:
            param kiosk: The PCSE VariableKiosk instance
            param crop_name: String identifying the crop
            param crop_variety: String identifying the variety
            param crop_start_date: Start date of the crop simulation
            param crop_start_type: Start type of the crop simulation ('sowing', 'emergence')
            param crop_end_date: End date of the crop simulation
            param crop_end_type: End type of the crop simulation ('harvest', 'maturity', 'death')
            param max_duration: Integer describing the maximum duration of the crop cycle
        """
        super().__init__(
            kiosk,
            crop_name=crop_name,
            crop_variety=crop_variety,
            crop_start_date=crop_start_date,
            crop_start_type=crop_start_type,
            crop_end_date=crop_end_date,
            crop_end_type=crop_end_type,
            max_duration=max_duration,
        )

    def __call__(self, day: date) -> None:
        """Runs the crop calendar to determine if any actions are needed.

        :param day:  a date object for the current simulation day
        :param drv: the driving variables at this day
        :return: None
        """

        if self.in_crop_cycle:
            self.duration += 1

        # end of the crop cycle
        finish_type = None
        if self.in_crop_cycle:
            # Check for forced stop because maximum duration is reached
            if self.in_crop_cycle and self.duration == self.max_duration:
                finish_type = "max_duration"

        # If finish condition is reached send a signal to finish the crop
        if finish_type is not None:
            self.in_crop_cycle = False
            self._send_signal(signal=signals.crop_finish, day=day, finish_type=finish_type, crop_delete=True)


class PerennialCropCalendar(BaseCropCalendar):
    """A crop calendar for managing the crop cycle.

    A `CropCalendar` object is responsible for storing, checking, starting and ending
    the crop cycle. The crop calendar is initialized by providing the parameters needed
    for defining the crop cycle. At each time step the instance of `CropCalendar` is called
    and at dates defined by its parameters it initiates the appropriate actions:

    - sowing/emergence: A `crop_start` signal is dispatched including the parameters needed to
      start the new crop simulation object
    - maturity/harvest: the crop cycle is ended by dispatching a `crop_finish` signal with the
      appropriate parameters.


    :return: A CropCalendar Instance
    """

    crop_start_type = Enum(["sowing", "emergence", "dormant", "endodorm", "ecodorm"])

    def __init__(
        self,
        kiosk: VariableKiosk,
        crop_name: str = None,
        crop_variety: str = None,
        crop_start_date: date = None,
        crop_start_type: date = None,
        crop_end_date: date = None,
        crop_end_type: date = None,
        max_duration: int = None,
    ) -> None:
        super().__init__(
            kiosk, crop_name, crop_variety, crop_start_date, crop_start_type, crop_end_date, crop_end_type, max_duration
        )


class BaseAgroManager(AncillaryObject):
    """Base class for Agromangement
    Defines shared parameters
    """

    # Overall engine start date and end date
    _soil_calendar = Instance(BaseSoilCalendar)
    _crop_calendar = Instance(BaseCropCalendar)

    start_date = Instance(date)
    end_date = Instance(date)

    def initialize(self, day: date, kiosk: VariableKiosk, parvalues: dict) -> None:
        """Initilize method
        Args:
            day   - current date
            kiosk - VariableKiosk Object storing global parameters"""
        msg = "`initialize` method not yet implemented on %s" % self.__class__.__name__
        raise NotImplementedError(msg)

    def reset(self) -> None:
        """
        Reset agromanager
        """
        self._soil_calendar.reset()
        self._crop_calendar.reset()

    def __call__(self, day: date, drv: WeatherDataContainer) -> None:
        """Calls the AgroManager to execute and crop calendar actions, timed or state events.

        :param day: The current simulation date
        :param drv: The driving variables for the current day
        :return: None
        """
        if self._soil_calendar is not None:
            self._soil_calendar(day)

        # call handlers for the crop calendar, timed and state events
        if self._crop_calendar is not None:
            self._crop_calendar(day)

    def _on_SOIL_FINISH(self, day: date) -> None:
        """Send signal to terminate after the crop cycle finishes.

        The simulation will be terminated when the following conditions are met:
        1. There are no campaigns defined after the current campaign
        2. There are no StateEvents active
        3. There are no TimedEvents scheduled after the current date.
        """
        self._send_signal(signal=signals.terminate)


class AgroManagerAnnual(BaseAgroManager):
    """Class for continuous AgroManagement actions including crop rotations and events.

    The AgroManager takes care of executing agromanagent actions that typically occur on agricultural
    fields including planting and harvesting of the crop, as well as management actions such as fertilizer
    application, irrigation and spraying.

    The agromanagement during the simulation is implemented as a sequence of campaigns. Campaigns start on a
    prescribed calendar date and finalize when the next campaign starts. The simulation ends either explicitly by
    provided a trailing empty campaign or by deriving the end date from the crop calendar and timed events in the
    last campaign. See also the section below on `end_date` property.

    Each campaign is characterized by zero or one crop calendar, zero or more timed events and zero or more
    state events.
    """

    def initialize(self, kiosk: VariableKiosk, agromanagement: dict) -> None:
        """Initialize the AgroManager.

        :param kiosk: A PCSE variable Kiosk
        :param agromanagement: the agromanagement definition, see the example above in YAML.
        """
        self.kiosk = kiosk

        # Connect CROP_FINISH signal with handler
        self._connect_signal(self._on_SOIL_FINISH, signals.soil_finish)

        # If there is an "AgroManagement" item defined then we first need to get
        # the contents defined within that item
        if "AgroManagement" in agromanagement:
            agromanagement = agromanagement["AgroManagement"]

        # Validate that a soil calendar and crop calendar are present
        sc_def = agromanagement["SoilCalendar"]
        if sc_def is not None:
            sc = SoilCalendar(kiosk, **sc_def)
            sc.validate()
            self._soil_calendar = sc

            self.start_date = self._soil_calendar.soil_start_date
            self.end_date = self._soil_calendar.soil_end_date

        # Get and validate the crop calendar
        cc_def = agromanagement["CropCalendar"]
        if cc_def is not None and sc_def is not None:
            cc = CropCalendar(kiosk, **cc_def)
            cc.validate(self._soil_calendar.soil_start_date, self._soil_calendar.soil_end_date)
            self._crop_calendar = cc


class AgroManagerPlant(BaseAgroManager):
    """Class for continuous AgroManagement actions including crop rotations and events.
    The Harvesting Agromanagement class differs slightly in that it does not specify
    crop planting and ending dates, instead requires signals to be sent from the
    engine to start the CropCalendar

    The AgroManager takes care of executing agromanagent actions that typically occur on agricultural
    fields including planting and harvesting of the crop, as well as management actions such as fertilizer
    application, irrigation and spraying.

    The agromanagement during the simulation is implemented as a sequence of campaigns. Campaigns start on a
    prescribed calendar date and finalize when the next campaign starts. The simulation ends either explicitly by
    provided a trailing empty campaign or by deriving the end date from the crop calendar and timed events in the
    last campaign. See also the section below on `end_date` property.

    Each campaign is characterized by zero or one crop calendar, zero or more timed events and zero or more
    state events.
    """

    def initialize(self, kiosk: VariableKiosk, agromanagement: dict) -> None:
        """Initialize the AgroManagerHarvest.

        :param kiosk: A PCSE variable Kiosk
        :param agromanagement: the agromanagement definition, see the example above in YAML.
        """
        self.kiosk = kiosk

        # Connect CROP_FINISH signal with handler
        self._connect_signal(self._on_SOIL_FINISH, signals.soil_finish)

        # If there is an "AgroManagement" item defined then we first need to get
        # the contents defined within that item
        if "AgroManagement" in agromanagement:
            agromanagement = agromanagement["AgroManagement"]

        # Validate that a soil calendar and crop calendar are present
        sc_def = agromanagement["SoilCalendar"]
        if sc_def is not None:
            sc = SoilCalendar(kiosk, **sc_def)
            sc.validate()
            self._soil_calendar = sc

            self.start_date = self._soil_calendar.soil_start_date
            self.end_date = self._soil_calendar.soil_end_date

        # Get and validate the crop calendar
        cc_def = agromanagement["CropCalendar"]
        if cc_def is not None and sc_def is not None:
            cc = CropCalendarPlant(kiosk, **cc_def)
            cc.validate(self._soil_calendar.soil_start_date, self._soil_calendar.soil_end_date)
            self._crop_calendar = cc


class AgroManagerHarvest(BaseAgroManager):
    """Class for continuous AgroManagement actions including crop rotations and events.

    The AgroManager takes care of executing agromanagent actions that typically occur on agricultural
    fields including planting and harvesting of the crop, as well as management actions such as fertilizer
    application, irrigation and spraying.

    The agromanagement during the simulation is implemented as a sequence of campaigns. Campaigns start on a
    prescribed calendar date and finalize when the next campaign starts. The simulation ends either explicitly by
    provided a trailing empty campaign or by deriving the end date from the crop calendar and timed events in the
    last campaign. See also the section below on `end_date` property.

    Each campaign is characterized by zero or one crop calendar, zero or more timed events and zero or more
    state events.
    """

    def initialize(self, kiosk: VariableKiosk, agromanagement: dict) -> None:
        """Initialize the AgroManager.

        :param kiosk: A PCSE variable Kiosk
        :param agromanagement: the agromanagement definition, see the example above in YAML.
        """
        self.kiosk = kiosk

        # Connect CROP_FINISH signal with handler
        self._connect_signal(self._on_SOIL_FINISH, signals.soil_finish)

        # If there is an "AgroManagement" item defined then we first need to get
        # the contents defined within that item
        if "AgroManagement" in agromanagement:
            agromanagement = agromanagement["AgroManagement"]

        # Validate that a soil calendar and crop calendar are present
        sc_def = agromanagement["SoilCalendar"]
        if sc_def is not None:
            sc = SoilCalendar(kiosk, **sc_def)
            sc.validate()
            self._soil_calendar = sc

            self.start_date = self._soil_calendar.soil_start_date
            self.end_date = self._soil_calendar.soil_end_date

        # Get and validate the crop calendar
        cc_def = agromanagement["CropCalendar"]
        if cc_def is not None and sc_def is not None:
            cc = CropCalendarHarvest(kiosk, **cc_def)
            cc.validate(self._soil_calendar.soil_start_date, self._soil_calendar.soil_end_date)
            self._crop_calendar = cc


class AgroManagerPerennial(BaseAgroManager):
    """Class for continuous AgroManagement actions including crop rotations and events.

    The AgroManager takes care of executing agromanagent actions that typically occur on agricultural
    fields including planting and harvesting of the crop, as well as management actions such as fertilizer
    application, irrigation and spraying.

    The agromanagement during the simulation is implemented as a sequence of campaigns. Campaigns start on a
    prescribed calendar date and finalize when the next campaign starts. The simulation ends either explicitly by
    provided a trailing empty campaign or by deriving the end date from the crop calendar and timed events in the
    last campaign. See also the section below on `end_date` property.

    Each campaign is characterized by zero or one crop calendar, zero or more timed events and zero or more
    state events.
    """

    def initialize(self, kiosk: VariableKiosk, agromanagement: dict) -> None:
        """Initialize the AgroManager.

        :param kiosk: A PCSE variable Kiosk
        :param agromanagement: the agromanagement definition, see the example above in YAML.
        """
        self.kiosk = kiosk

        # Connect CROP_FINISH signal with handler
        self._connect_signal(self._on_SOIL_FINISH, signals.soil_finish)

        # If there is an "AgroManagement" item defined then we first need to get
        # the contents defined within that item
        if "AgroManagement" in agromanagement:
            agromanagement = agromanagement["AgroManagement"]

        # Validate that a soil calendar and crop calendar are present
        sc_def = agromanagement["SoilCalendar"]
        if sc_def is not None:
            sc = PerennialSoilCalendar(kiosk, **sc_def)
            sc.validate()
            self._soil_calendar = sc

            self.start_date = self._soil_calendar.soil_start_date
            self.end_date = self._soil_calendar.soil_end_date

        # Get and validate the crop calendar
        cc_def = agromanagement["CropCalendar"]
        if cc_def is not None and sc_def is not None:
            cc = PerennialCropCalendar(kiosk, **cc_def)
            cc.validate(self._soil_calendar.soil_start_date, self._soil_calendar.soil_end_date)
            self._crop_calendar = cc

    def __call__(self, day: date, drv: WeatherDataContainer) -> None:
        """Calls the AgroManager to execute and crop calendar actions, timed or state events.

        :param day: The current simulation date
        :param drv: The driving variables for the current day
        :return: None
        """
        if self._soil_calendar is not None:
            self._soil_calendar(day)

        # call handlers for the crop calendar, timed and state events
        if self._crop_calendar is not None:
            self._crop_calendar(day)

    def _on_SOIL_FINISH(self, day: date) -> None:
        """Send signal to terminate after the crop cycle finishes.

        The simulation will be terminated when the following conditions are met:
        1. There are no campaigns defined after the current campaign
        2. There are no StateEvents active
        3. There are no TimedEvents scheduled after the current date.
        """
        self._send_signal(signal=signals.terminate)


class AgroManagerPlantPerennial(BaseAgroManager):
    """Class for continuous AgroManagement actions including crop rotations and events.
    The Harvesting Agromanagement class differs slightly in that it does not specify
    crop planting and ending dates, instead requires signals to be sent from the
    engine to start the CropCalendar

    The AgroManager takes care of executing agromanagent actions that typically occur on agricultural
    fields including planting and harvesting of the crop, as well as management actions such as fertilizer
    application, irrigation and spraying.

    The agromanagement during the simulation is implemented as a sequence of campaigns. Campaigns start on a
    prescribed calendar date and finalize when the next campaign starts. The simulation ends either explicitly by
    provided a trailing empty campaign or by deriving the end date from the crop calendar and timed events in the
    last campaign. See also the section below on `end_date` property.

    Each campaign is characterized by zero or one crop calendar, zero or more timed events and zero or more
    state events.
    """

    def initialize(self, kiosk: VariableKiosk, agromanagement: dict) -> None:
        """Initialize the AgroManagerHarvest.

        :param kiosk: A PCSE variable Kiosk
        :param agromanagement: the agromanagement definition, see the example above in YAML.
        """
        self.kiosk = kiosk

        # Connect CROP_FINISH signal with handler
        self._connect_signal(self._on_SOIL_FINISH, signals.soil_finish)

        # If there is an "AgroManagement" item defined then we first need to get
        # the contents defined within that item
        if "AgroManagement" in agromanagement:
            agromanagement = agromanagement["AgroManagement"]

        # Validate that a soil calendar and crop calendar are present
        sc_def = agromanagement["SoilCalendar"]
        if sc_def is not None:
            sc = SoilCalendar(kiosk, **sc_def)
            sc.validate()
            self._soil_calendar = sc

            self.start_date = self._soil_calendar.soil_start_date
            self.end_date = self._soil_calendar.soil_end_date

        # Get and validate the crop calendar
        cc_def = agromanagement["CropCalendar"]
        if cc_def is not None and sc_def is not None:
            cc = CropCalendarPlant(kiosk, **cc_def)
            cc.validate(self._soil_calendar.soil_start_date, self._soil_calendar.soil_end_date)
            self._crop_calendar = cc


class AgroManagerHarvestPerennial(BaseAgroManager):
    """Class for continuous AgroManagement actions including crop rotations and events.

    The AgroManager takes care of executing agromanagent actions that typically occur on agricultural
    fields including planting and harvesting of the crop, as well as management actions such as fertilizer
    application, irrigation and spraying.

    The agromanagement during the simulation is implemented as a sequence of campaigns. Campaigns start on a
    prescribed calendar date and finalize when the next campaign starts. The simulation ends either explicitly by
    provided a trailing empty campaign or by deriving the end date from the crop calendar and timed events in the
    last campaign. See also the section below on `end_date` property.

    Each campaign is characterized by zero or one crop calendar, zero or more timed events and zero or more
    state events.
    """

    def initialize(self, kiosk: VariableKiosk, agromanagement: dict) -> None:
        """Initialize the AgroManager.

        :param kiosk: A PCSE variable Kiosk
        :param agromanagement: the agromanagement definition, see the example above in YAML.
        """
        self.kiosk = kiosk

        # Connect CROP_FINISH signal with handler
        self._connect_signal(self._on_SOIL_FINISH, signals.soil_finish)

        # If there is an "AgroManagement" item defined then we first need to get
        # the contents defined within that item
        if "AgroManagement" in agromanagement:
            agromanagement = agromanagement["AgroManagement"]

        # Validate that a soil calendar and crop calendar are present
        sc_def = agromanagement["SoilCalendar"]
        if sc_def is not None:
            sc = SoilCalendar(kiosk, **sc_def)
            sc.validate()
            self._soil_calendar = sc

            self.start_date = self._soil_calendar.soil_start_date
            self.end_date = self._soil_calendar.soil_end_date

        # Get and validate the crop calendar
        cc_def = agromanagement["CropCalendar"]
        if cc_def is not None and sc_def is not None:
            cc = CropCalendarHarvest(kiosk, **cc_def)
            cc.validate(self._soil_calendar.soil_start_date, self._soil_calendar.soil_end_date)
            self._crop_calendar = cc

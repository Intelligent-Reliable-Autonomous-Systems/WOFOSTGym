"""Base class for for Timer object to keep track of important dates throughout
the course of the WOFOST model

Written by: Allard de Wit (allard.dewit@wur.nl), April 2014
Modified by Will Solow, 2024
"""
from __future__ import print_function
from datetime import date, timedelta

from ..base import AncillaryObject, VariableKiosk
from ..utils.traitlets import Instance, Bool, Int, Enum
from ..utils import signals

class Timer(AncillaryObject):
    """This class implements a basic timer for use with the WOFOST crop model.
    
    This object implements a simple timer that increments the current time with
    a fixed time-step of one day at each call and returns its value. Moreover,
    it generates OUTPUT signals in daily, dekadal or monthly time-steps that
    can be caught in order to store the state of the simulation for later use.
        
    Initializing the timer::

        timer = Timer(start_date, kiosk, final_date, mconf)
        CurrentDate = timer()
        
    **Signals sent or handled:**
 
        * "OUTPUT": sent when the condition for generating output is True
          which depends on the output type and interval.
  """

    start_date = Instance(date)
    end_date = Instance(date)
    current_date = Instance(date)
    time_step = Instance(timedelta)
    interval_type = Enum(["daily", "weekly", "dekadal", "monthly"])
    output_weekday = Int()
    interval_days = Int()
    generate_output = Bool(False)
    day_counter = Int(0)
    first_call = Bool(True)
    _in_crop_cycle = Bool()

    def initialize(self, kiosk: VariableKiosk, start_date: date, end_date: date, mconf):
        """
        :param day: Start date of the simulation
        :param kiosk: Variable kiosk of the PCSE instance
        :param end_date: Final date of the simulation. For example, this date
            represents (START_DATE + MAX_DURATION) for a single cropping season.
            This date is *not* the harvest date because signalling harvest is taken
            care of by the `AgroManagement` module.
        :param mconf: A ConfigurationLoader object, the timer needs access to the
            configuration attributes mconf.OUTPUT_INTERVAL, mconf.OUTPUT_VARS and
            mconf.OUTPUT_INTERVAL_DAYS

        """
        self.kiosk = kiosk
        self.start_date = start_date
        self.end_date = end_date
        self.current_date = start_date
        # Settings for generating output. Note that if no OUTPUT_VARS are listed
        # in that case no OUTPUT signals will be generated.
        self.generate_output = bool(mconf.OUTPUT_VARS)
        self.interval_type = mconf.OUTPUT_INTERVAL.lower()
        self.output_weekday = mconf.OUTPUT_WEEKDAY
        self.interval_days = mconf.OUTPUT_INTERVAL_DAYS
        self.time_step = timedelta(days=1)
    
    def reset(self):
        """
        Reset the timer
        """
        self.current_data = self.start_date

    def __call__(self):
        """Calls the Timer class. Handles signals for termination or output"""
        # On first call only return the current date, do not increase time
        if self.first_call is True:
            self.first_call = False
            self.logger.debug("Model time at first call: %s" % self.current_date)
        else:
            self.current_date += self.time_step
            self.day_counter += 1
            self.logger.debug("Model time updated to: %s" % self.current_date)

        # Check if output should be generated
        output = False
        if self.generate_output:
            if self.interval_type == "daily":
                if (self.day_counter % self.interval_days) == 0:
                    output = True
            elif self.interval_type == "weekly":
                if Timer.is_a_week(self.current_date, self.output_weekday):
                    output = True 
            elif self.interval_type == "dekadal":
                if Timer.is_a_dekad(self.current_date):
                    output = True
            elif self.interval_type == "monthly":
                if Timer.is_a_month(self.current_date):
                    output = True

        # Send output signal if True
        if output:
            self._send_signal(signal=signals.output)
            
        # If end date is reached send the terminate signal
        if self.current_date >= self.end_date:
            msg = "Reached end of simulation period as specified by END_DATE."
            self.logger.info(msg)
            self._send_signal(signal=signals.terminate)
            
        return self.current_date, float(self.time_step.days)
    
    @staticmethod
    def is_a_month(day):
        """Returns True if the date is on the last day of a month."""

        if day.month==12:
            if day == date(day.year, day.month, 31):
                return True
        else:
            if (day == date(day.year, day.month+1, 1) -
                    timedelta(days=1)):
                return True
        return False

    @staticmethod
    def is_a_week(day, weekday=0):
        """Default weekday is Monday. Monday is 0 and Sunday is 6"""
        if day.weekday() == weekday:
            return True
        else:
            return False

    @staticmethod
    def is_a_dekad(day):
        """Returns True if the date is on a dekad boundary, i.e. the 10th,
        the 20th or the last day of each month"""

        if day.month == 12:
            if day == date(day.year, day.month, 10):
                return True
            elif day == date(day.year, day.month, 20):
                return True
            elif day == date(day.year, day.month, 31):
                return True
        else:
            if day == date(day.year, day.month, 10):
                return True
            elif day == date(day.year, day.month, 20):
                return True
            elif (day == date(day.year, day.month+1, 1) -
                        timedelta(days=1)):
                return True
        return False




"""Handles all exceptions in the WOFOST Gym Package"""

class WOFOSTGymError(Exception):
    """Top Level WOFOST Gym Exception"""

class PolicyException(WOFOSTGymError):
    """Raised when there is an issue with the policy"""

class ActionException(WOFOSTGymError):
    """Raised when there is an issue with the inputted action"""

class ConfigFileException(WOFOSTGymError):
    """Raised when there is an issue with a configuration file"""

class ResetException(WOFOSTGymError):
    """Raised when there is an issue with the reset function by misspecification"""

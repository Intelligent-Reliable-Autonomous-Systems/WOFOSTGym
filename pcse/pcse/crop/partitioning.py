# -*- coding: utf-8 -*-
# Copyright (c) 2004-2014 Alterra, Wageningen-UR
# Allard de Wit (allard.dewit@wur.nl), April 2014
from collections import namedtuple
from math import exp
from datetime import date

from ..utils.traitlets import Float, Instance, Bool
from ..utils.decorators import prepare_states
from ..base import ParamTemplate, StatesTemplate, SimulationObject, VariableKiosk
from ..utils import exceptions as exc
from ..util import AfgenTrait, MultiAfgenTrait, limit
from ..nasapower import WeatherDataProvider


class PartioningFactors(namedtuple("partitioning_factors", "FR FL FS FO")):
    """Template for namedtuple containing partitioning factors"""
    pass

class Base_Partitioning_NPK(SimulationObject):
    """Class for assimilate partitioning based on development stage (`DVS`)
    with influence of NPK stress.

    `DVS_Partitioning_NPK` calculates the partitioning of the assimilates to roots,
    stems, leaves and storage organs using fixed partitioning tables as a
    function of crop development stage. The only different with the normal
    partitioning class is the effect of nitrogen stress on partitioning to
    leaves (parameter NPART). The available assimilates are first
    split into below-ground and aboveground using the values in FRTB. In a
    second stage they are split into leaves (`FLTB`), stems (`FSTB`) and storage
    organs (`FOTB`).

    Since the partitioning fractions are derived from the state variable `DVS`
    they are regarded state variables as well.

    **Simulation parameters** (To be provided in cropdata dictionary):

    =======  ============================================= =======  ============
     Name     Description                                   Type     Unit
    =======  ============================================= =======  ============
    FRTB     Partitioning to roots as a function of          TCr       -
             development stage.
    FSTB     Partitioning to stems as a function of          TCr       -
             development stage.
    FLTB     Partitioning to leaves as a function of         TCr       -
             development stage.
    FOTB     Partitioning to starge organs as a function     TCr       -
             of development stage.
    NPART    Coefficient for the effect of N stress on       SCR       -
             leaf biomass allocation
    NTHRESH  Threshold above which surface nitrogen          TCr       |kg ha-1|
             induces stress
    PTHRESH  Threshold above which surface phosphorous       TCr       |kg ha-1|
             induces stress
    KTHRESH  Threshold above which surface potassium         TCr       |kg ha-1|
             induces stress
    =======  ============================================= =======  ============


    **State variables**

    =======  ================================================= ==== ============
     Name     Description                                      Pbl      Unit
    =======  ================================================= ==== ============
    FR        Fraction partitioned to roots.                     Y    -
    FS        Fraction partitioned to stems.                     Y    -
    FL        Fraction partitioned to leaves.                    Y    -
    FO        Fraction partitioned to storage orgains            Y    -
    =======  ================================================= ==== ============

    **Rate variables**

    None

    **Signals send or handled**

    None

    **External dependencies:**

    =======  =================================== =================  ============
     Name     Description                         Provided by         Unit
    =======  =================================== =================  ============
    DVS      Crop development stage              DVS_Phenology       -
    TRA      Actual transpiration                Simple_Evapotranspiration mm d-1
    TRAMX    Maximum transpiration               Simple_Evapotranspiration mm d-1
    NNI      Nitrogen nutrition index            npk_dynamics        -
    =======  =================================== =================  ============

    *Exceptions raised*

    A PartitioningError is raised if the partitioning coefficients to leaves,
    stems and storage organs on a given day do not add up to '1'.
    """

    _THRESHOLD_N_FLAG = Bool(False)
    _THRESHOLD_N      = Float(0.)

    class Parameters(ParamTemplate):
        FRTB = AfgenTrait()
        FLTB = AfgenTrait()
        FSTB = AfgenTrait()
        FOTB = AfgenTrait()
        NPART = Float(-99.)  # coefficient for the effect of N stress on leaf allocation
        NTHRESH = Float(-99.) # Threshold above which excess N stress occurs
        PTHRESH = Float(-99.) # Threshold above which excess P stress occurs
        KTHRESH = Float(-99.) # Threshold above which excess K stress occurs

    class StateVariables(StatesTemplate):
        FR = Float(-99.)
        FL = Float(-99.)
        FS = Float(-99.)
        FO = Float(-99.)
        PF = Instance(PartioningFactors)

    def initialize(self, day:date, kiosk:VariableKiosk, parameters:dict):
        """
        :param day: start date of the simulation
        :param kiosk: variable kiosk of this PCSE instance
        :param parameters: dictionary with WOFOST cropdata key/value pairs
        """
        msg = "Initialize Partitioning in subclass"
        raise NotImplementedError(msg)

    def _check_partitioning(self):
        """Check for partitioning errors.
        """
        FR = self.states.FR
        FL = self.states.FL
        FS = self.states.FS
        FO = self.states.FO
        checksum = FR+(FL+FS+FO)*(1.-FR) - 1.
        if abs(checksum) >= 0.0001:
            msg = ("Error in partitioning!\n")
            msg += ("Checksum: %f, FR: %5.3f, FL: %5.3f, FS: %5.3f, FO: %5.3f\n" \
                    % (checksum, FR, FL, FS, FO))
            #self.logger.error(msg)
            #raise exc.PartitioningError(msg)

    @prepare_states
    def integrate(self, day:date, delt:float=1.0):
        """
        Update partitioning factors based on development stage (DVS)
        and the Nitrogen nutrition Index (NNI)
        """
        p = self.params
        s = self.states
        k = self.kiosk

        if k.RFTRA < k.NNI:
            # Water stress is more severe than nitrogen stress and the
            # partitioning follows the original LINTUL2 assumptions
            # Note: we use specifically nitrogen stress not nutrient stress!!!
            FRTMOD = max(1., 1./(k.RFTRA + 0.5))
            s.FR = min(0.6, p.FRTB(k.DVS) * FRTMOD)
            s.FL = p.FLTB(k.DVS)
            s.FS = p.FSTB(k.DVS)
            s.FO = p.FOTB(k.DVS)
        else:
            # Nitrogen stress is more severe than water stress resulting in
            # less partitioning to leaves and more to stems
            FLVMOD = exp(-p.NPART * (1.0 - k.NNI))
            s.FL = p.FLTB(k.DVS) * FLVMOD
            s.FS = p.FSTB(k.DVS) + p.FLTB(k.DVS) - s.FL
            s.FR = p.FRTB(k.DVS)
            s.FO = p.FOTB(k.DVS)
            
        if self._THRESHOLD_N_FLAG:
            # Excess nitrogen resulting in less partioning to storage organs
            # and more to leaves
            FLVMOD = 1 / exp(-p.NPART * (1.0 - (self._THRESHOLD_N / p.NTHRESH)))
            s.FO = p.FOTB(k.DVS) * FLVMOD
            s.FL = p.FLTB(k.DVS) + p.FOTB(k.DVS) - s.FO
            s.FS = p.FSTB(k.DVS)
            s.FR = p.FRTB(k.DVS)

        # Pack partitioning factors into tuple
        s.PF = PartioningFactors(s.FR, s.FL, s.FS, s.FO)

        self._check_partitioning()

    def calc_rates(self, day:date, drv:WeatherDataProvider):
        """ Return partitioning factors based on current DVS.
        """
        # Set the threshold flag
        if self.kiosk.SURFACE_N > self.params.NTHRESH:
            self._THRESHOLD_N_FLAG = True
            self._THRESHOLD_N = self.kiosk.SURFACE_N
        else:
            self._THRESHOLD_N_FLAG = False
            self._THRESHOLD_N = 0

        # rate calculation does nothing for partitioning as it is a derived state
        return self.states.PF

    def reset(self):
        """Reset states adn rates
        """

        # initial partioning factors (pf)
        k = self.kiosk
        s = self.states
        FR = self.params.FRTB(k.DVS)
        FL = self.params.FLTB(k.DVS)
        FS = self.params.FSTB(k.DVS)
        FO = self.params.FOTB(k.DVS)

        # Pack partitioning factors into tuple
        PF = PartioningFactors(FR, FL, FS, FO)

        s.FR=FR
        s.FL=FL
        s.FS=FS
        s.FO=FO
        s.PF=PF
    
class Annual_Partitioning_NPK(Base_Partitioning_NPK):
    """Class for assimilate partitioning based on development stage (`DVS`)
    with influence of NPK stress. For annual crops

    """

    def initialize(self, day:date, kiosk:VariableKiosk, parameters:dict):
        """
        :param day: start date of the simulation
        :param kiosk: variable kiosk of this PCSE instance
        :param parameters: dictionary with WOFOST cropdata key/value pairs
        """
        self.params = self.Parameters(parameters)

        # initial partioning factors (pf)
        k = self.kiosk
        FR = self.params.FRTB(k.DVS)
        FL = self.params.FLTB(k.DVS)
        FS = self.params.FSTB(k.DVS)
        FO = self.params.FOTB(k.DVS)

        # Pack partitioning factors into tuple
        PF = PartioningFactors(FR, FL, FS, FO)

        # Initial states
        self.states = self.StateVariables(kiosk, publish=["FR", "FL", "FS", "FO", "PF"],
                                          FR=FR, FL=FL, FS=FS, FO=FO, PF=PF)
        self._check_partitioning()

class Perennial_Partitioning_NPK(Base_Partitioning_NPK):
    """Class for assimilate partitioning based on development stage (`DVS`)
    with influence of NPK stress. For perennial crops

    """

    class Parameters(ParamTemplate):
        FRTB = MultiAfgenTrait()
        FLTB = MultiAfgenTrait()
        FSTB = MultiAfgenTrait()
        FOTB = MultiAfgenTrait()
        NPART = Float(-99.)  # coefficient for the effect of N stress on leaf allocation
        NTHRESH = Float(-99.) # Threshold above which excess N stress occurs
        PTHRESH = Float(-99.) # Threshold above which excess P stress occurs
        KTHRESH = Float(-99.) # Threshold above which excess K stress occurs

    def initialize(self, day:date, kiosk:VariableKiosk, parameters:dict):
        """
        :param day: start date of the simulation
        :param kiosk: variable kiosk of this PCSE instance
        :param parameters: dictionary with WOFOST cropdata key/value pairs
        """
        self.params = self.Parameters(parameters)

        # initial partioning factors (pf)
        k = self.kiosk
        FR = self.params.FRTB(k.AGE, k.DVS)
        FL = self.params.FLTB(k.AGE, k.DVS)
        FS = self.params.FSTB(k.AGE, k.DVS)
        FO = self.params.FOTB(k.AGE, k.DVS)

        # Pack partitioning factors into tuple
        PF = PartioningFactors(FR, FL, FS, FO)

        # Initial states
        self.states = self.StateVariables(kiosk, publish=["FR", "FL", "FS", "FO", "PF"],
                                          FR=FR, FL=FL, FS=FS, FO=FO, PF=PF)
        self._check_partitioning()

    @prepare_states
    def integrate(self, day:date, delt:float=1.0):
        """
        Update partitioning factors based on development stage (DVS)
        and the Nitrogen nutrition Index (NNI)
        """
        p = self.params
        s = self.states
        k = self.kiosk

        if k.RFTRA < k.NNI:
            # Water stress is more severe than nitrogen stress and the
            # partitioning follows the original LINTUL2 assumptions
            # Note: we use specifically nitrogen stress not nutrient stress!!!
            FRTMOD = max(1., 1./(k.RFTRA + 0.5))
            s.FR = min(0.6, p.FRTB(k.AGE, k.DVS) * FRTMOD)
            s.FL = p.FLTB(k.AGE, k.DVS)
            s.FS = p.FSTB(k.AGE, k.DVS)
            s.FO = p.FOTB(k.AGE, k.DVS)
        else:
            # Nitrogen stress is more severe than water stress resulting in
            # less partitioning to leaves and more to stems
            FLVMOD = exp(-p.NPART * (1.0 - k.NNI))
            s.FL = p.FLTB(k.AGE, k.DVS) * FLVMOD
            s.FS = p.FSTB(k.AGE, k.DVS) + p.FLTB(k.AGE, k.DVS) - s.FL
            s.FR = p.FRTB(k.AGE, k.DVS)
            s.FO = p.FOTB(k.AGE, k.DVS)

        if self._THRESHOLD_N_FLAG:
            # Excess nitrogen resulting in less partioning to storage organs
            # and more to leaves
            FLVMOD = 1 / exp(-p.NPART * (1.0 - limit(1, 10, self._THRESHOLD_N / p.NTHRESH)))
            s.FO = p.FOTB(k.AGE, k.DVS) * FLVMOD
            s.FL = p.FLTB(k.AGE, k.DVS) + p.FOTB(k.AGE, k.DVS) - s.FO
            s.FS = p.FSTB(k.AGE, k.DVS)
            s.FR = p.FRTB(k.AGE, k.DVS)

        # Pack partitioning factors into tuple
        s.PF = PartioningFactors(s.FR, s.FL, s.FS, s.FO)

        self._check_partitioning()

    def reset(self):
        """Reset states adn rates
        """

        # initial partioning factors (pf)
        k = self.kiosk
        s = self.states
        FR = self.params.FRTB(k.AGE, k.DVS)
        FL = self.params.FLTB(k.AGE, k.DVS)
        FS = self.params.FSTB(k.AGE, k.DVS)
        FO = self.params.FOTB(k.AGE, k.DVS)

        # Pack partitioning factors into tuple
        PF = PartioningFactors(FR, FL, FS, FO)

        s.FR=FR
        s.FL=FL
        s.FS=FS
        s.FO=FO
        s.PF=PF
    
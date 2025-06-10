"""YAML File reader for the agromanagmenet file

Written by: Allard de Wit (allard.dewit@wur.nl), April 2014
Modified by Will Solow, 2024
"""

import os
import yaml
from ..utils import exceptions as exc

class YAMLAgroManagementReader(list):
    """Reads PCSE agromanagement files in the YAML format.

    :param fname: filename of the agromanagement file. If fname is not provided as a absolute or
        relative path the file is assumed to be in the current working directory.
    """

    def __init__(self, fname):
        """Initialize class `YAMLAgroManagementReader
        """
        fname_fp = os.path.normpath(os.path.abspath(fname))
        if not os.path.exists(fname_fp):
            msg = "Cannot find agromanagement file: %s" % fname_fp
            raise exc.PCSEError(msg)

        with open(fname) as fp:
            try:
                r = yaml.safe_load(fp)
            except yaml.YAMLError as e:
                msg = "Failed parsing agromanagement file %s: %s" % (fname_fp, e)
                raise exc.PCSEError(msg)

        list.__init__(self, r['AgroManagement'])

    def __str__(self):
        return yaml.dump(self, default_flow_style=False)

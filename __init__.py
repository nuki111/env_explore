'''
env_explore is a library for quick and easy exploration of python objects
=========================================================================
**env_explore** combines pandas and ipywidgets to extract and process data
from almost any given python object into pandas DataFrame and generate a
clickable widget representation with which users can interact.
'''

__author__ = 'Oscar Nuki'

from .utils.backend import (getmain, envtodict, envtopandas, envtohtmltable, 
                           getattrsafe, maineval, EnvObj, EnvDict, EnvDf)

from .utils.frontend import (usename, hboxes, vboxes, arrange, ishtml,
                            showobj, runperiodic, runperiodicfactory, 
                            Printed, HTMLCode, LoadingButton, ClearButton)

from .processing import (EnvHandeler)

from .interface import (WidgetCell, WidgetDf, WidgetEnv, AutoWidgetEnv)
import os.path

PROJECT_PATH = os.path.dirname(os.path.dirname(__file__))

from django import *
from aps42 import *

#########################################################################
# Import settings from local_settings.py, if it exists.
#
# Put this at the end of settings.py

try:
  import local_settings
except ImportError:
  print """ 
    -------------------------------------------------------------------------
    You need to create a local_settings.py file which needs to contain at least
    database connection information.
    
    Copy local_settings_example.py to local_settings.py and edit it.
    -------------------------------------------------------------------------
    """
  import sys 
  sys.exit(1)
else:
  # Import any symbols that begin with A-Z. Append to lists any symbols that
  # begin with "EXTRA_".
  import re
  for attr in dir(local_settings):
    match = re.search('^EXTRA_(\w+)', attr)
    if match:
      name = match.group(1)
      value = getattr(local_settings, attr)
      try:
        globals()[name] += value
      except KeyError:
        globals()[name] = value
    elif re.search('^[A-Z]', attr):
      globals()[attr] = getattr(local_settings, attr)


# datalake_lib/ingress/eia.py
import os
import requests
from datalake_lib.core import eia_url
from datetime import date, timedelta
import logging 
import time 


header = {
    "frequency": "daily",
    "data": [
        "value"
    ],
    "facets": {},
    "start": duration,
    "end": duration,
    "sort": [
        {
            "column": "period",
            "direction": "asc"
        }
    ],
    "offset": 0,
    "length": 5000
}
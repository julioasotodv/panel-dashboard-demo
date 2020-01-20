import numpy as np
import pandas as pd

from data import (create_basic_data, 
                  load_and_parse_geographic_data, 
                  create_random_dataset, 
                  create_conteos_mensuales, 
                  create_conteos_activos)

def on_server_loaded(server_context):
    ''' If present, this function is called when the server first starts. '''
    create_basic_data()
    load_and_parse_geographic_data()
    create_random_dataset()
    create_conteos_mensuales()
    create_conteos_activos()


import os
import uuid

import numpy as np
import pandas as pd
import pendulum
import yaml
import zope.dottedname.resolve

import kikundi.utils

logger = kikundi.utils.get_logger(__name__)

def load_data(path, sep=','):
    """
    Load delimited (by <sep>) df at <path> to pandas dataframe
    """
    logger.info("Loading data from {}".format(path))

    df = pd.read_csv(path, sep=sep)

    l, w = df.shape

    logger.info('...Data points: {}'.format(l))
    logger.info('...Columns: {}'.format(w))
    
    return df


def load_yaml(path):
    """
    Load yaml at <path> to dictionary, d
    
    Returns
    =======
    Wrapper dictionary, D where
    D = {filename: d}
    """
    if not os.path.isfile(path):
        return None
    with open(path) as f:
        d = yaml.load(f)
        
    filename = os.path.splitext(
        os.path.basename(path)
    )[0]
    
    return {filename: d}

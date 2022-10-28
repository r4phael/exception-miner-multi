import os
import pandas as pd
import numpy as np
from numpy.random import default_rng

rng = default_rng()


def split_dataset(df: pd.DataFrame):
    train, validate, test = \
        np.split(df.sample(frac=1, random_state=42),
                 [int(.6*len(df)), int(.8*len(df))])

    return train, validate, test


def save_task1_pkl(dataframe: pd.DataFrame):
    train, validate, test = split_dataset(dataframe)
    
    os.makedirs('output/py/data/task1', exist_ok=True)

    train.to_pickle('output/py/data/task1/train.pkl', protocol=4)
    validate.to_pickle('output/py/data/task1/valid.pkl', protocol=4)
    test.to_pickle('output/py/data/task1/test.pkl', protocol=4)

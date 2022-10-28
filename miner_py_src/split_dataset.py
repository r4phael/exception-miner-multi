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

    train.to_pickle('../output/py/task1/data/train.pkl', protocol=4)
    validate.to_pickle('../output/py/task1/data/valid.pkl', protocol=4)
    test.to_pickle('../output/py/task1/data/test.pkl', protocol=4)

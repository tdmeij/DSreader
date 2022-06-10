
import os
import numpy as np
import pandas as pd

def relativepaths(column,rootdir):
    """Replace absolute path names with paths relative to root
    
    Parameters
    ----------
    column : pd.Series
        Absolute pathnames

    rootdir : str
        Absolute path to root directory

    Returns
    -------
    pd.Series
    
    """
    newcolumn = column.apply(lambda x:'..\\'+x.removeprefix(
        rootdir) if not pd.isnull(x) else x)
    return newcolumn

def absolutepaths(column,rootdir):
    """Replace relative path names with absolute paths
    
    Parameters
    ----------
    column : pd.Series
        Relative pathnames

    rootdir : str
        Absolute path to root directory

    Returns
    -------
    pd.Series
    
    """
    newcolumn = column.apply(
            lambda x:os.path.join(rootdir,x.lstrip('..\\'))
            if not pd.isnull(x) else np.nan
            )
    return newcolumn


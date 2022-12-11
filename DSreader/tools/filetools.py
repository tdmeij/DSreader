
import os
import numpy as np
from pandas import Series, DataFrame
import pandas as pd

def relativepath(abspath,rootdir):
    """Replace absolute path names with paths relative to root
    
    Parameters
    ----------
    abspath : pd.Series | str
        Absolute pathname.

    rootdir : str
        Absolute path to root directory

    Returns
    -------
    pd.Series, str
    
    """
    if isinstance(abspath,Series):
        relpath = abspath.apply(lambda x:'..\\'+x.removeprefix(
            rootdir) if not pd.isnull(x) else x)

    elif isinstance(abspath,str):
        relpath = '..\\'+abspath.removeprefix(rootdir)

    return relpath



def absolutepath(relpath,rootdir):
    """Replace relative path name with absolute path name.
    
    Parameters
    ----------
    relpath : pd.Series | str
        Relative pathnames.

    rootdir : str
        Absolute path to root directory.

    Returns
    -------
    pd.Series, str
    
    """
    if isinstance(relpath,Series):
        abspath = relpath.apply(
                lambda x:os.path.join(rootdir,x.lstrip('..\\'))
                if not pd.isnull(x) else np.nan
                )
    elif isinstance(relpath,str):
        abspath = os.path.join(rootdir,relpath.lstrip('..\\'))

    return abspath


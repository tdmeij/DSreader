
import re

def year_from_string(rawstring, minyear=1960, maxyear=2050):
    """
    Parse year from given string. For strings with more 
    than one valid year the last year is returned.
    
    Parameters
    ----------
    rawstring : str
        String that might contain a year between minyear and maxyear.
    minyear : int
        Years below this number are ignored.
    maxyear : int
        Years above this number are ignored.

    Returns
    -------
    str
    """
    # return any valid year in the text
    # between given years
    allyears = re.findall(r'\D(\d\d\d\d)',rawstring)
    validyears = [int(e) for e in allyears if minyear<= int(e) <= maxyear]

    # return last found year or None
    if len(validyears)>0:
        return str(validyears[-1])
    else:
        return ''

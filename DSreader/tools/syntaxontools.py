"""Module with functions operating on syntaxon codes."""

import re as _re

SBBDICT = {
    'klasse':_re.compile(r'^[0-9][0-9]$'),
    'klasseromp': _re.compile(r'^[0-9]+-[a-z]$'),
    'klassederivaat': _re.compile(r'^[0-9]+/[a-z]$'),
    'verbond':_re.compile(r'^[0-9]+[A-Z]$'),
    'verbondsromp': _re.compile(r'^[0-9]+[A-Z]-[a-z]$'),
    'verbondsderivaat': _re.compile(r'^[0-9]+[A-Z]/[a-z]$'),
    'associatie': _re.compile(r'^[0-9]+[A-Z][0-9]+$'),
    'subassociatie': _re.compile(r'^[0-9]+[A-Z][0-9]+[a-z]$'),
    }

VVNDICT = {
    'klasse':_re.compile(r'r?[0-9]?[0-9]$'),
    'orde': _re.compile(r'r?[0-9]?[0-9][A-Z]$'),
    'verbond' : _re.compile(r'r?[0-9]?[0-9][A-Z][A-z]$'),
    'associatie': _re.compile(r'r?[0-9]?[0-9][A-Z][A-z][0-9]?[0-9]$'),
    'subassociatie': _re.compile(r'r?[0-9]?[0-9][A-Z][A-z][0-9]?[0-9][A-z]$'),
    'romp': _re.compile(r'r?[0-9]?[0-9]RG[0-9]?[0-9]$'),
    'derivaat': _re.compile(r'r?[0-9]?[0-9]DG[0-9]?[0-9]$'),
    }


def _regexdict(system):
    """Return dictionary with Regex expressions for all of possible syntaxonomic levels."""

    if system=='sbbcat':
        syndict = SBBDICT
    elif system=='vvn':
        syndict = VVNDICT
    elif system=='rvvn':
        syndict = VVNDICT
    else:
        raise ValueError(f'{system} is not a valid reference system.')

    return syndict

def get_class(code, system='sbbcat'):
    """Return class of given staatsbosbeheer catalogus syntaxon code.
    
    Parameters
    ----------
    code : string
        Valid Staatsbosbeheer Syntaxon code.
    system : {'sbbcat', 'vvn', 'rvvn'}, default 'sbbcat'
        Syntaxonomic reference system.

    Returns
    -------
    str, class of syntaxon
        
    """
    syndict = _regexdict(system)

    result = None
    for key in syndict.keys():
        if syndict[key].match(code):
            result=syndict[key].match(code).group(0)

    if system=='sbbcat':
        result = result[:2]
    elif result.startswith('r'):
        result = result[:3]
    else:
        result = result[:2]
    return result


def get_synlevel(code, system='sbbcat'):
    """Return syntaxonomic level of given staatsbosbeheer catalogus 
    syntaxon code.
    
    Parameters
    ----------
    code : string
        Valid Staatsbosbeheer syntaxon code.
    system : {'sbbcat', 'vvn', 'rvvn'}, default 'sbbcat'
        Syntaxonomic reference system.

    Returns
    -------
    str, syntaxon level
        
    """
    syndict = _regexdict(system)

    result = None
    for key in syndict.keys():
        if syndict[key].match(code):
            result=key 

    return result


def get_possible_levels(system='sbbcat'):
    """Return list of all possible syntaxon levels in the Staatsbosbeheer 
    catalogus.

    Parameters
    ----------    
    system : {'sbbcat', 'vvn', 'rvvn'}, default 'sbbcat'
        Syntaxonomic reference system.
        
    """
    return list(_regexdict(system).keys())

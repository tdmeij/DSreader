"""Module with functions for analying Staatsbosbeheer Catalogus 
vegetation types."""

import re

REGDICT = {
    'klasse':re.compile(r'^[0-9][0-9]$'),
    'klasseromp': re.compile(r'^[0-9]+-[a-z]$'),
    'klassederivaat': re.compile(r'^[0-9]+/[a-z]$'),
    'verbond':re.compile(r'^[0-9]+[A-Z]$'),
    'verbondsromp': re.compile(r'^[0-9]+[A-Z]-[a-z]$'),
    'verbondsderivaat': re.compile(r'^[0-9]+[A-Z]/[a-z]$'),
    'associatie': re.compile(r'^[0-9]+[A-Z][0-9]+$'),
    'subassociatie': re.compile(r'^[0-9]+[A-Z][0-9]+[a-z]$'),
}


def get_class(code):
    """Return class of given staatsbosbeheer catalogus syntaxon code.
    
    Parameters
    ----------
    code : string
        Valid Staatsbosbeheer Syntaxon code.
    Returns
    -------
    str, class of syntaxon """
    result = None
    for key in REGDICT.keys():
        if REGDICT[key].match(code):
            result=REGDICT[key].match(code).group(0)[:2]
    return result

def get_synlevel(code):
    """Return syntaxonomic level of given staatsbosbeheer catalogus 
    syntaxon code.
    
    Parameters
    ----------
    code : string
        Valid Staatsbosbeheer syntaxon code.
    Returns
    -------
    str, syntaxon level"""

    result = None
    for key in REGDICT.keys():
        if REGDICT[key].match(code):
            result=key 
    return result

def syntaxon_levels():
    """Return list of all possible syntaxon levels in the Staatsbosbeheer 
    catalogus."""
    return list(REGDICT.keys())


from pandas import Series, DataFrame
import pandas as pd

class Releve:
    """Vegetation releve data."""

    TVHABITA_COLNAMES = [
       'releve_nr', 'reference', 'coverscale', 'project', 'author',
       'date', 'km_hok_x', 'km_hok_y', 'blok', 'syntaxon', 'new_syntax',
       'length', 'width', 'surf_area', 'exposition', 'inclinatio',
       'cov_total', 'cov_trees', 'cov_shrubs', 'cov_herbs', 'cov_mosses',
       'cov_algae', 'cov_litter', 'tree_high', 'tree_low', 'shrub_high',
       'shrub_low', 'herb_high', 'herb_low', 'herb_max', 'moss_ident',
       'pq', 'transect', 'sbbcode', 'remarks', 'nat2000geb',]

    TVABUND_COLNAMES = ['species_nr', 'cover_code', 'layer']

    TVFLORA_COLNAMES = ['species_nr', 'lettercode', 'shortname', 'abbreviat', 
        'nativename','remarks',]

    
    def __init__(self, header=None, species=None, meta=None):

        self.tvhabita = Series(index=self.TVHABITA_COLNAMES, name='tvhabita', dtype='object')

        self.tvabund = DataFrame(columns = self.TVABUND_COLNAMES)
        self.tvabund.index.name = 'entry'

        self.tvflora = DataFrame(columns = self.TVFLORA_COLNAMES)
        self.tvflora.set_index('species_nr', drop=True, inplace=True)
        self.tvflora.index.name = 'species_nr'

    def __repr__(self):
        return f'{self.__class__.__name__}(n={len(self)})'

    def __len__(self):
        return len(self.tvabund)


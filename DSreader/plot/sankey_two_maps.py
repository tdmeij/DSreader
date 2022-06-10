"""
Module with class SankeyTwoMaps for plotting Sankey diagram that
shows the changes between two consequtive maps.
"""


import numpy as np
from pandas import Series, DataFrame
import pandas as pd

import plotly.graph_objects as go
import plotly.express as pex
import itertools

class SankeyTwoMaps:
    """Plot Sankey diagram comparing changes between two consequtive maps"""

    def __init__(self,changes,fromyear=None,toyear=None):
        """Create SankeyTwoMaps instance
        
        Parameters
        ----------
        changes : pd.Series
            Table with changes.
        fromyear : str
            Year of first map.
        toyear : str
            Year of second map.

        Notes
        -----
        Parameter changes is a pandas series with multiindex 
        'from' and 'two' with values showing quantities of changes.
        """

        if not isinstance(changes,pd.Series):
            raise Exception(f'Expect class pandas.Series, not {changes.__class__}')
        self._changes = changes
        self.fromyear = fromyear
        self.toyear = toyear

    #def __repr__(self):
    #    return (f'{self._changes}')

    def _changes_example(self):
        """Return example of pandas Series with changes"""
        mydict = {
            ('2009_K1', '2017_K1'): 116,
            ('2009_K1', '2017_K2'): 122,
            ('2009_K1', '2017_K3'): 5,
            ('2009_K1', '2017_K4'): 158,
            ('2009_K2', '2017_K1'): 81,
            ('2009_K2', '2017_K2'): 334,
            ('2009_K2', '2017_K3'): 9,
            ('2009_K2', '2017_K4'): 466,
            ('2009_K3', '2017_K1'): 9,
            ('2009_K3', '2017_K2'): 49,
            ('2009_K3', '2017_K4'): 135,
            ('2009_K4', '2017_K1'): 48,
            ('2009_K4', '2017_K2'): 355,
            ('2009_K4', '2017_K3'): 6,
            ('2009_K4', '2017_K4'): 1612,
            }
        return Series(mydict)


    def _labels(self):
        """Return list of unique group labels"""
        from_labels = list(self._changes.index.get_level_values(0).unique().values)
        to_labels = list(self._changes.index.get_level_values(1).unique().values)
        labels = sorted(list(set(from_labels+to_labels)))
        return labels

    def _values(self,changes,labels):
        """Return list of values with changes to plot"""

        sourcenr = []
        targetnr = []
        values = []

        changes = changes.sort_index(axis=0,level=('from', 'to'), ascending=False)
        for (idx1,idx2),value in changes.iteritems():
            sourcenr.append(labels.index(idx1))
            targetnr.append(labels.index(idx2))
            values.append(value)
        return sourcenr,targetnr,values

        """
        # random colors
        colors = pex.colors.qualitative.D3
        node_colors_mappings = dict([(node,np.random.choice(colors,replace=False)) for node in labels])
        """
        
    def _label_color_maps(self,labels):
        """Return color mappings labels"""
        cmap = {}
        for lab in labels:
            if 'K1' in lab:
                cmap[lab]='#d7191c'
            if 'K2' in lab:
                cmap[lab]='#fdae61'
            if 'K3' in lab:
                cmap[lab]='#2c7bb6'
            if 'K4' in lab:
                cmap[lab]='#c9c9c9'
        return cmap

    def _node_colors(self,labels,cmap):
        """Return list of node colors"""
        node_colors = [cmap[label] for label in labels]
        return node_colors

    def _edge_colors(self,labels,cmap,sourcenr):
        """Return list of node colors"""
        edge_colors = [cmap[labels[nr]] for nr in sourcenr] #Waarom niet ook voor targetnr?
        return edge_colors
        

    def _xpos(self,labels):
        """Return list of xpositions for all labels"""
        xpos=[]
        for lab in labels:
            if self.fromyear in lab:
                xpos.append(0.1)
            if self.toyear in lab:
                xpos.append(0.9)
        return xpos

    def _ypos(self,labels):
        """Return list of ypositions for all labels"""   
        ypos=[]
        for lab in labels:
            if 'K1' in lab:
                ypos.append(0.1)
            if 'K2' in lab:
                ypos.append(0.3)
            if 'K3' in lab:
                ypos.append(0.5)
            if 'K4' in lab:
                ypos.append(0.9)
        return ypos

    def _create_fig(self,plotname):

        fig = go.Figure(data=[go.Sankey(
            arrangement = "snap",
            node = dict(
              pad = 5,
              thickness = 20,
              line = dict(color = "black", width = 0.3),
              label = self.labels,
              color = self.node_colors,
              x = self.xpos,
              y = self.ypos,
            ),
            link = dict(
              source = self.sourcenr,
              target = self.targetnr,
              value = self.values,
              color = self.edge_colors,
          ))])

        fig.update_layout(
            title={
                'text': plotname,
                'y':0.95,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'},
                font=dict(
                    #family="Courier New, monospace",
                    size=14,
                    color="#000000"
                    ),
                )

        return fig

    def sankeyplot(self,filename,plotname):
        """Write Sankeyplot to file"""
        
        changes = self._changes
        
        self.labels = self._labels()
        self.sourcenr,self.targetnr,self.values = self._values(changes,self.labels)
        self.cmap = self._label_color_maps(self.labels)
        self.node_colors = self._node_colors(self.labels,self.cmap)
        self.edge_colors = self._edge_colors(self.labels,self.cmap,self.sourcenr)
        self.xpos = self._xpos(self.labels)
        self.ypos = self._ypos(self.labels)

        fig = self._create_fig(plotname)
        fig.write_image(filename)
        fig.show()


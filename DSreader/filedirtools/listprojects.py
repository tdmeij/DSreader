
import os
import re
import warnings
import numpy as np
from pandas import Series, DataFrame
import pandas as pd
import difflib


class ListProjects:
    """List sourcefiles in Digitale Standaard project folders

    Methods
    -------
    projects
        Return pd.DataFrame of project directories under root.
    projectpaths
        Return pd.DataFrame with fullpath of all project files.
    check_selection
        Return pd.DataFrame with names of projects and filenames
        that seem to match the project (for manually checking guesses)

    Notes
    -----
    Projects should be organised in subfolders under a root folder.
    Projectfolders should be at the second level beneath the root folder. 
    The first level beneath the root folder is called 'provincie'. 
    A typical project folder path should look like:
    '..\01_Standaard\Drenthe\Dr 0007_Hijken_1989' 
    where '..\01_Standaard\' is the root folder.
    """

    def __init__(self,rootdir):
        """
        Parameters
        ----------
        rootdir : str
            root directory with project directories
        """
        if not isinstance(rootdir,str):
            raise TypeError(f'rootdir must be of type string not {type(rootdir)}')

        if not os.path.isdir(rootdir):
            raise TypeError(f'{rootdir} is not a valid directory name.')

        self._rootdir = rootdir
        self._projects = self.projects()

    def __repr__(self):
        nprj = len(self._projects)
        return (f'{nprj} projects')

    def projects(self):
        """Return list of project folders at level 2 under the root folder"""
        # projects are stored in a directory structure that looks like:
        # ..\01_Standaard\Drenthe\Dr 0007_Hijken_1989
        prvlist = []    #'Drenthe'
        prjlist = []    #'Dr 0007_Hijken_1989'
        yearlist = []   #'1989'
        pathlist = []   #fullpath

        prvnames = ([subdir for subdir in os.listdir(self._rootdir) 
            if os.path.isdir(os.path.join(self._rootdir,subdir))])

        for prvname in prvnames:

            # project names from folder names
            prjnames = [prjdir for prjdir in os.listdir(
                os.path.join(self._rootdir,prvname)) if os.path.isdir(
                os.path.join(self._rootdir,prvname,prjdir))] 
            prjpaths = [os.path.join(self._rootdir,prvname,prj) for prj in prjnames]

            # get years from folder name
            prjyears = []
            for prj in prjnames:
                match = re.match(r'.*([1-2][0-9]{3})', prj)
                if match is not None:
                    prjyears.append(match.group(1))
                else:
                    prjyears.append('')

            # append lists to lists
            prvlist += [prvname]*len(prjnames)
            prjlist += prjnames
            yearlist += prjyears
            pathlist += prjpaths

        self._projects = DataFrame(data=list(zip(prvlist,yearlist,prjlist,pathlist)),
            columns=['provincie','year','project','prjdir'])
        return self._projects

    def _listfiletype(self,filetype=None,colname=None):
        """
        Return table of all files of specified filetype under root

        Parameters
        ----------
        filetype : str
            list of file will be restricted to filetype
        colname : str
            results will be stored in colomn name colname

        Return
        ------
        pd.DataFrame
        """
        # check variable filetype
        if isinstance(filetype,str):
            filetype=filetype.lstrip('.')
            if not len(filetype)==3:
                    warnings.warn(f'{filetype} is not a valid filetype.')
                    filetype=None

        if filetype is None:
            warnings.warn(f'Filetype is None. All files wil be listed.')

        if colname is None:
            colname='fpath'
            if isinstance(filetype,str):
                colname = f'{filetype}fpath'

        # DataFrame of filepaths by project
        pathlist = []
        for idx,row in self._projects.iterrows():
            
            for rootdir,subdirs,files in os.walk(row['prjdir']):
                for f in files:
                    rowdict = row.to_dict()
                    rowdict[colname] = str(os.path.join(rootdir,f))
                    pathlist.append(rowdict)
        tbl = pd.DataFrame(pathlist)

        if filetype is not None:
            mask = tbl[colname].str.endswith(f'.{filetype}')
            tbl = tbl[mask].copy()

        return tbl


    def _selectfiletype(self,filetype,guessfile=False):
        """
        Return table with all files of given filetype and indication of 
        file that looks like the best match for the project"""

        if filetype.startswith('.'):
            filetype=filetype[1:]

        # colnames depend on filetype
        pathcol=filetype+'path'
        filedircol=filetype+'dir'
        selcol=filetype+'sel'
        namecol=filetype+'name'
        simcol=filetype+'sim'
        guescol=filetype+'gues'

        # find all filepaths of type filetype
        files = self._listfiletype(filetype=filetype,colname=pathcol)

        dirpaths = files[pathcol].apply(lambda x:os.path.dirname(x))
        files[filedircol]=dirpaths

        # calculate string similarity between file name and project name
        srfilenames = files[pathcol].apply(lambda x:os.path.splitext(
            os.path.basename(x))[0])
        filenames = list(srfilenames.values)
        files[namecol]=filenames
        prjnames = list(files['project'].values)
        similarities = [difflib.SequenceMatcher(None, p1, p2).ratio() 
            for (p1,p2) in zip(filenames,prjnames)]
        files[simcol]=similarities

        files[selcol]=False
        files[guescol]=False

        for (provincie,project),tbl in files.groupby(['provincie','project']):

            rowidx=None
            if len(tbl)==0: #no file found
                warnings.warn((f'No {filetype} file found for project {prj}'))

            if len(tbl)==1: #just one file
                rowidx = tbl.index[0]
                files.loc[rowidx,selcol]=True

            if len(tbl)>1: #multiple files

                # mask: file is in project folder
                filedir = tbl[filedircol].apply(os.path.normcase).values
                prjdir = tbl['prjdir'].apply(os.path.normcase).values
                inroot = np.where(filedir==prjdir,True,False)

                # mask: filename is like vlakken
                isname = tbl[namecol].str.lower()=='vlakken'
                hasname = tbl[namecol].str.lower().str.contains('vlakken')

                if len(tbl[inroot])==1: #just one file in project folder
                    rowidx = tbl[inroot].index[0]
                    files.loc[rowidx,selcol]=True

                if filetype=='shp':
                    # for shapefiles any file with name vlakken 
                    # has preference

                    if len(tbl[inroot&isname])==1:
                        rowidx = tbl[inroot&isname].index[0]
                        files.loc[rowidx,selcol]=True

                    elif len(tbl[inroot&hasname])==1:
                        rowidx = tbl[inroot&hasname].index[0]
                        files.loc[rowidx,selcol]=True

                    elif len(tbl[isname])==1:
                        rowidx = tbl[isname].index[0]
                        files.loc[rowidx,selcol]=True

                    elif len(tbl[hasname])==1:
                        rowidx = tbl[hasname].index[0]
                        files.loc[rowidx,selcol]=True

                if (guessfile is True) and (rowidx is None):
                    # from here on its all guesswork

                    if filetype=='shp':

                        if len(tbl[isname])>1:
                            # select on highest similarity between file name 
                            # and project name
                            rowidx = tbl[isname].sort_values(simcol).index[-1]
                            files.loc[rowidx,selcol]=True
                            files.loc[rowidx,guescol]=True

                        elif len(tbl[hasname])>1:
                            # select on highest similarity between file name 
                            # and project name
                            rowidx = tbl[hasname].sort_values(simcol).index[-1]
                            files.loc[rowidx,selcol]=True
                            files.loc[rowidx,guescol]=True

                if (guessfile is True) and (rowidx is None):
                    # this second if prevents duplicate shp entries

                    if len(tbl[inroot])>1: #multiple files in prj folder, 
                        # select by similarity between file name and project name
                        rowidx = tbl[inroot].sort_values(simcol).index[-1]
                        files.loc[rowidx,selcol]=True
                        files.loc[rowidx,guescol]=True

                    if len(tbl[inroot])==0: #no filetype files in project folder
                        # last resort: take file with highest simililarity 
                        # from all available files, regardless
                        # of directory
                        rowidx = tbl.sort_values(simcol).index[-1]
                        files.loc[rowidx,selcol]=True
                        files.loc[rowidx,guescol]=True
        return files

    def projectpaths(self,relpaths=True):
        """Return table with filepaths for all projects"""

        prj = self.projects()
        prj = prj[['provincie','project']].copy()

        if not hasattr(self,'_mdbfiles'):
            self._mdbfiles = self._selectfiletype('mdb',guessfile=True)
        selected = self._mdbfiles['mdbsel']==True
        mdb = self._mdbfiles[selected].copy()

        if not hasattr(self,'_shpfiles'):
            self._shpfiles = self._selectfiletype('shp',guessfile=True)
        selected = self._shpfiles['shpsel']==True
        shp = self._shpfiles[selected].copy()

        mergecols = ['provincie','project']
        prj = pd.merge(prj,mdb,how='left',left_on=mergecols,
            right_on=mergecols,suffixes=[None,'_from_mdb'],
            validate='one_to_one')
        prj = pd.merge(prj,shp,how='left',left_on=mergecols,
            right_on=mergecols,suffixes=[None,'_from_shp'],)
            #validate='one_to_one')

        dup_mdb = [x for x in prj.columns if '_from_mdb' in x]
        dup_shp = [x for x in prj.columns if '_from_shp' in x]
        duplicates = dup_mdb+dup_shp
        prj = prj.drop(columns=duplicates)

        if relpaths: #remove root from paths
            for col in ['prjdir','mdbpath','mdbdir','shppath','shpdir']:
                prj[col] = prj[col].apply(lambda x:'..\\'+x.removeprefix(
                    self._rootdir) if not pd.isnull(x) else x)

        return prj

    def check_selection(self,filetype=None,filename=None):
        """Return table with guessed project files for manual check"""

        prj = self.projectpaths()
        colnames = ['project','provincie','mdbname','shpname']
        prj = prj[colnames].copy()

        if filename is not None:
            #write to excel
            writer = pd.ExcelWriter(filename) 
            prj.to_excel(writer, sheet_name='results', index=True, na_rep='NaN')

            # auto-adjust column width
            for column in prj:
                column_width = max(prj[column].astype(str).map(len).max(), len(column))
                col_idx = prj.columns.get_loc(column)
                writer.sheets['results'].set_column(col_idx, col_idx, column_width)

            writer.save()

        return prj


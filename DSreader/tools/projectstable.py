
import os
##import re
import warnings
import numpy as np
from pandas import Series, DataFrame
import pandas as pd
import difflib

from .filetools import relativepath,absolutepath
from .conversions import year_from_string

class ProjectsTable:
    """
    Find filepaths to ESRI shapefiles and Microsoft Acces database files 
    for each projectfolder under a given root directory.

    The method list_projectfiles() returns a table with all projects 
    and the corresponding shapefile and access mdbfile, if they were 
    found. This table is the main result for this class, all the other 
    methods are merely preparations and checks.

    Methods
    -------
    list_projectfiles
        Return table with all projects and filepaths found.
    list_projects
        Return table of project directories under root.
    list_files
        Return table with all files of given filetype under root.
    list_tv2
        Return table with all Turboveg2 project files
        under a project folder.
    projectfiles_counts
        Return table of file counts by project for given filtetype.
    filter_mdbfiles
        Return table with project mdbfiles.
    filter_shapefiles
        Return table with project shapefiles.

    Notes
    -----
    Projects are supposed to be organised in subfolders under a root 
    folder. Projectfolders should be at the second level beneath the 
    root folder. 
    The first level beneath the root folder is called 'provincie'. 
    A typical project folder path should look like:
    '..\\01_Standaard\Drenthe\Dr 0007_Hijken_1989' 
    where '..\\01_Standaard\' is the root folder.
        
    """

    _discardtags = ['conversion','ConversionPGB','catl','ctl','soorten',
        'kopie','test','kievit','oude versie','db1','test','fout',
        'themas','florakartering','flora','toestand','backup',
        'foutmelding','Geodatabase',]

    def __init__(self,rootdir,relpaths=True):
        """
        Parameters
        ----------
        rootdir : str
            Root directory with project directories
        repaths : boolean, default True
            Return relative filepaths
        """
        if not isinstance(rootdir,str):
            raise TypeError((f'rootdir must be of type string '
                f'not {type(rootdir)}'))

        if not os.path.isdir(rootdir):
            raise TypeError(f'{rootdir} is not a valid directory name.')

        self._rootdir = rootdir
        self._relpaths = relpaths
        self._projects = DataFrame()


    def __repr__(self):
        if self._projects.empty:
            self._projects = self.list_projects()
        return (f'{self.__class__.__name__} ({len(self._projects)} projects)')


    def __len__(self):
        if self._projects.empty:
            self._projects = self.list_projects()
        return len(self._projects)

    def _relativepaths(self,column):
        """Replace absolute path with path relative to root"""
        return relativepath(column,self._rootdir)


    def _absolutepaths(self,column):
        """Replace path relative to root with absolute path"""
        return absolutepath(column,self._rootdir)


    def list_projects(self):
        """Return table of projects

        Notes
        -----
        Digital Standard vegetation mapping projects are stored in a 
        directory structure below the root folder '..\\01_Standaard\'
        that looks like:
         ..\\01_Standaard\Drenthe\Dr 0007_Hijken_1989
        First level are Dutch provinces (e.g. 'Drenthe'), second level 
        are project directories (e.g. 'Dr 0007_Hijken_1989').
        Foldernames at level 2 under the root folder are used as 
        Projectnames.

        Mapping projects that cross province boundaries can be present
        as a project in both provinces. Therefore, grouping must be done
        on the combination of 'province' and 'project'.  
           
        """
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
                year = year_from_string(prj)
                prjyears.append(year)

            # append lists to lists
            prvlist += [prvname]*len(prjnames)
            prjlist += prjnames
            yearlist += prjyears
            pathlist += prjpaths

        self._projects = DataFrame(data=list(zip(prvlist,prjlist,yearlist,pathlist)),
            columns=['provincie','project','year','prjdir'])
        self._projects = self._projects.set_index(keys=['provincie','project'],
            verify_integrity=True)

        # relative path to prjdir
        if self._relpaths:
            self._projects['prjdir'] = self._relativepaths(self._projects['prjdir'])

        return self._projects

    def _validate_filetype(self,filetype=None):
        """Return valid filetype string or None"""
        if filetype is not None:
            if isinstance(filetype,str):
                filetype=filetype.lstrip('.')
                #if not filetype.startswith('.'):
                #    filetype = f'.{filetype}'
                if not len(filetype)==3:
                        warnings.warn(f'{filetype} is not a valid filetype.')
                        filetype=None
            else:
                warnings.warn(f'{filetype} is not a valid filetype.')
                filetype=None
        return filetype

    def _file_in_projectdir(self,filetbl,pathcol=None):
        """
        Return boolean mask for files in project directory with 
    `   preserved index

        Parameters
        ----------
        filetbl : pd.DataFrame
            table with filepathnames as returned by list_files()
        pathcol : str
            column name with filepath
        """
        prjtbl = self.list_projects()
        prjdirs = Series(index=filetbl.index,dtype='object')
        for idx in prjdirs.index:
            prv = filetbl.loc[idx,'provincie']
            prj = filetbl.loc[idx,'project']
            prjdirs.loc[idx] = prjtbl.loc[(prv,prj),'prjdir']
        filedirs = filetbl[pathcol].apply(lambda x:os.path.dirname(x))
        mask = filedirs==prjdirs
        return mask

    def list_files(self,filetype=None,relpaths=True):
        """
        Return table of all files by project for given filetype 

        Parameters
        ----------
        filetype : str, optional
            list of files will be restricted to filetype
        relpaths : bool, default True
            return paths relative to root folder

        Returns
        -------
        pd.DataFrame

        Notes
        -----
        Projects with no files of given filetype will not be present in
        the table that is returned.   
           
        """
        filetype = self._validate_filetype(filetype)
        if filetype is None:
            warnings.warn(f'Filetype is None. All files wil be listed.')

        fpathcol='fpath'
        fnamecol='fname'
        if isinstance(filetype,str):
            fpathcol=f'{filetype}path'
            fnamecol=f'{filetype}name'

        prjtbl = self.list_projects()
        if self._relpaths: # restore absolute paths
            prjtbl['prjdir'] = self._absolutepaths(prjtbl['prjdir'])

        # create list of dicts for each file under a project directory
        # and create dataframe with all filepaths by provincie, project
        pathlist = []
        empty_projects = []
        for (prv,prj),row in prjtbl.iterrows():
            for prjdir,subdirs,files in os.walk(row['prjdir']):
                for f in files:
                    filepath = os.path.join(prjdir,f)
                    #fname = 
                    rowdict = row.to_dict()
                    rowdict['provincie'] = prv
                    rowdict['project'] = prj
                    rowdict[fpathcol] = str(filepath)
                    rowdict[fnamecol] = f
                    pathlist.append(rowdict)
        tbl = pd.DataFrame(pathlist)

        # reorder columns
        colnames = ['provincie','project']+[fnamecol,fpathcol]
        tbl = tbl[colnames]

        if filetype is not None:
            mask = tbl[fpathcol].str.endswith(f'.{filetype}')
            tbl = tbl[mask].copy()

        if relpaths: #remove root from paths
            tbl[fpathcol] = self._relativepaths(tbl[fpathcol])

        return tbl.reset_index(drop=True)

    def list_tv2(self,relpaths=True):
        """Return table with all Turboveg2 project files
        under a project folder."""

        # create table of project directories
        pjt = self.list_projects()
        if self._relpaths: # restore absolute paths
            pjt['prjdir'] = self._absolutepaths(pjt['prjdir'])

        # traverse from root through all project directories and 
        # subdirectories and find all directories with Tuboveg2 files
        tvdirs=[]
        for (prv,prj),row in pjt.iterrows():
            for filedir,subdirs,files in os.walk(row['prjdir']):
                if 'tvhabita.dbf' in [f.lower() for f in files]:
                    tvdirs.append(
                        {'provincie':prv,'project':prj,'tvdir':filedir}
                        )
        return DataFrame(tvdirs)

    def projectfiles_counts(self,filetbl,colname=None,fill_missing=True):
        """
        Return table of filecounts by project for given filtetype

        Parameters
        ----------
        filetbl : pd.DataFrame
            Table with files listed by project as returned by list_files.
        colname : str, optional
            Give filecounts only for this column.
        fill_missing : bool, default True
            Include projects with zero files.

        Returns
        -------
        pd.DataFrame

        Notes
        -----
        This methods presumes a DataFrame as returned by the list_files 
        method, but any dataframe with the columns 'provincie' and 
        'project' should be accepted.
        """
        if not isinstance(filetbl,pd.DataFrame):
            warnings.warn(f'{filetbl} is not a DataFrame')
            return DataFrame()

        if colname is None:
            colname = 'shpname'
        if colname not in filetbl.columns:
            warnings.warn((f'"{colname}" not in filetbl columns: '
                f'{list(filetbl)}. Counts for all columns will be '
                f'returned.'))
            colname = None

        grp = filetbl.groupby(by=['provincie','project'])
        filecounts = grp.count()
        if colname is not None:
            filecounts = filecounts[colname].copy()
            filecounts.name = f'{colname}_counts'

        if fill_missing:
            index = self.list_projects().index
            filecounts = filecounts.reindex(index=index,fill_value=0)

        return filecounts

    def _list_ambiguous(self,masktbl):
        """
        Return table of all filenames for projects where no single 
        projectfile could be identified with certainty.
        
        Parameters
        ----------
        masktbl : pd.DataFrame
            Boolean values for filtering.

        Returns
        -------
        pd.DataFrame
        """
        tblist = []

        # group all files by project. If any file is marked 'masksel'
        # then this file is the wanted projectfile. If no such file
        # is present, return a table with all filenames in a project
        # and let the user sort it all out.
        for (provincie,project),tbl in masktbl.groupby(['provincie','project']):
            any_masksel = tbl['masksel'].any()
            if 'likename' in list(tbl):
                any_likename = tbl['likename'].any()
            else:
                any_likename = True
            if (not any_masksel) and any_likename:
                tblist.append(tbl)
        if tblist: #return table of ambigous filenames
            ambiguous = pd.concat(tblist)
        else: #return empty dataframe
            ambiguous = DataFrame(columns=masktbl.columns)
        return ambiguous

    def filter_mdbfiles(self,filetbl=None,discardtags=None,
        default_tags=False,priority_filepaths=None):
        """
        Return table with mdbfiles by project and table with projects 
        for which no single mdb-file could be selected.

        Parameters
        ----------
        filetbl : pd.DataFrame, optional
            Table with mdb filepaths as returned by list_files() method.
        discardtags : list of string, optional
            Mdb filepaths with these keywords will be ignored.
        default_tags : bool, default False
            Use standardtags for ignoring files. Value of discardtags
            will be ignored.
        priority_filepaths : list of string, optional
            Mdb filepaths in this list are selected as projectfiles.

        Returns
        -------
        mdbsel : DataFrame
            Table with selected mdbfiles.
        ambiguous : DataFrame
            Table with projects for which multiple mdbfiles remain
            present after filtering.

        Notes
        -----
        Results include only projects for which exactly one mdb file 
        could be identified as the most likely project file. Projects 
        with multiple possible mdbfiles or no mdb files at all are not
        included in the result.

        Valid mdb projectfiles can have any filename. Selection is based
        on file location (files in project folder have priority) and
        filepaths (filepaths that contain words present in discardtags 
        will be discarded). 
        Filepaths equal to strings in priority_filepaths are selected as 
        when multiple files are present.
        """
        if filetbl is None:
            filetbl = self.list_files(filetype='mdb',relpaths=True)

        if default_tags:
            discardtags = self._discardtags

        if discardtags is not None:
            if not isinstance(discardtags,list):
                warnings.warn(f'Input argument pathtags with invalid '
                    f'value {discardtags} will be ignored.')
                discardtags = None

        # mask for mdbfile in project directory
        mask_prjdir = self._file_in_projectdir(filetbl,pathcol='mdbpath')

        # mask for tags in pathfilter
        if discardtags:
            ##lowertags = [x.lower() for x in discardtags]
            ##mask_fpath = filetbl['mdbpath'].str.lower().str.contains(
            ##    '|'.join(lowertags),na=False,regex=True,case=False)
            ##mask_fpath = filetbl['mdbpath'].str.contains(
            ##    '|'.join(discardtags),na=False,regex=True,case=False)
            mask_fpath = filetbl['mdbpath'].apply(
                lambda x: any([tag.lower() in str(x).lower() for tag in discardtags]))
            
            sumfpath = sum(mask_fpath)
            warnings.warn((f'{sumfpath} rows with mdb-files have been '
                f'marked as copies based on given tags.'))
        else:
            mask_fpath = Series(data=False,index=filetbl.index)


        # masktbl is a temporary copy of filetbl with columns for masking
        # mask_fname and mask_prjdir are series with the same index
        # as DataFrame filetbl.
        masktbl = filetbl.copy()
        masktbl['maskprj'] = mask_prjdir
        masktbl['maskfpath'] = ~mask_fpath
        masktbl['masksel'] = False

        # step-wise select most probable mdb projectfile
        for (provincie,project),tbl in masktbl.groupby(['provincie','project']):

            if len(tbl)==1:
                # just one mdb in entire project tree structure
                idx = tbl.index[0]
            elif len(tbl[tbl['maskprj']])==1:
                # exactly one mdb in prjdir
                idx = tbl[tbl['maskprj']].index[0]
            elif len(tbl[tbl['maskfpath']])==1:
                # only one mdbfile found in entire tree structure 
                # after excluding unlikely files
                idx = tbl[tbl['maskfpath']].index[0]
            elif len(tbl[tbl['maskprj']&tbl['maskfpath']])==1:
                # only one mdb in prjdir after discarding unlikely 
                # files by pathname
                idx = tbl[tbl['maskprj']&tbl['maskfpath']].index[0]
            else:
                idx = None

            if (not idx) and priority_filepaths:
            # At this point, idx is still None. An mdb-projectfile has
            # not been choosen based on automated selection.
            # Parameter priority_filepaths contains a list of filepaths
            # of mdb-projects. If any of these filepaths is present in 
            # column mdbpath, this file will be selected.
                mask = tbl['mdbpath'].isin(priority_filepaths)
                if len(tbl[mask])==1:
                    idx = tbl[mask].index[0]

            if idx is not None:
                # mark chosen file as selected
                masktbl.loc[idx,'masksel']=True

        # create table of projects with selected mdb files
        mdbsel = filetbl[masktbl['masksel']]

        # create table of projects with to many ambiguous files to 
        # select a project mdb file
        ambiguous = self._list_ambiguous(masktbl)

        return mdbsel, ambiguous


    def filter_shapefiles(self,filetbl=None,shptype='polygon',colprefix=None,
        priority_filepaths=None):
        """
        Return table with project shapefiles and table with possible 
        projectfiles for projects where no single projectfile could be 
        identified with certainty.

        Parameters
        ----------
        filetbl : pd.DataFrame, optional
            Table with filepaths as returned by list_files() method.
        shptype : {'polygon','line'}, default 'polygon'
            Type of shapefile to filter.
        colprefix : str, optional
            Column in filetbl with filename. If None, default name is
            inferred from value of shptype.
        priority_filepaths : list of strings, optional
            Filepaths equal to a string in this list will allways be 
            selected as project shapefile, discarding other files.

        Returns
        -------
        shapesel : pd.DataFrame
            Table with selected shapefiles.
        ambigous : pd.DataFrame
            Table with shapefiles for projects for which no single 
            shapefile could be selected.

        Notes
        -----
        Valid shapefiles with vegetation polygons are called 'vlakken', 
        'Vlakken', or they have the keyword 'vlak' somewhere in their 
        filename. For line elements these keywords are 'lijnen' or 
        'lijn'. For point elements keyword is 'point'.
        """
        if filetbl is None:
            filetbl = self.list_files(filetype='shp',relpaths=True)

        # masks for filename contains keyword
        if shptype=='polygon':
            key_isname = 'vlakken.shp'
            key_contains = 'vlak'
            if colprefix is None:
                colprefix = 'poly'
        elif shptype=='line':
            key_isname = 'lijnen.shp'
            key_contains = 'lijn'
            if colprefix is None:
                colprefix = 'line'
        else:
            raise(f'{shptype} is not a valid shapefile type. ')

        namecol='shpname'
        pathcol='shppath'

        isname = filetbl[namecol].str.lower()==key_isname
        likename = filetbl[namecol].str.lower().str.contains(key_contains)

        # mask for file in project directory
        masktbl = filetbl.copy()
        mask_prjdir = self._file_in_projectdir(masktbl,pathcol=pathcol)

        # masktbl is a temporary copy of filetbl with columns for masking
        # mask_fname and mask_prjdir are series with the same index
        # as DataFrame filetbl.
        masktbl['isname'] = isname
        masktbl['likename'] = likename
        masktbl['inprj'] = mask_prjdir
        masktbl['masksel'] = False


        # step-wise select most probable shp projectfile
        for (provincie,project),tbl in masktbl.groupby(['provincie','project']):

            if len(tbl[tbl['isname']])==1: 
                # only one file named 'vlakken'
                idx = tbl[tbl['isname']].index[0]
            elif len(tbl[tbl['isname']&tbl['inprj']])==1:
                # only one file vlakken in projectfolder
                idx = tbl[tbl['isname']&tbl['inprj']].index[0]
            elif len(tbl[tbl['likename']])==1:
                # only one file with name like vlakken
                idx = tbl[tbl['likename']].index[0]
            elif len(tbl[tbl['likename']&tbl['inprj']])==1:
                # only one file with name like vlakken in projectfolder
                idx = tbl[tbl['likename']&tbl['inprj']].index[0]
            else:
                idx = None

            if (not idx) and priority_filepaths:
            # At this point, idx is still None. No shp-projectfile has
            # been choosen based on automated selection.
            # Parameter shpfilepaths contains a list of filepaths of 
            # shapefiles. If any of these filepaths is present in 
            # column shppath, this file will be selected.
                mask = tbl[pathcol].isin(priority_filepaths)
                if len(tbl[mask])==1:
                    idx = tbl[mask].index[0]

            if idx is not None:
                masktbl.loc[idx,'masksel']=True

        self._shpfilter = masktbl

        # rename columns in table
        if colprefix is not None:
            filetbl = filetbl.rename(columns={
                'shpname': f'{colprefix}name',
                'shppath': f'{colprefix}path',
                })

        # create table of projects with selected project files
        shpsel = filetbl[masktbl['masksel']].reset_index(drop=True)
        shpsel = shpsel.sort_values(by=['provincie','project'])

        # create table of projects with to many ambiguous files to 
        # select a project file
        ambiguous = self._list_ambiguous(masktbl).reset_index(drop=True)
        ambiguous = ambiguous.sort_values(by=['provincie','project'])

        return shpsel, ambiguous

    def filter_tv2(self):
        """Return table with TV2 source directories and select criteria."""

        tvdir = self.list_tv2(relpaths=False)
        
        tvdir['path_depth'] = tvdir['tvdir'].apply(lambda x:len(os.path.normpath(x).split(os.sep)))
        tvdir['mask_tv'] = tvdir['tvdir'].str.upper().str.contains('TV_')
        tvdir['mask_tag'] = tvdir['tvdir'].str.lower().str.contains('kievit|cmsi|oud|wateropn',regex=True)
        tvdir['selected']=False

        ambiguous = []
        for (prv,prj),tbl in tvdir.groupby(by=['provincie','project']):

            if len(tbl)==1:
                # just one directory with turboveg files

                # get name of selected directory
                icol = tbl.columns.get_loc('tvdir')
                seldir = tbl.iloc[0,icol]

            elif len(tbl[tbl['mask_tv']])==1:
                # select directories starting with _TV

                # get name of selected directory
                icol = tbl.columns.get_loc('tvdir')
                seldir = tbl[tbl['mask_tv']].iloc[0,icol]

            elif len(tbl[tbl['mask_tv']&~tbl['mask_tag']])==1:
                # just one directory after discarding directories with
                # specific tags in pathname

                # get name of selected directory
                icol = tbl.columns.get_loc('tvdir')
                seldir = tbl[tbl['mask_tv']&~tbl['mask_tag']].iloc[0,icol]

            elif len(tbl[tbl['path_depth']==tbl['path_depth'].min()])==1:
                # there is one directory that is on a hogher level in 
                # the directory tree than all the other directories

                # get name of selected directory
                icol = tbl.columns.get_loc('tvdir')
                seldir = tbl[tbl['path_depth']==tbl['path_depth'].min()].iloc[0,icol]

            else:
                # Last resort: just pick the first directory

                # get name of selected directory
                icol = tbl.columns.get_loc('tvdir')
                seldir = tbl.iloc[0,icol]

                warnings.warn((f'No single directory with Turboveg '
                    f'files found for {prv} {prj}. Just picked the '
                    f' first directory in the list.'))
                ambiguous.append(tbl)

            # set selected row to True
            idx = tvdir[tvdir['tvdir']==seldir].index.values[0]
            tvdir.loc[idx,'selected']=True

        #if relpaths: #remove root from paths
        #    tvdir[fpathcol] = self._relativepaths(tbl[fpathcol])

        # list of DataFrames to DataFrame
        if not ambiguous:
            ambiguous = DataFrame()
        else:
            ambiguous = pd.concat(ambiguous)

        return tvdir, ambiguous



    def list_projectfiles(self,relpaths=True,discardtags=None,default_tags=True,
        mdbpaths=None,polypaths=None,linepaths=None,pointpaths=None):
        """
        Return table with all projects and filepaths found

        Parameters
        ----------
        relpaths : bool, default True
            Filepaths relative to root directory.
        discardtags : list of string, optional
            Mdb filepaths with these keywords will be ignored.
        default_tags : bool, default False
            Use standardtags for ignoring files. Value of discardtags
            is ignored.
        mdbpaths : list of string, optional
            Mdb filepaths in this list are selected as projectfiles.
        shppaths : list of strings, optional
            Filepaths equal to a string in this list will be selected
            as project shapefile.   
           
        """

        if default_tags:
            discardtags = self._discardtags

        # find mdb files
        mdblist = self.list_files(filetype='mdb')
        mdbsel,ambigous = self.filter_mdbfiles(mdblist,
            discardtags=discardtags,priority_filepaths=mdbpaths)
        mdbsel = mdbsel.set_index(keys=['provincie','project'],
            verify_integrity=True)

        ambiprj = len(set(ambigous['project'].values))
        if ambiprj!=0:
            warnings.warn((f'{ambiprj} projects with multiple mdb-files '
                f'have been dropped from projectstable. Use '
                f'method filter_mdbfiles to get a table of candidate '
                f'files.'))

        # table of all available shapefiles
        shp = self.list_files(filetype='shp')
        
        # find polygon shapefiles
        polysel,ambigous = self.filter_shapefiles(shp,shptype='polygon',
            priority_filepaths=polypaths)
        polysel = polysel.set_index(
                keys=['provincie','project'],verify_integrity=True)

        ambiprj = len(set(ambigous['project'].values))
        if ambiprj!=0:
            warnings.warn((f'{ambiprj} projects with multiple polygonfiles '
                f'have been dropped from projectstable. Use '
                f'method filter_shpfiles to get a table of candidate '
                f'files.'))

        # find line shapefiles
        linesel,ambigous = self.filter_shapefiles(shp,shptype='line',
            priority_filepaths=linepaths)
        linesel = linesel.set_index(
                keys=['provincie','project'],verify_integrity=True)

        ambiprj = len(set(ambigous['project'].values))
        if ambiprj!=0:
            warnings.warn((f'{ambiprj} projects with multiple linefiles '
                f'have been dropped from projectstable. Use '
                f'method filter_shpfiles to get a table of candidate '
                f'files.'))

        # list of TV2 directories
        tvdir, tvambi = self.filter_tv2()
        if not tvambi.empty:
            warnings.warn((f'{ambiprj} projects with multiple TV2 directories '
                f'found. Use '
                f'method filter_tv2 to get a table of candidate '
                f'files.'))
        tvsel = tvdir[tvdir['selected']==True].set_index(['provincie','project'])
        tvsel = tvsel[['tvdir']].copy()
        if relpaths: #remove root from paths
            tvsel['tvdir'] = self._relativepaths(tvsel['tvdir'])
            #tvambi['tvdir'] = self._relativepaths(tvambi['tvdir'])

        # merge file tables with base project table
        baseprj = self.list_projects()
        baseprj = baseprj[['year']].copy()

        prj = pd.merge(baseprj,mdbsel,left_index=True,right_index=True,
            how='left',suffixes=[None,'_from_mdb'],validate='one_to_one')
        prj = pd.merge(prj,polysel,left_index=True,right_index=True,
            how='left',suffixes=[None,'_from_poly'],validate='one_to_one')
        prj = pd.merge(prj,linesel,left_index=True,right_index=True,
            how='left',suffixes=[None,'_from_line'],validate='one_to_one')
        prj = pd.merge(prj,tvsel,left_index=True,right_index=True,
            how='left',suffixes=[None,'_from_tv2'],validate='one_to_one')

        # drop duplicaste columns names
        colnames = []
        for tag in ['_from_mdb','_from_poly','_from_line','_from_tv2',]:
            colnames = colnames + [x for x in prj.columns if tag in x]
        prj = prj.drop(columns=colnames)

        # relative paths or absolute paths
        if not relpaths:
            pathcols = [x for x in prj.columns if 'path' in x]
            for col in pathcols:
                prj[col]=self._absolutepaths(prj[col])

        return prj



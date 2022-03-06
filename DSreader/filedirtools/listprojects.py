
import os
import re
import warnings
import numpy as np
from pandas import Series, DataFrame
import pandas as pd
import difflib


class ListProjects:
    """
    Find filepaths to ESRI shapefiles and Microsoft Acces database files 
    for each projectfolder under given root directory.

    The method projectfiles_table() returns a table with all projects 
    and the corresponding shapefile and access madfile, if they were 
    found. This table is the main result for this class, all the other 
    methods are merely preparations and checks.

    Methods
    -------
    list_projects
        Return table of project directories under root.
    list_files
        Return table with all files of given filetype under root.
    projectfiles_counts
        Return table of file counts by project for given filtetype.
    filter_mdbfiles
        Return table with project mdbfiles.
    filter_shapefiles
        Return table with project shapefiles.
    projectfiles_table
        Return table with all projects and filepaths found.

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

    _discardtags = ['conversion','ConversionPGB','catl','ctl','soorten','kopie','test',
        'kievit','oud','oude','database','db1','test','fout','themas','florakartering',
        'flora','toestand','backup','foutmelding',]

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
            raise TypeError(f'rootdir must be of type string not {type(rootdir)}')

        if not os.path.isdir(rootdir):
            raise TypeError(f'{rootdir} is not a valid directory name.')

        self._rootdir = rootdir
        self._relpaths = relpaths
        self._projects = None

    def __repr__(self):

        nprj=0
        if self._projects:
            nprj = len(self._projects)
        return (f'{nprj} projects')

    def _relativepaths(self,column):
        """Replace absolute path with path relative to root"""
        newcolumn = column.apply(lambda x:'..\\'+x.removeprefix(
            self._rootdir) if not pd.isnull(x) else x)
        return newcolumn

    def _absolutepaths(self,column):
        """Replace path relative to root with absolute path"""
        newcolumn = column.apply(
                lambda x:os.path.join(self._rootdir,x.lstrip('..\\'))
                if not pd.isnull(x) else np.nan
                )
        return newcolumn

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
            mask = tbl[fpathcol].str.endswith(f'{filetype}')
            tbl = tbl[mask].copy()

        if relpaths: #remove root from paths
            tbl[fpathcol] = self._relativepaths(tbl[fpathcol])

        return tbl


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
            return None

        if colname not in filetbl.columns:
            warnings.warn(f'{colname} not in filetbl')
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
        tblist = []
        for (provincie,project),tbl in masktbl.groupby(['provincie','project']):
            if not tbl['masksel'].any():
                tblist.append(tbl)
        if tblist:
            ambiguous = pd.concat(tblist)
        else:
            ambiguous = DataFrame(columns=masktbl.columns)
        return ambiguous

    def filter_mdbfiles(self,filetbl,discardtags=None,default_tags=False,priority_filepaths=None):
        """
        Return table with mdbfiles by project

        Parameters
        ----------
        filetbl : pd.DataFrame
            Table with mdb filepaths as returned by list_files() method.
        discardtags : list of string, optional
            Mdb filepaths with these keywords will be ignored.
        default_tags : bool, default False
            Use standardtags for ignoring files. Value of discardtags
            will be ignored.
        priority_filepaths : list of string, optional
            Mdb filepaths in this list are selected as projectfiles.

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
            lowertags = [x.lower() for x in discardtags]
            mask_fpath = filetbl['mdbpath'].str.lower().str.contains(
                '|'.join(lowertags),na=False)
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
                # only one mdbfile found
                idx = tbl.index[0]
            elif len(tbl[tbl['maskprj']])==1: 
                # only one mdb in prjdir
                idx = tbl[tbl['maskprj']].index[0]
            elif len(tbl[tbl['maskprj']&tbl['maskfpath']])==1:
                # only one mdb in prjdir after discarding unlikely 
                # files by pathname
                idx = tbl[tbl['maskprj']&tbl['maskfpath']].index[0]
            elif len(tbl[tbl['maskfpath']])==1:
                # only one file at all after masking unlikely files
                # by pathname
                idx = tbl[tbl['maskfpath']].index[0]
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
                masktbl.loc[idx,'masksel']=True

        # create table of projects with selected mdb filesd
        mdbtbl = filetbl[masktbl['masksel']]

        # create table of projects with to many ambiguous files to 
        # select a project mdb file
        ambiguous = self._list_ambiguous(masktbl)

        return mdbtbl,ambiguous


    def filter_shapefiles(self,filetbl,priority_filepaths=None):
        """
        Return table with project shapefiles

        Parameters
        ----------
        filetbl : pd.DataFrame
            Table with mdb filepaths as returned by list_files() method.
        priority_filepaths : list of strings, optional
            Filepaths equal to a string in this list will be selected
            as project shapefile

        Notes
        -----
        Valid shapefiles are called 'vlakken', 'Vlakken', or they have
        the keyword 'vlak' somewhere in their filename.
        """

        # masks for filename 'vlakken'
        namecol='shpname'
        isname = filetbl[namecol].str.lower()=='vlakken.shp'
        likename = filetbl[namecol].str.lower().str.contains('vlak')

        # mask for file in project directory
        mask_prjdir = self._file_in_projectdir(filetbl,pathcol='shppath')

        # masktbl is a temporary copy of filetbl with columns for masking
        # mask_fname and mask_prjdir are series with the same index
        # as DataFrame filetbl.
        masktbl = filetbl.copy()
        masktbl['isname'] = isname
        masktbl['likename'] = likename
        masktbl['inprj'] = mask_prjdir
        masktbl['masksel'] = False

        # step-wise select most probable shp projectfile
        for (provincie,project),tbl in masktbl.groupby(['provincie','project']):

            if len(tbl[tbl['isname']])==1: 
                # only one file vlakken
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
                mask = tbl['shppath'].isin(priority_filepaths)
                if len(tbl[mask])==1:
                    idx = tbl[mask].index[0]

            if idx is not None:
                masktbl.loc[idx,'masksel']=True

        self._shpfilter = masktbl

        # create table of projects with selected mdb filesd
        shptbl = filetbl[masktbl['masksel']]

        # create table of projects with to many ambiguous files to 
        # select a project mdb file
        ambiguous = self._list_ambiguous(masktbl)

        return shptbl, ambiguous


    def projectfiles_table(self,relpaths=True,discardtags=None,default_tags=True,
        mdbpaths=None,shppaths=None):
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

        # projecttable
        prj = self.list_projects()
        prj = prj[['year']].copy()

        # find shapefiles
        shp = self.list_files(filetype='shp')
        shpsel,_ = self.filter_shapefiles(shp,
            priority_filepaths=shppaths)
        shpsel = shpsel.set_index(
                keys=['provincie','project'],verify_integrity=True)

        mdblist = self.list_files(filetype='mdb')
        mdbsel,_ = self.filter_mdbfiles(mdblist,
            discardtags=discardtags,priority_filepaths=mdbpaths)
        mdbsel = mdbsel.set_index(keys=['provincie','project'],
            verify_integrity=True)

        # merge tables with mdb and shp files
        prj = pd.merge(prj,shpsel,left_index=True,right_index=True,
            how='left',suffixes=[None,'_from_shp'],validate='one_to_one')
        prj = pd.merge(prj,mdbsel,left_index=True,right_index=True,
            how='left',suffixes=[None,'_from_mdb'],validate='one_to_one')

        # drop duplicaste columns names
        dup_shp = [x for x in prj.columns if '_from_shp' in x]
        dup_mdb = [x for x in prj.columns if '_from_mdb' in x]
        duplicates = dup_mdb+dup_shp
        prj = prj.drop(columns=duplicates)

        # relative paths or absolute paths
        if not relpaths:
            pathcols = [x for x in prj.columns if 'path' in x]
            for col in pathcols:
                prj[col]=self._absolutepaths(prj[col])

        return prj



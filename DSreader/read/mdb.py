
import os
import collections
import warnings
from pandas import Series, DataFrame
import pandas as pd
import pyodbc

class Mdb:
    """
    Read tables from a Microsoft Access mdb file

    Methods
    -------
    tablenames
        Return tablenames as list
    table
        Return specific table as pd.DataFrame
    all_tables
        Return all tables as OrderedDict of Dataframes
    """

    ##_mdbopen_errors = []

    def __init__(self,mdbpath):
        """
        Open Microsoft Access mdb-file

        Parameters
        ----------
        mdbpath : str
            valid filepath to .mdb file
    `   """

        if not isinstance(mdbpath,str):
            raise TypeError(f'mdbpath must be of type string not {type(mdbpath)}')

        if not os.path.isfile(mdbpath):
            raise TypeError(f'{mdbpath} is not a valid filepath.')

        # connect to mdb file
        self._mdbpath = mdbpath
        self._cur = self._connect()

    def __repr__(self):
        """Return string representation of Mdb instance."""
        fname = os.path.basename(self._mdbpath)
        mdbname = os.path.splitext(fname)[0]
        number_of_tables = len(self) #.tablenames)
        return f'{mdbname} ({number_of_tables})'

    def __len__(self):
        """Return number of tables."""
        return len(self.tablenames)

    def _connect(self):

        self._mdbopen_error = None
        self._conn = None
        self._cur = None
        try:
            self._conn_str = (
                r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
                r'DBQ='+self._mdbpath+r';'
                )
            self._conn = pyodbc.connect(self._conn_str)
            self._cur = self._conn.cursor()

        except pyodbc.Error as err:
            self._err = err
            #print(self._err.args[0])
            self._mdbopen_error = {
                'errtype':self._err.__class__,
                'errmsg':repr(self._err),
                'fpath':self._mdbpath,
                }
            warnings.warn((f'Could not open .mdb file {self._mdbpath} '
             f'because of an {self._mdbopen_error["errtype"]} error. '
             f'Full error message: {self._mdbopen_error["errmsg"]}.'))

            # Closing cursor and connection prevents 
            # "[ODBC Microsoft Access Driver] Too many client tasks"
            # error.
            if self._cur is not None:
                self._cur.close()
            if self._conn is not None:
                self._conn.close()

        return self._cur

    def _cursor(self):
        """Return cursor, returns None if file could not be opened"""
        return self._cur

    @property
    def read_error(self):
        """
        Return dict with readfile error message. Returns None if
        no errers occurred.
        """
        return self._mdbopen_error

    @property
    def tablenames(self):
        """Return list of tablenames in database"""
        tblnames = []
        if self._cur is not None:
            for table_info in self._cur.tables(tableType='TABLE'):
                tblnames.append(table_info.table_name)
        return tblnames

    def get_table(self,tblname):
        """Return specified table as pd.DataFrame"""
        qrstr = f'select * from [{tblname}]'
        self._cur.execute(qrstr)
        colnames = [column[0] for column in self._cur.description]

        data = []
        for row in self._cur.fetchall():
            data.append(list(row))

        table = DataFrame(data, columns=colnames)
        return table

    @property
    def all_tables(self):
        """Return OrderedDict with all tables"""
        catkeys = [x for x in self.tablenames if not x.startswith('GDB_')]
        cat = collections.OrderedDict()
        for key in catkeys:
            cat[key] = self.get_table(key)
        return cat

    @property
    def filepath(self):
        """Return path to mdb sourcefile."""
        return self._mdbpath




from pandas import Series,DataFrame
import pandas as pd

def write_to_excel(filename,data):
    """Write (mulitple) dataframes to Excel.
    
    Parameters
    ----------
    filename : str
        Valid path name for Excelfile to wrtie.
    data : tuple | list of tuples
        (dataframe,sheet_name)
    """


    def write_excel_sheet(writer,df,sheet_name):
        """Write dataframe to Excelsheet and autoadjust columns width.
        
        Parameters
        ----------
        writer : pd.ExcelWrtier
            ExcelWriter object to wrtie sheet to.
        df : DataFrame | Series
            DataFrame or Series to wrtie on sheet.
        sheet_name : str
            Excel sheet name.

        """

        # write data
        df.to_excel(writer,sheet_name=sheet_name, index=True)

        # set index columns width
        for icol,index_name in enumerate(df.index.names):
            vals = df.index.get_level_values(icol)
            val_len_max = max([len(x) for x in vals])               
            column_width = max(len(index_name),val_len_max)
            writer.sheets[sheet_name].set_column(icol,icol,column_width)

        # set value columns width
        def get_col_width(column):
            maxlenvalues = column.astype(str).map(len).max()
            lencolname = len(column.name)
            column_width = max(maxlenvalues,lencolname)
            return column_width

        colstartpos = len(df.index.names)
        if isinstance(df,Series):
            col_idx = colstartpos + 0
            column_width = get_col_width(df)
            writer.sheets[sheet_name].set_column(col_idx,col_idx,column_width)
        else:
            for colname in list(df):
                column_width = get_col_width(df[colname])
                col_idx = colstartpos + df.columns.get_loc(colname)
                writer.sheets[sheet_name].set_column(col_idx, col_idx, column_width)

        #return writer

    
    with pd.ExcelWriter(filename) as writer:
        for df,sheet_name in data:
            write_excel_sheet(writer,df,sheet_name)



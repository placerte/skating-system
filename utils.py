import pandas as pd
from rich.table import Table

def data_frame_to_rich_table(dataframe: pd.DataFrame)->Table:
    rich_table: Table = Table(title="Score Table")
    
    rich_table.add_column("Comp. \\ Judges")
    for column in dataframe.columns:
        rich_table.add_column(column)

    for index, row in dataframe.iterrows():
        values=[]
        for column in dataframe.columns:
            value = row[column]
            if pd.notna(value):
                values.append(str(value))
            else:
                values.append("")
        rich_table.add_row(str(index), *values)

    return rich_table

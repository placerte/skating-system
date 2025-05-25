# In this code I lay out the basics of a scoring sheet

from rich.table import Table
from rich.console import Console
import pandas as pd
from utils import data_frame_to_rich_table

judges: list[str] = ["Judge 1", "Judge 2", "Judge 3", "Judge 4", "Judge 5" ]
competitors: list[str] = ["Joe", "Anna", "Mary", "John", "Paul" ]

df_score_sheet: pd.DataFrame = pd.DataFrame(index=competitors, columns=judges) # type: ignore

ctr: int = 1

for judge in judges:
    for competitor in competitors:
        df_score_sheet.loc[competitor,judge] = ctr
        ctr +=1

console: Console = Console()
score_sheet: Table = Table()
score_sheet = data_frame_to_rich_table(df_score_sheet)

console.print(score_sheet)

"""
score_sheet.add_column(header="Participant")
score_sheet.add_column(header="Judge 1")
score_sheet.add_column(header="Judge 2")
score_sheet.add_column(header="Judge 3")
score_sheet.add_column(header="Judge 4")
score_sheet.add_column(header="Judge 5")

score_sheet.add_row("Joe","1","2","3","4","5")

console.print(score_sheet)
"""

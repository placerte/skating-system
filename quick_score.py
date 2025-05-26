# In this code I lay out the basics of a scoring sheet

from rich.table import Table
from rich.console import Console
import pandas as pd
from utils import data_frame_to_rich_table
from models import Competition, Competitor, Judge

lindy_mm_adv: Competition = Competition()
lindy_mm_adv.name = "Lindy - Mix and Match - Advance"

lindy_mm_adv.set_judges(["Judge 1", "Judge 2", "Judge 3", "Judge 4", "Judge 5" ])
lindy_mm_adv.set_competitors(["Joe", "Anna", "Mary", "John", "Paul" ])

lindy_mm_adv.print_score_sheet()

ctr: int = 1
"""
for judge in judges:
    for competitor in competitors:
        df_score_sheet.loc[competitor,judge] = ctr
        ctr +=1

console: Console = Console()
score_sheet: Table = Table()
score_sheet = data_frame_to_rich_table(df_score_sheet)

console.print(score_sheet)
"""

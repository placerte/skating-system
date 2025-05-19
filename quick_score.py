# In this code I lay out the basics of a scoring sheet


from rich.table import Table
from rich.console import Console

console: Console = Console()
score_sheet: Table = Table()

score_sheet.add_column(header="Participant")
score_sheet.add_column(header="Judge 1")
score_sheet.add_column(header="Judge 2")
score_sheet.add_column(header="Judge 3")
score_sheet.add_column(header="Judge 4")
score_sheet.add_column(header="Judge 5")

score_sheet.add_row("Joe","1","2","3","4","5")

console.print(score_sheet)

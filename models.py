from dataclasses import dataclass, field
from typing import Optional
import pandas as pd
from rich.console import Console
from rich.table import Table

@dataclass
class Competitor():
    names: str = ""
    number: int = 0

@dataclass
class Judge():
    name: str = ""
    identifier: str = ""

@dataclass
class Score():
    judge: Optional[Judge] = field(default=None)
    competitor: Optional[Competitor] = field(default=None)
    rank: int = 0
@dataclass

class Competition():
    name: str = ""
    competitors: list[Competitor] = field(default_factory=list)
    judges: list[Judge] = field(default_factory=list)
    scores: list[Score] = field(default_factory=list)

    def get_all_scores_of_competitor(self, competitor: Competitor)-> list[int]:
        scores_int: list[int] = []
        score: Score
        
        for score in self.scores:
            if score.competitor == competitor:
                scores_int.append(score.rank)

        return scores_int

    def get_score_table(self) -> pd.DataFrame:
        """
        Creates a score table as a Pandas DataFrame.
        The DataFrame has a "Competitor" column and one column per judge,
        where each cell contains the rank given by that judge to the competitor.
        If a score is missing, pd.NA is used.
        """
        data = []
        for competitor in self.competitors:
            row = {"Competitor": competitor.names}
            for judge in self.judges:
                score_value = next(
                    (score.rank for score in self.scores
                     if score.competitor == competitor and score.judge == judge),
                    pd.NA
                )
                row[judge.name] = score_value
            data.append(row)
        df = pd.DataFrame(data)
        return df

    def print_score_table(self):
        """
        Prints the score table using Rich's Console and Table.
        """
        df = self.get_score_table()
        # Create a Rich Table with a title
        table = Table(title="Score Table")
        
        # Add columns to the table based on the DataFrame's columns
        for column in df.columns:
            table.add_column(column, justify="center", style="cyan", no_wrap=True)
        
        # Add rows from the DataFrame
        for _, row in df.iterrows():
            table.add_row(*(str(cell) for cell in row))
        
        console = Console()
        console.print(table)
    def get_sum_of_ranks_of_competitor(self, competitor: Competitor)-> int:
        scores_int: list[int] = self.get_all_scores_of_competitor(competitor)
        return sum(scores_int)

    def validate_scores(self):
        #make sure there all scores are covered (all judges judged all competitors)
        #make sur there is no double scores (a judge scoring twice or more the same competitor)
        raise NotImplementedError("To be implemented")



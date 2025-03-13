from dataclasses import dataclass, field
from typing import Optional
import pandas as pd
from rich.console import Console
from rich.table import Table as RichTable

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Integer, String, Column
from sqlalchemy import Table as SQLTable

# declaring the base classe of sql alchemy
class SQLBase(DeclarativeBase):
    pass

# Many-to-many association tables
at_competitions_competitors: SQLTable = SQLTable(
        "at_competitions_competitors",
        SQLBase.metadata,
        Column("competition_id", ForeignKey("competitions.id"), primary_key=True),
        Column("competitor_id", ForeignKey("competitors.id"), primary_key=True)
        )

class Event(SQLBase):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    
    participants: Mapped[list["Participant"]] = relationship("Participant")
    competitors: Mapped[list["Competitor"]] =  relationship("Competitor", back_populates="event")
    judges: Mapped[list["Judge"]] = relationship("Judge")
    competitions: Mapped[list["Competition"]] = relationship("Competition")

class Participant(SQLBase):
    __tablename__ = "participants"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False)

    def __init__(self, name: str):
        self.name = name

class Competitor(SQLBase):
    __tablename__ = "competitors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id"),nullable=False)
    participant_id: Mapped[int] = mapped_column(ForeignKey("participants.id"), nullable=False)
    number: Mapped[int] = mapped_column(Integer, nullable=False)

    event: Mapped["Event"] = relationship("Event", back_populates="competitors")
    participant: Mapped["Participant"] = relationship("Participant")
    
    # for the name just parse the participant name
    @property
    def name(self)->str:
        return self.participant.name


class Judge(SQLBase):
    __tablename__ = "judges"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id"), nullable=False)
    participant_id: Mapped[int]  = mapped_column(ForeignKey("participants.id"), nullable=False)
    identifier: Mapped[str] = mapped_column(String, nullable=False)

    event: Mapped["Event"] = relationship("Event", back_populates="judges")
    participant: Mapped["Participant"] = relationship("Participant")

    #for the name just parse the participant name
    @property
    def name(self)->str:
        return self.participant.name

class Score(SQLBase):
    __tablename__ = "scores"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    judge_id: Mapped[int] = mapped_column(ForeignKey("judges.id"),  nullable=False)
    competitor_id: Mapped[int] = mapped_column(ForeignKey("competitors.id"), nullable=False)
    competition_id: Mapped[int] = mapped_column(ForeignKey("competitions.id"),nullable=False)
    rank: Mapped[int] = mapped_column(Integer, nullable=False)

    judge: Mapped["Judge"] = relationship("Judge")
    competitor: Mapped["Competitor"] = relationship("Competitor")
    competition: Mapped["Competition"] = relationship("Competition")

class Competition(SQLBase):
    __tablename__ = "competitions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    ###RENDU ICI considérer relations many-to-many et association table###
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
        table = RichTable(title="Score Table")
        
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


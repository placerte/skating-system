# Skating System App - Diagrams

## Skating System Classes

```plantuml
@startuml
  !theme reddress-darkgreen
  skinparam backgroundcolor transparent
  skinparam dpi 200
  skinparam defaultFontSize 16


  class Event {
    -id: str
    +name: str
    +competitions: list[Competition]
    +participants: list[Participant]
    +competitors: list[Competitor]
    +competitor_groups: list[CompetitorGroup]
    +judges(): list[Participant]
  }

  class Participant {
    -id: str
    -obsolete: bool
    +number: int
    +first_name: str
    +last_name: str
    +email: str
    +full_name(): str
  }

  class Competition {
    -id: str
    -obsolete: bool
    +name: str
    -judges_ids: list[str]
    -competitor_groups_ids: list[str]
    +scores: list[Score]
  }

  class Score {
    -id: str
    -obsolete: bool
    +value: int
    -competitor_group_id: str
    -judge_id: str
  }

  class Competitor {
    -id: str
    -obsolete: bool
    -participant_id: str
    +role: str
  }

  class CompetitorGroup {
    -id: str
    -obsolete: bool
    +name: str
    -competitor_ids: list[str]
  }

  Event --> Participant
  Event --> Competition
  Event --> CompetitorGroup
  Event --> Competitor
  Competition --> Score

@enduml
```

Why this structure?:

- to simplify first persistence scheme (aggregated json file)
- There is a lot of possible reusability for instance:
  - The same participant could be a competitor for a certain competition as a *leader* and in another competition as a *follower*.
  - The same competitor could be a lead in a duo (competitor group) and also a lead in a troup (another competitor group)
  - A competitor group like a troup could enter multiple competitions.
- The only really direct child-parent relation would be scores and competitions. Where scores do not really make sense outside a competition, but most certainly should not be reused.

# Specification Tracking

This table tracks requirements from `docs/specs.md` and their implementation
status. Keep it updated as work lands.

Legend for Status: planned, in-progress, implemented, deferred, dropped.

| Spec ID | Topic | Summary | Implementation | Status | Notes |
| --- | --- | --- | --- | --- | --- |
| GEN-1 | Scope | Skating System ranking app | N/A | planned | |
| GEN-2 | Scope | Offline-first, one Event per file | persistence/json_repo.py | planned | |
| GEN-3 | Scope | Fast, resilient, transparent | ui, services | planned | |
| GEN-4 | Scope | Use "rank" not "score" | domain, ui | planned | |
| GEN-5 | Scope | PoC scope: clarity over completeness | N/A | planned | |
| VOC-1 | Vocabulary | Define Event | docs/specs.md | planned | |
| VOC-2 | Vocabulary | Define Participant | docs/specs.md | planned | |
| VOC-3 | Vocabulary | Define Entry | docs/specs.md | planned | |
| VOC-4 | Vocabulary | Define Judge | docs/specs.md | planned | |
| VOC-5 | Vocabulary | Define Rank | docs/specs.md | planned | |
| VOC-6 | Vocabulary | Define Result | docs/specs.md | planned | |
| ID-1 | Identity | UUID is true identity | domain/models.py | planned | |
| ID-2 | Identity | Names/numbers not identity | domain/models.py | planned | |
| ID-3 | Identity | New UUID on recreate | services/event_service.py | planned | |
| NUM-1 | Identity | Participant display number | domain/models.py | planned | |
| NUM-2 | Identity | Numbers not permanent IDs | domain/models.py | planned | |
| NUM-3 | Identity | New number on recreate | services/event_service.py | planned | |
| NUM-4 | Identity | Numbers not reused | services/event_service.py | planned | |
| NUM-5 | Identity | Participant numbers unique | domain/validate.py | planned | |
| NUM-6 | Identity | Auto-assign max + 1 | services/event_service.py | planned | |
| NUM-7 | Identity | Numbers start at >= 100 | services/event_service.py | planned | |
| NUM-8 | Identity | Manual number edits disabled | ui/modals/participant_form.py | planned | |
| OBS-1 | Lifecycle | Avoid delete | domain/models.py | planned | |
| OBS-2 | Lifecycle | Use is_obsolete | domain/models.py | planned | |
| OBS-3 | Lifecycle | Hide obsolete by default | ui | planned | |
| OBS-4 | Lifecycle | Obsolete stays in JSON | persistence/json_repo.py | planned | |
| OBS-5 | Lifecycle | UI toggle show obsolete | ui | planned | |
| TIE-1 | Ranking | Ties valid | domain | planned | |
| TIE-2 | Ranking | Support ties conceptually | services | planned | |
| TIE-3 | Ranking | MVP cannot assume no ties | domain | planned | |
| TIE-4 | Ranking | Multiple entries can share rank | services | planned | |
| EVT-1 | Data model | Event is root object | domain/models.py | planned | |
| EVT-2 | Data model | Event fields id, name | domain/models.py | planned | |
| EVT-3 | Data model | Event participants list | domain/models.py | planned | |
| EVT-4 | Data model | Event entries list | domain/models.py | planned | |
| EVT-5 | Data model | Event competitions list | domain/models.py | planned | |
| EVT-6 | Data model | Event optional fields | domain/models.py | planned | |
| PAR-1 | Data model | Participant is person | domain/models.py | planned | |
| PAR-2 | Data model | Participant fields | domain/models.py | planned | |
| PAR-3 | Data model | Participant competitor role | domain/models.py | planned | |
| PAR-4 | Data model | Participant judge role | domain/models.py | planned | |
| PAR-5 | Data model | Judge not separate entity | domain/models.py | planned | |
| ENT-1 | Data model | Entry competes | domain/models.py | planned | |
| ENT-2 | Data model | Entry fields | domain/models.py | planned | |
| MEM-1 | Data model | EntryMember fields | domain/models.py | planned | |
| MEM-2 | Data model | EntryMember for clarity | domain/models.py | planned | |
| MEM-3 | Data model | EntryMember mostly UI-invisible | ui | planned | |
| MEM-4 | Data model | Roles are free-form strings | domain/models.py | planned | |
| MEM-5 | Data model | Roles optional or Other | domain/models.py | planned | |
| ENT-3 | Data model | Entries reusable | domain/models.py | planned | |
| ENT-4 | Data model | Entries created globally | ui/screens/entries.py | planned | |
| ENT-5 | Data model | Entries created inline | ui/modals/entry_form.py | planned | |
| COM-1 | Data model | Competition is ranked instance | domain/models.py | planned | |
| COM-2 | Data model | Competition fields id, name | domain/models.py | planned | |
| COM-3 | Data model | Competition judge_ids | domain/models.py | planned | |
| COM-4 | Data model | Competition entry_ids | domain/models.py | planned | |
| COM-5 | Data model | Competition rank_marks | domain/models.py | planned | |
| COM-6 | Data model | Optional results | domain/models.py | planned | |
| COM-7 | Data model | Judges from participants | services/event_service.py | planned | |
| COM-8 | Data model | Participant can judge and compete | services/event_service.py | planned | |
| RM-1 | Data model | RankMark meaning | domain/models.py | planned | |
| RM-2 | Data model | RankMark fields | domain/models.py | planned | |
| RM-3 | Data model | RankMark optional notes | domain/models.py | planned | |
| RM-4 | Data model | Unique judge/entry pair | domain/validate.py | planned | |
| RES-1 | Data model | Results include ties | services | planned | |
| RES-2 | Data model | Rule trace future | services | planned | |
| RES-3 | Data model | Display avg rank to 2 decimals | ui/screens/ranking.py | planned | |
| RES-4 | Data model | Ties ordered by entry label | ui/screens/ranking.py | planned | |
| PST-1 | Persistence | One event per JSON | persistence/json_repo.py | planned | |
| PST-2 | Persistence | JSON full event | persistence/json_repo.py | planned | |
| PST-3 | Persistence | Schema/app version | persistence/schema.py | planned | |
| PST-4 | Persistence | Migration for older versions | persistence/schema.py | planned | |
| PST-5 | Persistence | Round-trip safety | persistence/json_repo.py | planned | |
| PST-6 | Persistence | UUID references | persistence/json_repo.py | planned | |
| PST-7 | Persistence | No silent data loss | persistence/json_repo.py | planned | |
| PST-8 | Persistence | Preserve unknown fields | persistence/json_repo.py | planned | |
| PST-9 | Persistence | Warn on schema mismatch | persistence/schema.py | planned | |
| VAL-1 | Validation | Warnings on load | domain/validate.py | planned | |
| VAL-2 | Validation | Detect duplicate participant numbers | domain/validate.py | planned | |
| VAL-3 | Validation | Detect missing referenced IDs | domain/validate.py | planned | |
| VAL-4 | Validation | Detect invalid rank values | domain/validate.py | planned | |
| VAL-5 | Validation | Detect duplicate rank marks | domain/validate.py | planned | |
| VAL-6 | Validation | Required fields non-empty | domain/validate.py | planned | |
| VAL-7 | Validation | Entries must have members | domain/validate.py | planned | |
| VAL-8 | Validation | No duplicate entry members | domain/validate.py | planned | |
| VAL-9 | Validation | Rank range 1..entry_count | domain/validate.py | planned | |
| VAL-10 | Validation | Missing ranks allowed | ui/screens/ranking.py | planned | |
| VAL-11 | Validation | Missing ranks -> entry_count + 1 | services | planned | |
| VAL-12 | Validation | Participant numbers >= 100 | domain/validate.py | planned | |
| VAL-13 | Validation | Min judges/entries to compute | services | planned | |
| WFE-1 | Workflow | Create event | ui/screens/home.py | planned | |
| WFE-2 | Workflow | Save event | ui/screens/home.py | planned | |
| WFE-3 | Workflow | Open event | ui/screens/home.py | planned | |
| WFE-4 | Workflow | Save As | ui/screens/home.py | planned | |
| WFE-5 | Workflow | Warn unsaved changes | ui | planned | |
| WFE-6 | Workflow | Recoverable load error | ui, persistence | planned | |
| WFE-7 | Workflow | Default .json extension | ui, persistence | planned | |
| WFE-8 | Workflow | Default dir ~/skating-events | ui | planned | |
| WFE-9 | Workflow | Remember last event path | ui | planned | |
| WFE-10 | Workflow | Modal prompts for load/save/rename | ui | planned | |
| WFP-1 | Workflow | List participants | ui/screens/participants.py | planned | |
| WFP-2 | Workflow | Add or edit participants | ui/modals/participant_form.py | planned | |
| WFP-3 | Workflow | Obsolete or unobsolete participants | ui/screens/participants.py | planned | |
| WFP-4 | Workflow | Search participants | ui/screens/participants.py | planned | |
| WFP-5 | Workflow | Fuzzy case-insensitive search | ui/screens/participants.py | planned | |
| WFN-1 | Workflow | Create or edit entries | ui/screens/entries.py | planned | |
| WFN-2 | Workflow | Assign participants and roles | ui/modals/entry_form.py | planned | |
| WFN-3 | Workflow | Obsolete or unobsolete entries | ui/screens/entries.py | planned | |
| WFN-4 | Workflow | Search entries | ui/screens/entries.py | planned | |
| WFN-5 | Workflow | Fuzzy case-insensitive search | ui/screens/entries.py | planned | |
| WFC-1 | Workflow | Create competition | ui/screens/competitions.py | planned | |
| WFC-2 | Workflow | Select judges | ui/modals/competition_form.py | planned | |
| WFC-3 | Workflow | Select or create entries inline | ui/modals/competition_form.py | planned | |
| WFC-4 | Workflow | Enter ranks | ui/screens/ranking.py | planned | |
| WFC-5 | Workflow | Compute/view results | ui/screens/ranking.py | planned | |
| CAL-1 | Computation | PoC average rank | services | planned | |
| CAL-2 | Computation | Missing ranks use entry_count + 1 | services | planned | |
| CAL-3 | Computation | Mark results provisional | ui/screens/ranking.py | planned | |
| CAL-4 | Computation | Recompute on rank changes | ui/screens/ranking.py | planned | |
| UI-1 | UI | Keyboard-first | ui | planned | |
| UI-2 | UI | Fast navigation | ui | planned | |
| UI-3 | UI | No crashes on input | ui | planned | |
| UI-4 | UI | Validation in context | ui | planned | |
| UI-5 | UI | Show obsolete per-screen | ui | planned | |
| UI-6 | UI | Show obsolete default off | ui | planned | |
| UI-7 | UI | Solo entry display label | ui | planned | |
| UI-8 | UI | Named entry display label | ui | planned | |
| UI-9 | UI | Couple entry display label | ui | planned | |
| UI-10 | UI | Entry label decision order | ui | planned | |
| UI-11 | UI | Entry label fallback | ui | planned | |
| UI-12 | UI | Couple leader selection | ui | planned | |
| ENG-1 | Engine | Published ruleset | services | planned | |
| ENG-2 | Engine | Tie handling per rulebook | services | planned | |
| ENG-3 | Engine | Separate engine from UI/persistence | services | planned | |
| NG-1 | Non-goals | Multi-event databases | N/A | planned | |
| NG-2 | Non-goals | Cloud sync | N/A | planned | |
| NG-3 | Non-goals | Authentication | N/A | planned | |
| NG-4 | Non-goals | Printing/PDF exports | N/A | planned | |

from __future__ import annotations
from pathlib import Path
from persistence.json_repo import JsonEventRepo
from services.event_service import EventService
from ui.tk_app import TkApp

def main():
    repo = JsonEventRepo(file_path=Path("data/event.json"), default_title="Skating Event")
    svc = EventService(repo)
    app = TkApp(svc)
    app.mainloop()

if __name__ == "__main__":
    main()


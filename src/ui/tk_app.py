from __future__ import annotations
import tkinter as tk
from tkinter import ttk, messagebox
from services.event_service import EventService


class TkApp(tk.Tk):
    def __init__(self, svc: EventService):
        super().__init__()
        self.svc = svc
        self.title("Skating – Event Participants (POC)")
        self.geometry("520x420")

        style = ttk.Style()
        style.configure("Treeview", rowheight=28)  # default is ~20

        # Header: event title (editable)
        self.title_var = tk.StringVar(value=self.svc.get_event().title)
        title_row = ttk.Frame(self)
        title_row.pack(fill="x", padx=8, pady=(8, 4))
        ttk.Label(title_row, text="Event Title:").pack(side="left")
        self.title_entry = ttk.Entry(title_row, textvariable=self.title_var, width=40)
        self.title_entry.pack(side="left", padx=6)
        ttk.Button(title_row, text="Save", command=self._save_title).pack(side="left")

        # Participants list
        mid = ttk.Frame(self)
        mid.pack(fill="both", expand=True, padx=8, pady=8)
        self.tree = ttk.Treeview(
            mid,
            columns=("first_name", "last_name", "email"),
            show="headings",
            height=12,
        )
        self.tree.heading("first_name", text="First Name")
        self.tree.heading("last_name", text="Last Name")
        self.tree.heading("email", text="Email")
        self.tree.pack(side="left", fill="both", expand=True)
        sb = ttk.Scrollbar(mid, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=sb.set)
        sb.pack(side="right", fill="y")

        # Add form
        form = ttk.Frame(self)
        form.pack(fill="x", padx=8, pady=(0, 8))
        self.first_name_var = tk.StringVar()
        self.email_var = tk.StringVar()
        self.last_name_var = tk.StringVar()
        ttk.Label(form, text="First Name").grid(row=0, column=0, sticky="w")
        ttk.Entry(form, textvariable=self.first_name_var, width=22).grid(
            row=0, column=1, padx=6
        )
        ttk.Label(form, text="Last Name").grid(row=0, column=2, sticky="w")
        ttk.Entry(form, textvariable=self.last_name_var, width=22).grid(
            row=0, column=3, padx=6
        )
        ttk.Label(form, text="Email").grid(row=0, column=4, sticky="w")
        ttk.Entry(form, textvariable=self.email_var, width=22).grid(
            row=0, column=5, padx=6
        )
        ttk.Button(form, text="Add", command=self._add).grid(row=0, column=6, padx=6)

        # Delete button
        actions = ttk.Frame(self)
        actions.pack(fill="x", padx=8, pady=(0, 8))
        ttk.Button(actions, text="Remove Selected", command=self._remove_selected).pack(
            side="left"
        )

        self._refresh()

    def _refresh(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for p in self.svc.list_participants():
            self.tree.insert(
                "", "end", iid=p.id, values=(p.first_name, p.last_name, p.email)
            )

    def _add(self):
        try:
            p = self.svc.add_participant(
                self.first_name_var.get(),
                self.last_name_var.get(),
                self.email_var.get(),
            )
            self.tree.insert(
                "", "end", iid=p.id, values=(p.first_name, p.last_name, p.email)
            )
            self.first_name_var.set("")
            self.last_name_var.set("")
            self.email_var.set("")
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def _remove_selected(self):
        sel = self.tree.selection()
        if not sel:
            return
        for iid in sel:
            self.svc.remove_participant(iid)
        self._refresh()

    def _save_title(self):
        self.svc.rename_event(self.title_var.get())
        messagebox.showinfo("Saved", "Event title saved.")

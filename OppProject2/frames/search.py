import tkinter as tk
from tkinter import ttk

class SearchFrame(tk.Frame):
    def __init__(self,parent,controller):
        super().__init__(parent,bg="#f4f6f9")
        self.controller=controller

        tk.Label(self,text="Search Module",font=("Segoe UI",20),bg="#f4f6f9").pack(pady=10)

        frame=tk.Frame(self,bg="#f4f6f9")
        frame.pack(pady=10)
        tk.Label(frame,text="Search:",bg="#f4f6f9").grid(row=0,column=0,padx=5)
        self.entry=tk.Entry(frame,width=30)
        self.entry.grid(row=0,column=1,padx=5)
        tk.Button(frame,text="Search",bg="#2563eb",fg="white",command=self.perform_search).grid(row=0,column=2,padx=5)

        table_frame=tk.Frame(self,bg="#f4f6f9")
        table_frame.pack(fill="both",expand=True)
        self.table=ttk.Treeview(table_frame,columns=("ID","Name","Type","Info"),show="headings")
        self.table.pack(fill="both",expand=True)
        for col in ("ID","Name","Type","Info"):
            self.table.heading(col,text=col)
            self.table.column(col,width=150)

        tk.Button(self,text="Back to Dashboard",bg="#334155",fg="white",command=lambda:self.controller.show_frame("DashboardFrame")).pack(pady=10)

    def perform_search(self):
        keyword=self.entry.get()
        self.table.delete(*self.table.get_children())
        rows=self.controller.db.search_all(keyword)
        for row in rows:
            self.table.insert("", "end", values=row)

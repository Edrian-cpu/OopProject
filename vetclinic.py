import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date, datetime

DB_FILE = "vet_clinic.db"

# DATABASE 

class Database:
    def __init__(self, path=DB_FILE):
        self.conn = sqlite3.connect(path)
        self.conn.execute("PRAGMA foreign_keys = ON;")
        self.cur = self.conn.cursor()
        self._create_tables()

    def _create_tables(self):
        # create essential tables (kept readable & similar to your UML)
        self.cur.executescript("""
        CREATE TABLE IF NOT EXISTS Veterinarian (
            vetID INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            specialization TEXT,
            contactNo TEXT
        );

        CREATE TABLE IF NOT EXISTS Client (
            clientID INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            address TEXT,
            contactNo TEXT
        );

        CREATE TABLE IF NOT EXISTS Pet (
            petID INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            species TEXT,
            breed TEXT,
            gender TEXT,
            birthDate TEXT,
            ownerID INTEGER,
            FOREIGN KEY(ownerID) REFERENCES Client(clientID) ON DELETE SET NULL
        );

        CREATE TABLE IF NOT EXISTS Appointment (
            appointmentID INTEGER PRIMARY KEY AUTOINCREMENT,
            petID INTEGER,
            vetID INTEGER,
            date TEXT,
            time TEXT,
            status TEXT,
            reason TEXT,
            FOREIGN KEY(petID) REFERENCES Pet(petID) ON DELETE CASCADE,
            FOREIGN KEY(vetID) REFERENCES Veterinarian(vetID) ON DELETE SET NULL
        );

        CREATE TABLE IF NOT EXISTS MedicalRecord (
            recordID INTEGER PRIMARY KEY AUTOINCREMENT,
            petID INTEGER,
            visitDate TEXT,
            diagnosis TEXT,
            notes TEXT,
            FOREIGN KEY(petID) REFERENCES Pet(petID) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS Treatment (
            treatmentID INTEGER PRIMARY KEY AUTOINCREMENT,
            treatmentName TEXT NOT NULL,
            description TEXT,
            cost REAL DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS MedicalRecord_Treatment (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recordID INTEGER,
            treatmentID INTEGER,
            quantity INTEGER DEFAULT 1,
            FOREIGN KEY(recordID) REFERENCES MedicalRecord(recordID) ON DELETE CASCADE,
            FOREIGN KEY(treatmentID) REFERENCES Treatment(treatmentID) ON DELETE CASCADE
        );
        """)
        self.conn.commit()

    # Convenience wrappers
    def fetchall(self, query, params=()):
        self.cur.execute(query, params)
        return self.cur.fetchall()

    def fetchone(self, query, params=()):
        self.cur.execute(query, params)
        return self.cur.fetchone()

    def execute(self, query, params=()):
        self.cur.execute(query, params)
        self.conn.commit()
        return self.cur

    def close(self):
        self.conn.close()

# UTILS
def calc_age_from_iso(birth_iso):
    if not birth_iso:
        return ""
    try:
        b = datetime.strptime(birth_iso, "%Y-%m-%d").date()
        today = date.today()
        yrs = today.year - b.year - ((today.month, today.day) < (b.month, b.day))
        return f"{yrs} yr(s)"
    except Exception:
        return ""

def safe_int(val, default=None):
    try:
        return int(val)
    except Exception:
        return default

# GUI / Application
class VetClinicApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Vet Clinic Management")
        self.root.geometry("1100x700")
        self.db = Database()
        self._build_ui()
        self.show_home()

    def _build_ui(self):
        # top bar
        top_bar = tk.Frame(self.root, bg="#ffffff", height=70)
        top_bar.pack(fill=tk.X)
        tk.Label(top_bar, text="Veterinary Clinic System", font=("Arial", 18, "bold"), bg="#ffffff").pack(side=tk.LEFT, padx=18, pady=14)

        # left menu
        self.menu = tk.Frame(self.root, bg="#93c6e6", width=220)
        self.menu.pack(side=tk.LEFT, fill=tk.Y)
        self.content = tk.Frame(self.root, bg="#f5fbff")
        self.content.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        tk.Label(self.menu, text="Menu", font=("Arial", 14, "bold"), bg="#93c6e6").pack(pady=12)
        btn_conf = {"width":20, "pady":6, "bg":"#bde5fb", "relief":"flat"}
        tk.Button(self.menu, text="Home", command=self.show_home, **btn_conf).pack(pady=4)
        tk.Button(self.menu, text="Clients", command=self.show_clients, **btn_conf).pack(pady=4)
        tk.Button(self.menu, text="Animals", command=self.show_pets, **btn_conf).pack(pady=4)
        tk.Button(self.menu, text="Appointments", command=self.show_appointments, **btn_conf).pack(pady=4)
        tk.Button(self.menu, text="Invokes (Records)", command=self.show_invokes, **btn_conf).pack(pady=4)
        tk.Button(self.menu, text="Treatments", command=self.show_treatments, **btn_conf).pack(pady=4)
        tk.Button(self.menu, text="Reports", command=self.show_reports, **btn_conf).pack(pady=4)
        tk.Button(self.menu, text="Search", command=self.show_search, **btn_conf).pack(pady=4)
        tk.Button(self.menu, text="Exit", command=self._exit, bg="#ff7f7f", width=20, pady=6).pack(side=tk.BOTTOM, pady=12)

    def clear_content(self):
        for w in self.content.winfo_children():
            w.destroy()

    # ---- HOME ----
    def show_home(self):
        self.clear_content()
        card = tk.Frame(self.content, bg="white", bd=1, relief=tk.RIDGE, padx=20, pady=20)
        card.place(relx=0.5, rely=0.4, anchor=tk.CENTER)
        tk.Label(card, text="Welcome to the Vet Clinic Management", font=("Arial", 18, "bold"), bg="white").pack(pady=6)
        tk.Label(card, text="Use the left menu to manage clients, pets, appointments, records and reports.", bg="white", wraplength=600, justify=tk.CENTER).pack(pady=10)

    # ---- CLIENTS ----
    def show_clients(self):
        self.clear_content()
        tk.Label(self.content, text="Clients (Owners)", font=("Arial", 16, "bold"), bg="#f5fbff").pack(pady=10)
        frame = tk.Frame(self.content, bg="white", bd=1, relief=tk.SOLID)
        frame.pack(fill=tk.BOTH, expand=True, padx=18, pady=10)

        cols = ("ID","Name","Address","Contact")
        self.client_tree = ttk.Treeview(frame, columns=cols, show="headings")
        for c in cols:
            self.client_tree.heading(c, text=c)
            self.client_tree.column(c, width=150 if c!="Address" else 300)
        self.client_tree.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        self._load_clients()

        btns = tk.Frame(self.content, bg="#f5fbff")
        btns.pack(pady=6)
        tk.Button(btns, text="Add", width=12, command=self._client_add).grid(row=0,column=0,padx=6)
        tk.Button(btns, text="Edit", width=12, command=self._client_edit).grid(row=0,column=1,padx=6)
        tk.Button(btns, text="Delete", width=12, command=self._client_delete).grid(row=0,column=2,padx=6)
        tk.Button(btns, text="Refresh", width=12, command=self._load_clients).grid(row=0,column=3,padx=6)

    def _load_clients(self):
        for i in self.client_tree.get_children():
            self.client_tree.delete(i)
        rows = self.db.fetchall("SELECT clientID, name, address, contactNo FROM Client ORDER BY clientID DESC")
        for r in rows:
            self.client_tree.insert("", tk.END, values=r)

    def _client_add(self):
        win = tk.Toplevel(self.root); win.title("Add Client")
        tk.Label(win, text="Name:").grid(row=0,column=0,sticky="w"); e_name = tk.Entry(win, width=40); e_name.grid(row=0,column=1,padx=6,pady=4)
        tk.Label(win, text="Address:").grid(row=1,column=0,sticky="w"); e_addr = tk.Entry(win, width=40); e_addr.grid(row=1,column=1,padx=6,pady=4)
        tk.Label(win, text="Contact:").grid(row=2,column=0,sticky="w"); e_contact = tk.Entry(win, width=40); e_contact.grid(row=2,column=1,padx=6,pady=4)
        def save():
            name = e_name.get().strip()
            if not name:
                messagebox.showerror("Validation", "Client name is required.")
                return
            self.db.execute("INSERT INTO Client (name, address, contactNo) VALUES (?, ?, ?)",
                            (name, e_addr.get().strip(), e_contact.get().strip()))
            win.destroy(); self._load_clients()
        tk.Button(win, text="Save", command=save).grid(row=3,column=0,columnspan=2,pady=8)

    def _client_edit(self):
        sel = self.client_tree.selection()
        if not sel:
            messagebox.showwarning("Select", "Select client to edit.")
            return
        data = self.client_tree.item(sel[0])['values']
        cid, name, address, contact = data
        win = tk.Toplevel(self.root); win.title("Edit Client")
        tk.Label(win, text="Name:").grid(row=0,column=0,sticky="w"); e_name = tk.Entry(win, width=40); e_name.grid(row=0,column=1); e_name.insert(0,name)
        tk.Label(win, text="Address:").grid(row=1,column=0,sticky="w"); e_addr = tk.Entry(win, width=40); e_addr.grid(row=1,column=1); e_addr.insert(0,address or "")
        tk.Label(win, text="Contact:").grid(row=2,column=0,sticky="w"); e_contact = tk.Entry(win, width=40); e_contact.grid(row=2,column=1); e_contact.insert(0,contact or "")
        def save():
            if not e_name.get().strip():
                messagebox.showerror("Validation", "Name required.")
                return
            self.db.execute("UPDATE Client SET name=?, address=?, contactNo=? WHERE clientID=?",
                            (e_name.get().strip(), e_addr.get().strip(), e_contact.get().strip(), cid))
            win.destroy(); self._load_clients()
        tk.Button(win, text="Save", command=save).grid(row=3,column=0,columnspan=2,pady=8)

    def _client_delete(self):
        sel = self.client_tree.selection()
        if not sel:
            messagebox.showwarning("Select", "Select client to delete.")
            return
        cid = self.client_tree.item(sel[0])['values'][0]
        if messagebox.askyesno("Confirm", "Delete client? Pets' owner will be set to NULL."):
            self.db.execute("DELETE FROM Client WHERE clientID=?", (cid,))
            self._load_clients()

    # ---- PETS / ANIMALS ----
    def show_pets(self):
        self.clear_content()
        tk.Label(self.content, text="Pets / Animals", font=("Arial", 16, "bold"), bg="#f5fbff").pack(pady=10)
        frame = tk.Frame(self.content, bg="white", bd=1, relief=tk.SOLID)
        frame.pack(fill=tk.BOTH, expand=True, padx=18, pady=10)

        cols = ("ID","Name","Species","Breed","Gender","BirthDate","Owner","Age")
        self.pet_tree = ttk.Treeview(frame, columns=cols, show="headings")
        for c in cols:
            self.pet_tree.heading(c, text=c)
            self.pet_tree.column(c, width=100)
        self.pet_tree.column("Owner", width=160)
        self.pet_tree.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        self._load_pets()

        btns = tk.Frame(self.content, bg="#f5fbff"); btns.pack(pady=6)
        tk.Button(btns, text="Add Pet", width=12, command=self._pet_add).grid(row=0,column=0,padx=6)
        tk.Button(btns, text="Edit Pet", width=12, command=self._pet_edit).grid(row=0,column=1,padx=6)
        tk.Button(btns, text="Delete Pet", width=12, command=self._pet_delete).grid(row=0,column=2,padx=6)
        tk.Button(btns, text="Refresh", width=12, command=self._load_pets).grid(row=0,column=3,padx=6)

    def _load_pets(self):
        for i in self.pet_tree.get_children():
            self.pet_tree.delete(i)
        rows = self.db.fetchall("""
            SELECT Pet.petID, Pet.name, Pet.species, Pet.breed, Pet.gender, Pet.birthDate, Client.name
            FROM Pet LEFT JOIN Client ON Pet.ownerID = Client.clientID
            ORDER BY Pet.petID DESC
        """)
        for r in rows:
            birth = r[5] or ""
            age = calc_age_from_iso(birth)
            owner = r[6] or "—"
            self.pet_tree.insert("", tk.END, values=(r[0], r[1], r[2], r[3], r[4], birth, owner, age))

    def _pet_add(self):
        win = tk.Toplevel(self.root); win.title("Add Pet")
        tk.Label(win, text="Name:").grid(row=0,column=0,sticky="w"); e_name = tk.Entry(win, width=30); e_name.grid(row=0,column=1)
        tk.Label(win, text="Species:").grid(row=1,column=0,sticky="w"); e_species = tk.Entry(win, width=30); e_species.grid(row=1,column=1)
        tk.Label(win, text="Breed:").grid(row=2,column=0,sticky="w"); e_breed = tk.Entry(win, width=30); e_breed.grid(row=2,column=1)
        tk.Label(win, text="Gender:").grid(row=3,column=0,sticky="w"); gender_cb = ttk.Combobox(win, values=("Male","Female","Unknown"), width=28); gender_cb.grid(row=3,column=1); gender_cb.set("Unknown")
        tk.Label(win, text="BirthDate (YYYY-MM-DD):").grid(row=4,column=0,sticky="w"); e_birth = tk.Entry(win, width=30); e_birth.grid(row=4,column=1)
        tk.Label(win, text="Owner:").grid(row=5,column=0,sticky="w")
        clients = self.db.fetchall("SELECT clientID, name FROM Client ORDER BY name")
        owner_values = [f"{c[0]} - {c[1]}" for c in clients]
        owner_var = tk.StringVar(); owner_cb = ttk.Combobox(win, values=owner_values, textvariable=owner_var, width=28); owner_cb.grid(row=5,column=1)
        def save():
            name = e_name.get().strip()
            if not name:
                messagebox.showerror("Validation", "Pet name required.")
                return
            ownerID = None
            if owner_var.get():
                ownerID = safe_int(owner_var.get().split(" - ")[0])
            self.db.execute("INSERT INTO Pet (name, species, breed, gender, birthDate, ownerID) VALUES (?, ?, ?, ?, ?, ?)",
                            (name, e_species.get().strip(), e_breed.get().strip(), gender_cb.get().strip(), e_birth.get().strip(), ownerID))
            win.destroy(); self._load_pets()
        tk.Button(win, text="Save", command=save).grid(row=6,column=0,columnspan=2,pady=8)

    def _pet_edit(self):
        sel = self.pet_tree.selection()
        if not sel:
            messagebox.showwarning("Select", "Select a pet to edit.")
            return
        data = self.pet_tree.item(sel[0])['values']
        pid = data[0]
        win = tk.Toplevel(self.root); win.title("Edit Pet")
        tk.Label(win, text="Name:").grid(row=0,column=0,sticky="w"); e_name = tk.Entry(win, width=30); e_name.grid(row=0,column=1); e_name.insert(0, data[1])
        tk.Label(win, text="Species:").grid(row=1,column=0,sticky="w"); e_species = tk.Entry(win, width=30); e_species.grid(row=1,column=1); e_species.insert(0, data[2] or "")
        tk.Label(win, text="Breed:").grid(row=2,column=0,sticky="w"); e_breed = tk.Entry(win, width=30); e_breed.grid(row=2,column=1); e_breed.insert(0, data[3] or "")
        tk.Label(win, text="Gender:").grid(row=3,column=0,sticky="w"); gender_cb = ttk.Combobox(win, values=("Male","Female","Unknown"), width=28); gender_cb.grid(row=3,column=1); gender_cb.set(data[4] or "Unknown")
        tk.Label(win, text="BirthDate (YYYY-MM-DD):").grid(row=4,column=0,sticky="w"); e_birth = tk.Entry(win, width=30); e_birth.grid(row=4,column=1); e_birth.insert(0, data[5] or "")
        tk.Label(win, text="Owner:").grid(row=5,column=0,sticky="w")
        clients = self.db.fetchall("SELECT clientID, name FROM Client ORDER BY name")
        owner_values = [f"{c[0]} - {c[1]}" for c in clients]
        owner_var = tk.StringVar(); owner_cb = ttk.Combobox(win, values=owner_values, textvariable=owner_var, width=28); owner_cb.grid(row=5,column=1)
        # pre-select owner if exist
        if data[6] and owner_values:
            for opt in owner_values:
                if opt.endswith(data[6]):
                    owner_var.set(opt); break
        def save():
            ownerID = None
            if owner_var.get():
                ownerID = safe_int(owner_var.get().split(" - ")[0])
            self.db.execute("UPDATE Pet SET name=?, species=?, breed=?, gender=?, birthDate=?, ownerID=? WHERE petID=?",
                            (e_name.get().strip(), e_species.get().strip(), e_breed.get().strip(), gender_cb.get().strip(), e_birth.get().strip(), ownerID, pid))
            win.destroy(); self._load_pets()
        tk.Button(win, text="Save", command=save).grid(row=6,column=0,columnspan=2,pady=8)

    def _pet_delete(self):
        sel = self.pet_tree.selection()
        if not sel:
            messagebox.showwarning("Select", "Select a pet to delete.")
            return
        pid = self.pet_tree.item(sel[0])['values'][0]
        if messagebox.askyesno("Confirm", "Delete pet and all related records?"):
            self.db.execute("DELETE FROM Pet WHERE petID=?", (pid,))
            self._load_pets()

    # ---- APPOINTMENTS ----
    def show_appointments(self):
        self.clear_content()
        tk.Label(self.content, text="Appointments", font=("Arial", 16, "bold"), bg="#f5fbff").pack(pady=10)
        frame = tk.Frame(self.content, bg="white", bd=1, relief=tk.SOLID)
        frame.pack(fill=tk.BOTH, expand=True, padx=18, pady=10)

        cols = ("ID","Pet","Vet","Date","Time","Status","Reason")
        self.app_tree = ttk.Treeview(frame, columns=cols, show="headings")
        for c in cols:
            self.app_tree.heading(c, text=c)
            self.app_tree.column(c, width=120)
        self.app_tree.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        self._load_appointments()

        btns = tk.Frame(self.content, bg="#f5fbff"); btns.pack(pady=6)
        tk.Button(btns, text="Add Appointment", width=15, command=self._appointment_add).grid(row=0,column=0,padx=6)
        tk.Button(btns, text="Complete", width=12, command=lambda: self._appointment_update_status("completed")).grid(row=0,column=1,padx=6)
        tk.Button(btns, text="Cancel", width=12, command=lambda: self._appointment_update_status("cancelled")).grid(row=0,column=2,padx=6)
        tk.Button(btns, text="Refresh", width=12, command=self._load_appointments).grid(row=0,column=3,padx=6)

    def _load_appointments(self):
        for i in self.app_tree.get_children():
            self.app_tree.delete(i)
        rows = self.db.fetchall("""
            SELECT a.appointmentID, p.name, v.name, a.date, a.time, a.status, a.reason
            FROM Appointment a
            LEFT JOIN Pet p ON a.petID = p.petID
            LEFT JOIN Veterinarian v ON a.vetID = v.vetID
            ORDER BY a.date ASC
        """)
        for r in rows:
            self.app_tree.insert("", tk.END, values=r)

    def _appointment_add(self):
        win = tk.Toplevel(self.root); win.title("Add Appointment")
        tk.Label(win, text="Pet:").grid(row=0,column=0,sticky="w")
        pets = self.db.fetchall("SELECT petID, name FROM Pet ORDER BY name")
        pet_opts = [f"{p[0]} - {p[1]}" for p in pets]
        pet_var = tk.StringVar(); pet_cb = ttk.Combobox(win, values=pet_opts, textvariable=pet_var, width=34); pet_cb.grid(row=0,column=1)

        tk.Label(win, text="Vet (optional):").grid(row=1,column=0,sticky="w")
        vets = self.db.fetchall("SELECT vetID, name FROM Veterinarian ORDER BY name")
        vet_opts = [f"{v[0]} - {v[1]}" for v in vets]
        vet_var = tk.StringVar(); vet_cb = ttk.Combobox(win, values=vet_opts, textvariable=vet_var, width=34); vet_cb.grid(row=1,column=1)

        tk.Label(win, text="Date (YYYY-MM-DD):").grid(row=2,column=0,sticky="w"); e_date = tk.Entry(win, width=36); e_date.grid(row=2,column=1)
        tk.Label(win, text="Time (HH:MM):").grid(row=3,column=0,sticky="w"); e_time = tk.Entry(win, width=36); e_time.grid(row=3,column=1)
        tk.Label(win, text="Reason:").grid(row=4,column=0,sticky="w"); e_reason = tk.Entry(win, width=36); e_reason.grid(row=4,column=1)

        def save():
            if not pet_var.get():
                messagebox.showerror("Validation", "Select a pet.")
                return
            petID = safe_int(pet_var.get().split(" - ")[0])
            vetID = None
            if vet_var.get():
                vetID = safe_int(vet_var.get().split(" - ")[0])
            self.db.execute("INSERT INTO Appointment (petID, vetID, date, time, status, reason) VALUES (?, ?, ?, ?, ?, ?)",
                            (petID, vetID, e_date.get().strip(), e_time.get().strip(), "scheduled", e_reason.get().strip()))
            win.destroy(); self._load_appointments()
        tk.Button(win, text="Save", command=save).grid(row=5,column=0,columnspan=2,pady=8)

    def _appointment_update_status(self, new_status):
        sel = self.app_tree.selection()
        if not sel:
            messagebox.showwarning("Select", "Select appointment first.")
            return
        aid = self.app_tree.item(sel[0])['values'][0]
        self.db.execute("UPDATE Appointment SET status=? WHERE appointmentID=?", (new_status, aid))
        self._load_appointments()

    # ---- TREATMENTS ----
    def show_treatments(self):
        self.clear_content()
        tk.Label(self.content, text="Treatments", font=("Arial", 16, "bold"), bg="#f5fbff").pack(pady=10)
        frame = tk.Frame(self.content, bg="white", bd=1, relief=tk.SOLID)
        frame.pack(fill=tk.BOTH, expand=True, padx=18, pady=10)

        cols = ("ID","Name","Description","Cost")
        self.treat_tree = ttk.Treeview(frame, columns=cols, show="headings")
        for c in cols:
            self.treat_tree.heading(c, text=c)
            self.treat_tree.column(c, width=150)
        self.treat_tree.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        self._load_treatments()

        btns = tk.Frame(self.content, bg="#f5fbff"); btns.pack(pady=6)
        tk.Button(btns, text="Add Treatment", width=14, command=self._treatment_add).grid(row=0,column=0,padx=6)
        tk.Button(btns, text="Edit Treatment", width=14, command=self._treatment_edit).grid(row=0,column=1,padx=6)
        tk.Button(btns, text="Delete Treatment", width=14, command=self._treatment_delete).grid(row=0,column=2,padx=6)
        tk.Button(btns, text="Refresh", width=12, command=self._load_treatments).grid(row=0,column=3,padx=6)

    def _load_treatments(self):
        for i in self.treat_tree.get_children():
            self.treat_tree.delete(i)
        rows = self.db.fetchall("SELECT treatmentID, treatmentName, description, cost FROM Treatment ORDER BY treatmentName")
        for r in rows:
            self.treat_tree.insert("", tk.END, values=r)

    def _treatment_add(self):
        win = tk.Toplevel(self.root); win.title("Add Treatment")
        tk.Label(win, text="Name:").grid(row=0,column=0,sticky="w"); e_name = tk.Entry(win, width=40); e_name.grid(row=0,column=1,padx=6,pady=4)
        tk.Label(win, text="Description:").grid(row=1,column=0,sticky="w"); e_desc = tk.Entry(win, width=40); e_desc.grid(row=1,column=1,padx=6,pady=4)
        tk.Label(win, text="Cost:").grid(row=2,column=0,sticky="w"); e_cost = tk.Entry(win, width=40); e_cost.grid(row=2,column=1,padx=6,pady=4)
        def save():
            name = e_name.get().strip()
            if not name:
                messagebox.showerror("Validation", "Treatment name required.")
                return
            try:
                cost = float(e_cost.get() or 0)
            except:
                messagebox.showerror("Validation", "Invalid cost.")
                return
            self.db.execute("INSERT INTO Treatment (treatmentName, description, cost) VALUES (?, ?, ?)", (name, e_desc.get().strip(), cost))
            win.destroy(); self._load_treatments()
        tk.Button(win, text="Save", command=save).grid(row=3,column=0,columnspan=2,pady=8)

    def _treatment_edit(self):
        sel = self.treat_tree.selection()
        if not sel:
            messagebox.showwarning("Select", "Select treatment to edit.")
            return
        data = self.treat_tree.item(sel[0])['values']
        tid = data[0]
        win = tk.Toplevel(self.root); win.title("Edit Treatment")
        tk.Label(win, text="Name:").grid(row=0,column=0,sticky="w"); e_name = tk.Entry(win, width=40); e_name.grid(row=0,column=1); e_name.insert(0, data[1])
        tk.Label(win, text="Description:").grid(row=1,column=0,sticky="w"); e_desc = tk.Entry(win, width=40); e_desc.grid(row=1,column=1); e_desc.insert(0, data[2] or "")
        tk.Label(win, text="Cost:").grid(row=2,column=0,sticky="w"); e_cost = tk.Entry(win, width=40); e_cost.grid(row=2,column=1); e_cost.insert(0, data[3] or "0")
        def save():
            try:
                cost = float(e_cost.get() or 0)
            except:
                messagebox.showerror("Validation", "Invalid cost.")
                return
            self.db.execute("UPDATE Treatment SET treatmentName=?, description=?, cost=? WHERE treatmentID=?",
                            (e_name.get().strip(), e_desc.get().strip(), cost, tid))
            win.destroy(); self._load_treatments()
        tk.Button(win, text="Save", command=save).grid(row=3,column=0,columnspan=2,pady=8)

    def _treatment_delete(self):
        sel = self.treat_tree.selection()
        if not sel:
            messagebox.showwarning("Select", "Select treatment to delete.")
            return
        tid = self.treat_tree.item(sel[0])['values'][0]
        if messagebox.askyesno("Confirm", "Delete treatment? This will remove links to records."):
            self.db.execute("DELETE FROM Treatment WHERE treatmentID=?", (tid,))
            self._load_treatments()

    # ---- MEDICAL RECORDS (Invokes) ----
    def show_invokes(self):
        self.clear_content()
        tk.Label(self.content, text="Medical Records (Invokes)", font=("Arial", 16, "bold"), bg="#f5fbff").pack(pady=10)

        main = tk.Frame(self.content, bg="#f5fbff")
        main.pack(fill=tk.BOTH, expand=True, padx=12, pady=6)

        left = tk.Frame(main, bg="white", bd=1, relief=tk.SOLID)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(12,6), pady=10)
        tk.Label(left, text="Records", bg="white", font=("Arial", 12, "bold")).pack(pady=6)
        cols = ("ID","Pet","VisitDate","Diagnosis","Notes","Treatments")
        self.record_tree = ttk.Treeview(left, columns=cols, show="headings")
        for c in cols:
            self.record_tree.heading(c, text=c)
            self.record_tree.column(c, width=100)
        self.record_tree.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        self._load_records()

        right = tk.Frame(main, bg="white", bd=1, relief=tk.SOLID, width=360)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(6,12), pady=10)
        tk.Label(right, text="Actions", bg="white", font=("Arial", 12, "bold")).pack(pady=6)
        btn_frame = tk.Frame(right, bg="white"); btn_frame.pack(pady=8)
        tk.Button(btn_frame, text="Add Medical Record", width=18, command=self._record_add).grid(row=0,column=0,padx=6, pady=6)
        tk.Button(btn_frame, text="Link Treatment -> Record", width=22, command=self._link_treatment_to_record).grid(row=1,column=0,padx=6, pady=6)
        tk.Button(btn_frame, text="Refresh", width=18, command=self._load_records).grid(row=2,column=0,padx=6, pady=6)

    def _load_records(self):
        for i in self.record_tree.get_children():
            self.record_tree.delete(i)
        rows = self.db.fetchall("""
            SELECT m.recordID, p.name, m.visitDate, m.diagnosis, m.notes
            FROM MedicalRecord m LEFT JOIN Pet p ON m.petID = p.petID
            ORDER BY m.visitDate DESC
        """)
        for r in rows:
            recID = r[0]
            tret_rows = self.db.fetchall("""
                SELECT t.treatmentName FROM MedicalRecord_Treatment mrt
                JOIN Treatment t ON mrt.treatmentID = t.treatmentID
                WHERE mrt.recordID=?
            """, (recID,))
            tret = ", ".join([x[0] for x in tret_rows]) if tret_rows else ""
            self.record_tree.insert("", tk.END, values=(r[0], r[1], r[2], r[3], r[4], tret))

    def _record_add(self):
        win = tk.Toplevel(self.root); win.title("Add Medical Record")
        tk.Label(win, text="Pet:").grid(row=0,column=0,sticky="w")
        pets = self.db.fetchall("SELECT petID, name FROM Pet ORDER BY name")
        pet_opts = [f"{p[0]} - {p[1]}" for p in pets]
        pet_var = tk.StringVar(); pet_cb = ttk.Combobox(win, values=pet_opts, textvariable=pet_var, width=36); pet_cb.grid(row=0,column=1)

        tk.Label(win, text="Visit Date (YYYY-MM-DD):").grid(row=1,column=0,sticky="w"); e_date = tk.Entry(win, width=38); e_date.grid(row=1,column=1)
        tk.Label(win, text="Diagnosis:").grid(row=2,column=0,sticky="w"); e_diag = tk.Entry(win, width=38); e_diag.grid(row=2,column=1)
        tk.Label(win, text="Notes:").grid(row=3,column=0,sticky="w"); e_notes = tk.Entry(win, width=38); e_notes.grid(row=3,column=1)

        tk.Label(win, text="Treatments (multi-select):").grid(row=4,column=0,sticky="nw")
        treatments = self.db.fetchall("SELECT treatmentID, treatmentName FROM Treatment ORDER BY treatmentName")
        tr_list = tk.Listbox(win, selectmode=tk.MULTIPLE, height=6, width=36)
        for t in treatments:
            tr_list.insert(tk.END, f"{t[0]} - {t[1]}")
        tr_list.grid(row=4,column=1,padx=6,pady=6)

        def save():
            if not pet_var.get():
                messagebox.showerror("Validation", "Select a pet.")
                return
            petID = safe_int(pet_var.get().split(" - ")[0])
            vdate = e_date.get().strip()
            self.db.execute("INSERT INTO MedicalRecord (petID, visitDate, diagnosis, notes) VALUES (?, ?, ?, ?)",
                            (petID, vdate, e_diag.get().strip(), e_notes.get().strip()))
            recID = self.db.cur.lastrowid
            for idx in tr_list.curselection():
                tid = safe_int(tr_list.get(idx).split(" - ")[0])
                self.db.execute("INSERT INTO MedicalRecord_Treatment (recordID, treatmentID, quantity) VALUES (?, ?, ?)", (recID, tid, 1))
            win.destroy(); self._load_records()

        tk.Button(win, text="Save", command=save).grid(row=5,column=0,columnspan=2,pady=8)

    def _link_treatment_to_record(self):
        sel_rec = self.record_tree.selection()
        if not sel_rec:
            messagebox.showwarning("Select", "Select a medical record first.")
            return
        recordID = self.record_tree.item(sel_rec[0])['values'][0]
        # open small dialog to pick a treatment
        win = tk.Toplevel(self.root); win.title("Link Treatment")
        tk.Label(win, text="Select Treatment:").pack(padx=10, pady=6)
        treatments = self.db.fetchall("SELECT treatmentID, treatmentName FROM Treatment ORDER BY treatmentName")
        tv = ttk.Combobox(win, values=[f"{t[0]} - {t[1]}" for t in treatments], width=40)
        tv.pack(padx=10, pady=6)
        def do_link():
            if not tv.get():
                messagebox.showerror("Validation", "Pick a treatment.")
                return
            tid = safe_int(tv.get().split(" - ")[0])
            self.db.execute("INSERT INTO MedicalRecord_Treatment (recordID, treatmentID, quantity) VALUES (?, ?, ?)", (recordID, tid, 1))
            win.destroy(); self._load_records()
        tk.Button(win, text="Link", command=do_link).pack(pady=8)

    # ---- SEARCH ----
    def show_search(self):
        self.clear_content()
        tk.Label(self.content, text="Search", font=("Arial", 16, "bold"), bg="#f5fbff").pack(pady=10)
        frame = tk.Frame(self.content, bg="white", bd=1, relief=tk.SOLID); frame.pack(fill=tk.BOTH, expand=True, padx=18, pady=10)
        tk.Label(frame, text="Keyword:").pack(pady=6)
        q_entry = tk.Entry(frame, width=60); q_entry.pack(pady=6)
        result_tree = ttk.Treeview(frame, columns=("Type","Info"), show="headings")
        result_tree.heading("Type", text="Type"); result_tree.heading("Info", text="Info")
        result_tree.pack(fill=tk.BOTH, expand=True, padx=12, pady=8)
        def run_search():
            kw = q_entry.get().strip()
            for i in result_tree.get_children():
                result_tree.delete(i)
            if not kw:
                return
            # clients
            for r in self.db.fetchall("SELECT clientID, name FROM Client WHERE name LIKE ? OR address LIKE ? OR contactNo LIKE ?", (f"%{kw}%", f"%{kw}%", f"%{kw}%")):
                result_tree.insert("", tk.END, values=("Client", f"{r[0]} - {r[1]}"))
            # pets
            for r in self.db.fetchall("SELECT petID, name, species FROM Pet WHERE name LIKE ? OR species LIKE ? OR breed LIKE ?", (f"%{kw}%", f"%{kw}%", f"%{kw}%")):
                result_tree.insert("", tk.END, values=("Pet", f"{r[0]} - {r[1]} ({r[2]})"))
            # appointments
            for r in self.db.fetchall("SELECT a.appointmentID, p.name, a.date, a.time FROM Appointment a JOIN Pet p ON a.petID = p.petID WHERE p.name LIKE ? OR a.reason LIKE ?", (f"%{kw}%", f"%{kw}%")):
                result_tree.insert("", tk.END, values=("Appointment", f"{r[0]} - {r[1]} @ {r[2]} {r[3]}"))
        tk.Button(frame, text="Search", command=run_search).pack(pady=6)

    # ---- REPORTS ----
    def show_reports(self):
        self.clear_content()
        tk.Label(self.content, text="Reports", font=("Arial", 16, "bold"), bg="#f5fbff").pack(pady=10)
        frame = tk.Frame(self.content, bg="white", bd=1, relief=tk.SOLID); frame.pack(fill=tk.BOTH, expand=True, padx=18, pady=10)
        tk.Label(frame, text="Summary Report", font=("Arial", 12, "bold"), bg="white").pack(pady=8)
        self.report_area = tk.Text(frame, height=18)
        self.report_area.pack(fill=tk.BOTH, expand=True, padx=12, pady=8)
        tk.Button(frame, text="Generate Summary", command=self._generate_summary).pack(pady=6)

    def _generate_summary(self):
        self.report_area.delete("1.0", tk.END)
        total_clients = self.db.fetchone("SELECT COUNT(*) FROM Client")[0]
        total_pets = self.db.fetchone("SELECT COUNT(*) FROM Pet")[0]
        total_appointments = self.db.fetchone("SELECT COUNT(*) FROM Appointment")[0]
        total_records = self.db.fetchone("SELECT COUNT(*) FROM MedicalRecord")[0]
        lines = [
            "Clinic Summary Report",
            "=====================",
            f"Total Clients: {total_clients}",
            f"Total Pets: {total_pets}",
            f"Total Appointments: {total_appointments}",
            f"Total Medical Records: {total_records}",
            "",
            "Recent Appointments:",
        ]
        recent = self.db.fetchall("SELECT a.appointmentID, p.name, a.date, a.time, a.status FROM Appointment a LEFT JOIN Pet p ON a.petID=p.petID ORDER BY a.date DESC LIMIT 8")
        for r in recent:
            lines.append(f"- {r[0]}: {r[1]} on {r[2]} {r[3]} ({r[4]})")
        self.report_area.insert(tk.END, "\n".join(lines))

    # ---- EXIT ----
    def _exit(self):
        if messagebox.askokcancel("Exit", "Close application?"):
            self.db.close()
            self.root.destroy()

# Run application
if __name__ == "__main__":
    root = tk.Tk()
    app = VetClinicApp(root)
    root.mainloop()


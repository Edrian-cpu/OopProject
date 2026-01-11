import sqlite3

class Database:
    def __init__(self):
        self.conn = sqlite3.connect("vet_clinic.db")
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        """Create all required tables"""
        try:
            # Clients table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS clients (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    contact TEXT,
                    address TEXT
                )
            """)

            # Animals table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS animals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pet_name TEXT NOT NULL,
                    species TEXT,
                    breed TEXT,
                    age INTEGER,
                    owner_name TEXT
                )
            """)

            # Appointments table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS appointments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    client_name TEXT NOT NULL,
                    pet_name TEXT,
                    date TEXT,
                    time TEXT,
                    reason TEXT
                )
            """)

            # Treatments table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS treatments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    reason TEXT,
                    pet TEXT,
                    client TEXT,
                    treatment_type TEXT,
                    date TEXT,
                    confined TEXT,
                    notes TEXT
                )
            """)

            # Invoices table (create if not exists)
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS invoices (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    invoice_no TEXT,
                    client TEXT,
                    pet TEXT,
                    amount REAL,
                    date TEXT
                )
            """)

            # Ensure 'status' column exists (migration for older DBs)
            try:
                self.cursor.execute("PRAGMA table_info(invoices)")
                cols = [row[1] for row in self.cursor.fetchall()]  # row[1] is column name
                if "status" not in cols:
                    self.cursor.execute("ALTER TABLE invoices ADD COLUMN status TEXT DEFAULT 'Unpaid'")
            except Exception as mig_e:
                print(f"Warning: invoice status migration failed: {mig_e}")

            # Walk-ins table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS walkins (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    client_name TEXT,
                    contact TEXT,
                    address TEXT,
                    pet_name TEXT,
                    species TEXT,
                    breed TEXT,
                    age INTEGER,
                    reason TEXT,
                    date TEXT
                )
            """)

            # Pet Status tracking table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS pet_status (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pet TEXT,
                    client TEXT,
                    status TEXT,
                    date TEXT,
                    notes TEXT
                )
            """)

            self.conn.commit()
            print("✅ All tables created/validated successfully!")
        except Exception as e:
            print(f"Error creating tables: {e}")

    # Fetch clients for Dashboard
    def fetch_clients(self, keyword=""):
        self.cursor.execute(
            "SELECT * FROM clients WHERE name LIKE ?",
            ('%' + keyword + '%',)
        )
        return self.cursor.fetchall()

    def fetch_walkins(self):
        """Fetch all walk-ins from the database"""
        try:
            self.cursor.execute("SELECT id, client_name, contact, pet_name, species, breed, age, reason, date FROM walkins")
            rows = self.cursor.fetchall()
            return rows
        except Exception as e:
            print(f"Error fetching walk-ins: {e}")
            return []

    def insert_walkin(self, data):
        """Insert a new walk-in into the database"""
        try:
            self.cursor.execute(
                "INSERT INTO walkins (client_name, contact, address, pet_name, species, breed, age, reason, date) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                data
            )
            self.conn.commit()
        except Exception as e:
            print(f"Error inserting walk-in: {e}")

    def fetch_animals(self):
        """Fetch all animals from the database"""
        try:
            self.cursor.execute("SELECT id, pet_name, species, breed, age, owner_name FROM animals")
            rows = self.cursor.fetchall()
            return rows
        except Exception as e:
            print(f"Error fetching animals: {e}")
            return []

    def insert_animal(self, data):
        """Insert a new animal into the database"""
        try:
            self.cursor.execute(
                "INSERT INTO animals (pet_name, species, breed, age, owner_name) VALUES (?, ?, ?, ?, ?)",
                data
            )
            self.conn.commit()
        except Exception as e:
            print(f"Error inserting animal: {e}")

    def delete_animal(self, animal_id):
        """Delete an animal from the database"""
        try:
            self.cursor.execute("DELETE FROM animals WHERE id=?", (animal_id,))
            self.conn.commit()
        except Exception as e:
            print(f"Error deleting animal: {e}")

    def fetch_appointments(self):
        """Fetch all appointments from the database"""
        try:
            self.cursor.execute("SELECT id, client_name, pet_name, date, time, reason FROM appointments")
            rows = self.cursor.fetchall()
            return rows
        except Exception as e:
            print(f"Error fetching appointments: {e}")
            return []

    def insert_appointment(self, data):
        """Insert a new appointment into the database"""
        try:
            self.cursor.execute(
                "INSERT INTO appointments (client_name, pet_name, date, time, reason) VALUES (?, ?, ?, ?, ?)",
                data
            )
            self.conn.commit()
        except Exception as e:
            print(f"Error inserting appointment: {e}")

    def delete_appointment(self, appointment_id):
        """Delete an appointment from the database"""
        try:
            self.cursor.execute("DELETE FROM appointments WHERE id=?", (appointment_id,))
            self.conn.commit()
        except Exception as e:
            print(f"Error deleting appointment: {e}")

    def fetch_invoices(self):
        """Fetch all invoices from the database"""
        try:
            self.cursor.execute("SELECT id, invoice_no, client, pet, amount, date, status FROM invoices ORDER BY date DESC")
            rows = self.cursor.fetchall()
            return rows
        except Exception as e:
            print(f"Error fetching invoices: {e}")
            return []

    def insert_invoice(self, data):
        """Insert a new invoice into the database"""
        try:
            # data = [invoice_no, client, pet, amount, date, status]
            self.cursor.execute(
                "INSERT INTO invoices (invoice_no, client, pet, amount, date, status) VALUES (?, ?, ?, ?, ?, ?)",
                data
            )
            self.conn.commit()
        except Exception as e:
            print(f"Error inserting invoice: {e}")

    def update_invoice_amount(self, invoice_id, new_amount):
        """Update invoice amount"""
        try:
            self.cursor.execute("UPDATE invoices SET amount=? WHERE id=?", (new_amount, invoice_id))
            self.conn.commit()
        except Exception as e:
            print(f"Error updating invoice: {e}")

    def update_invoice_status(self, invoice_id, status):
        """Update invoice status (Paid/Unpaid)"""
        try:
            self.cursor.execute("UPDATE invoices SET status=? WHERE id=?", (status, invoice_id))
            self.conn.commit()
        except Exception as e:
            print(f"Error updating invoice status: {e}")

    def fetch_invoice_by_id(self, invoice_id):
        """Fetch single invoice by ID"""
        try:
            self.cursor.execute("SELECT id, invoice_no, client, pet, amount, date, status FROM invoices WHERE id=?", (invoice_id,))
            return self.cursor.fetchone()
        except Exception as e:
            print(f"Error fetching invoice: {e}")
            return None

    def insert_treatment_with_type(self, data):
        """Insert a new treatment with treatment type into the database"""
        try:
            # data = [reason, pet, client, treatment_type, date, confined, notes]
            self.cursor.execute(
                "INSERT INTO treatments (reason, pet, client, treatment_type, date, confined, notes) VALUES (?, ?, ?, ?, ?, ?, ?)",
                data
            )
            self.conn.commit()
            print(f"✅ Treatment added: {data}")
        except Exception as e:
            print(f"Error inserting treatment: {e}")

    def fetch_treatments(self):
        """Fetch all treatments from the database"""
        try:
            self.cursor.execute("SELECT id, reason, pet, client, treatment_type, date, confined, notes FROM treatments ORDER BY date DESC")
            rows = self.cursor.fetchall()
            return rows
        except Exception as e:
            print(f"Error fetching treatments: {e}")
            return []

    def insert_client(self, data):
        """Insert a new client into the database"""
        try:
            self.cursor.execute(
                "INSERT INTO clients (name, contact, address) VALUES (?, ?, ?)",
                data
            )
            self.conn.commit()
        except Exception as e:
            print(f"Error inserting client: {e}")

    def insert_pet_status(self, data):
        """Insert pet status record"""
        try:
            # data = [pet, client, status, date, notes]
            self.cursor.execute(
                "INSERT INTO pet_status (pet, client, status, date, notes) VALUES (?, ?, ?, ?, ?)",
                data
            )
            self.conn.commit()
        except Exception as e:
            print(f"Error inserting pet status: {e}")

    def fetch_pet_status(self):
        """Fetch all pet status records"""
        try:
            self.cursor.execute("SELECT id, pet, client, status, date, notes FROM pet_status ORDER BY date DESC")
            rows = self.cursor.fetchall()
            return rows
        except Exception as e:
            print(f"Error fetching pet status: {e}")
            return []


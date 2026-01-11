import tkinter as tk
from tkinter import ttk, messagebox

class TreatmentsFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#f4f6f9")
        self.controller = controller

        tk.Label(self, text="Treatments Module", font=("Segoe UI", 20), bg="#f4f6f9").pack(pady=10)

        self.create_form()
        self.create_table()
        self.load_treatments()
        self.create_back_button()

    def create_form(self):
        frame = tk.Frame(self, bg="#f4f6f9")
        frame.pack(pady=10)

        # Select Appointment
        tk.Label(frame, text="Select Appointment:", width=15, anchor="w", bg="#f4f6f9").grid(row=0, column=0, pady=5)
        self.appointment_combo = ttk.Combobox(frame, width=30, state="readonly")
        self.appointment_combo.grid(row=0, column=1, pady=5)
        self.appointment_combo.bind("<<ComboboxSelected>>", self.on_appointment_select)
        self.load_appointments()

        # Client Name (auto-populated)
        tk.Label(frame, text="Client:", width=15, anchor="w", bg="#f4f6f9").grid(row=1, column=0, pady=5)
        self.client_entry = tk.Entry(frame, width=30, state="readonly")
        self.client_entry.grid(row=1, column=1, pady=5)

        # Pet Name (auto-populated)
        tk.Label(frame, text="Pet:", width=15, anchor="w", bg="#f4f6f9").grid(row=2, column=0, pady=5)
        self.pet_entry = tk.Entry(frame, width=30, state="readonly")
        self.pet_entry.grid(row=2, column=1, pady=5)

        # Reason (auto-populated from appointment)
        tk.Label(frame, text="Reason:", width=15, anchor="w", bg="#f4f6f9").grid(row=3, column=0, pady=5)
        self.reason_entry = tk.Entry(frame, width=30, state="readonly")
        self.reason_entry.grid(row=3, column=1, pady=5)

        # Treatment Type based on Reason
        tk.Label(frame, text="Treatment Type:", width=15, anchor="w", bg="#f4f6f9").grid(row=4, column=0, pady=5)
        self.treatment_combo = ttk.Combobox(frame, width=30, state="readonly")
        self.treatment_combo.grid(row=4, column=1, pady=5)
        self.load_treatment_types()

        # Date (auto-populated)
        tk.Label(frame, text="Date:", width=15, anchor="w", bg="#f4f6f9").grid(row=5, column=0, pady=5)
        self.date_entry = tk.Entry(frame, width=30, state="readonly")
        self.date_entry.grid(row=5, column=1, pady=5)

        # Notes
        tk.Label(frame, text="Notes:", width=15, anchor="w", bg="#f4f6f9").grid(row=6, column=0, pady=5)
        self.notes_entry = tk.Entry(frame, width=30)
        self.notes_entry.grid(row=6, column=1, pady=5)

        # Confine Pet Checkbox (Emergency)
        tk.Label(frame, text="Emergency:", width=15, anchor="w", bg="#f4f6f9").grid(row=7, column=0, pady=5)
        self.confine_var = tk.BooleanVar()
        self.confine_check = tk.Checkbutton(frame, text="Confine Pet (Emergency Only)", variable=self.confine_var, bg="#f4f6f9")
        self.confine_check.grid(row=7, column=1, pady=5, sticky="w")

        tk.Button(frame, text="Add Treatment", bg="#2563eb", fg="white", command=self.add_treatment).grid(row=8, column=0, columnspan=2, pady=10)

    def load_treatment_types(self):
        """Load treatment types available"""
        self.treatment_types = [
            "Checkup",
            "Vaccination",
            "Surgery",
            "Dental Cleaning",
            "X-Ray",
            "Blood Test",
            "Grooming",
            "Wound Care",
            "Physical Therapy",
            "Medication"
        ]
        self.treatment_combo['values'] = self.treatment_types

    def load_appointments(self):
        """Load appointments into dropdown"""
        try:
            rows = self.controller.db.fetch_appointments()
            appointment_display = [f"{row[1]} - {row[2]} ({row[5]})" for row in rows]  # Client - Pet (Reason)
            self.appointment_combo['values'] = appointment_display
            self.appointment_data = {f"{row[1]} - {row[2]} ({row[5]})": row for row in rows}
        except Exception as e:
            print(f"Error loading appointments: {e}")

    def on_appointment_select(self, event):
        """Auto-populate fields when appointment is selected"""
        try:
            selected = self.appointment_combo.get()
            if selected in self.appointment_data:
                appt = self.appointment_data[selected]
                # appt = (ID, client_name, pet_name, date, time, reason)
                
                self.client_entry.config(state="normal")
                self.client_entry.delete(0, tk.END)
                self.client_entry.insert(0, appt[1])
                self.client_entry.config(state="readonly")

                self.pet_entry.config(state="normal")
                self.pet_entry.delete(0, tk.END)
                self.pet_entry.insert(0, appt[2])
                self.pet_entry.config(state="readonly")

                self.reason_entry.config(state="normal")
                self.reason_entry.delete(0, tk.END)
                self.reason_entry.insert(0, appt[5])
                self.reason_entry.config(state="readonly")

                self.date_entry.config(state="normal")
                self.date_entry.delete(0, tk.END)
                self.date_entry.insert(0, appt[3])
                self.date_entry.config(state="readonly")
                
                # Auto-suggest treatment type based on reason
                reason = appt[5].lower()
                suggested_treatment = self.suggest_treatment(reason)
                self.treatment_combo.current(self.treatment_types.index(suggested_treatment) if suggested_treatment in self.treatment_types else 0)
        except Exception as e:
            print(f"Error selecting appointment: {e}")

    def suggest_treatment(self, reason):
        """Suggest treatment type based on appointment reason"""
        reason_lower = reason.lower()
        
        suggestions = {
            "checkup": "Checkup",
            "vaccine": "Vaccination",
            "surgery": "Surgery",
            "dental": "Dental Cleaning",
            "x-ray": "X-Ray",
            "blood": "Blood Test",
            "groom": "Grooming",
            "wound": "Wound Care",
            "therapy": "Physical Therapy",
            "medicine": "Medication"
        }
        
        for key, value in suggestions.items():
            if key in reason_lower:
                return value
        
        return "Checkup"  # Default

    def create_table(self):
        frame = tk.Frame(self, bg="#f4f6f9")
        frame.pack(pady=10, fill="both", expand=True)

        columns = ("ID", "Reason", "Pet", "Client", "Treatment Type", "Date", "Confined", "Notes")
        self.tree = ttk.Treeview(frame, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=90)

        self.tree.pack(fill="both", expand=True, padx=20, pady=20)

    def load_treatments(self):
        self.tree.delete(*self.tree.get_children())
        rows = self.controller.db.fetch_treatments()
        for row in rows:
            self.tree.insert("", "end", values=row)

    def add_treatment(self):
        """Add treatment and refresh table"""
        reason = self.reason_entry.get()
        pet = self.pet_entry.get()
        client = self.client_entry.get()
        treatment_type = self.treatment_combo.get()
        date = self.date_entry.get()
        notes = self.notes_entry.get()
        confined = "Yes" if self.confine_var.get() else "No"

        if not all([reason, pet, client, treatment_type, date]):
            messagebox.showerror("Error", "Please select all required fields!")
            return

        data = [reason, pet, client, treatment_type, date, confined, notes if notes else "No notes"]
        self.controller.db.insert_treatment_with_type(data)
        
        # Add treatment cost to invoice
        self.controller.add_treatment_cost(client, treatment_type, 0)
        
        messagebox.showinfo("Success", "Treatment added and invoice updated!")

        # Clear form
        self.appointment_combo.set("")
        self.client_entry.config(state="normal")
        self.client_entry.delete(0, tk.END)
        self.client_entry.config(state="readonly")
        self.pet_entry.config(state="normal")
        self.pet_entry.delete(0, tk.END)
        self.pet_entry.config(state="readonly")
        self.reason_entry.config(state="normal")
        self.reason_entry.delete(0, tk.END)
        self.reason_entry.config(state="readonly")
        self.treatment_combo.set("")
        self.date_entry.config(state="normal")
        self.date_entry.delete(0, tk.END)
        self.date_entry.config(state="readonly")
        self.notes_entry.delete(0, tk.END)
        self.confine_var.set(False)

        # Refresh table
        self.load_treatments()

    def create_back_button(self):
        tk.Button(self, text="Back to Dashboard", bg="#334155", fg="white", 
                  command=lambda: self.controller.show_frame("DashboardFrame")).pack(pady=10)

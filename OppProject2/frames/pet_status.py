import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

class PetStatusFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#f4f6f9")
        self.controller = controller

        tk.Label(self, text="Pet Status Tracking", font=("Segoe UI", 20), bg="#f4f6f9").pack(pady=10)

        self.create_form()
        self.create_table()
        self.load_pet_status()
        self.create_back_button()

    def create_form(self):
        frame = tk.Frame(self, bg="#f4f6f9")
        frame.pack(pady=10)

        # Select Pet/Appointment
        tk.Label(frame, text="Select Appointment:", width=15, anchor="w", bg="#f4f6f9").grid(row=0, column=0, pady=5)
        self.appointment_combo = ttk.Combobox(frame, width=30, state="readonly")
        self.appointment_combo.grid(row=0, column=1, pady=5)
        self.appointment_combo.bind("<<ComboboxSelected>>", self.on_appointment_select)
        self.load_appointments()

        # Pet Name (auto-populated)
        tk.Label(frame, text="Pet Name:", width=15, anchor="w", bg="#f4f6f9").grid(row=1, column=0, pady=5)
        self.pet_entry = tk.Entry(frame, width=30, state="readonly")
        self.pet_entry.grid(row=1, column=1, pady=5)

        # Client Name (auto-populated)
        tk.Label(frame, text="Client Name:", width=15, anchor="w", bg="#f4f6f9").grid(row=2, column=0, pady=5)
        self.client_entry = tk.Entry(frame, width=30, state="readonly")
        self.client_entry.grid(row=2, column=1, pady=5)

        # Status (dropdown)
        tk.Label(frame, text="Status:", width=15, anchor="w", bg="#f4f6f9").grid(row=3, column=0, pady=5)
        self.status_combo = ttk.Combobox(frame, width=30, state="readonly", 
                                          values=["Appointment", "Confined", "Daily Treatment", "Discharged"])
        self.status_combo.grid(row=3, column=1, pady=5)

        # Notes
        tk.Label(frame, text="Notes:", width=15, anchor="w", bg="#f4f6f9").grid(row=4, column=0, pady=5)
        self.notes_entry = tk.Entry(frame, width=30)
        self.notes_entry.grid(row=4, column=1, pady=5)

        # Date
        tk.Label(frame, text="Date:", width=15, anchor="w", bg="#f4f6f9").grid(row=5, column=0, pady=5)
        self.date_entry = tk.Entry(frame, width=30)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.date_entry.grid(row=5, column=1, pady=5)

        tk.Button(frame, text="Update Pet Status", bg="#2563eb", fg="white", command=self.update_status).grid(row=6, column=0, columnspan=2, pady=10)

    def load_appointments(self):
        """Load appointments into dropdown"""
        try:
            rows = self.controller.db.fetch_appointments()
            appointment_display = [f"{row[1]} - {row[2]} ({row[5]})" for row in rows]
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

                # Set initial status
                self.status_combo.set("Appointment")
        except Exception as e:
            print(f"Error selecting appointment: {e}")

    def create_table(self):
        frame = tk.Frame(self, bg="#f4f6f9")
        frame.pack(pady=10, fill="both", expand=True)

        columns = ("ID", "Pet", "Client", "Status", "Date", "Notes")
        self.tree = ttk.Treeview(frame, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)

        self.tree.pack(fill="both", expand=True, padx=20, pady=20)

    def load_pet_status(self):
        """Load pet status records"""
        self.tree.delete(*self.tree.get_children())
        try:
            rows = self.controller.db.fetch_pet_status()
            for row in rows:
                self.tree.insert("", "end", values=row)
        except Exception as e:
            print(f"Error loading pet status: {e}")

    def update_status(self):
        """Update pet status and auto-create invoice when discharged"""
        pet = self.pet_entry.get()
        client = self.client_entry.get()
        status = self.status_combo.get()
        notes = self.notes_entry.get()
        date = self.date_entry.get()

        if not all([pet, client, status, date]):
            messagebox.showerror("Error", "Please fill all required fields!")
            return

        try:
            data = [pet, client, status, date, notes if notes else ""]
            self.controller.db.insert_pet_status(data)
            messagebox.showinfo("Success", f"Pet status updated to: {status}")

            # If discharged, auto-create invoice
            if status == "Discharged":
                self.auto_create_discharge_invoice(client, pet)

            # Refresh table
            self.load_pet_status()

            # Clear form
            self.appointment_combo.set("")
            self.pet_entry.config(state="normal")
            self.pet_entry.delete(0, tk.END)
            self.pet_entry.config(state="readonly")
            self.client_entry.config(state="normal")
            self.client_entry.delete(0, tk.END)
            self.client_entry.config(state="readonly")
            self.status_combo.set("")
            self.notes_entry.delete(0, tk.END)
            self.date_entry.delete(0, tk.END)
            self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        except Exception as e:
            messagebox.showerror("Error", f"Error updating status: {e}")

    def auto_create_discharge_invoice(self, client, pet):
        """Auto-create invoice when pet is discharged"""
        try:
            # Calculate total treatment costs
            treatments = self.controller.db.fetch_treatments()
            treatment_costs = {
                "Checkup": 50, "Vaccination": 75, "Surgery": 500,
                "Dental Cleaning": 150, "X-Ray": 100, "Blood Test": 80,
                "Grooming": 60, "Wound Care": 120, "Physical Therapy": 100,
                "Medication": 40
            }
            
            total_amount = 0
            for treatment in treatments:
                if treatment[3] == client and treatment[2] == pet:  # client and pet match
                    treatment_type = treatment[4]
                    total_amount += treatment_costs.get(treatment_type, 50)

            # Create invoice
            invoice_no = "INV-" + datetime.now().strftime("%Y%m%d%H%M%S")
            date = datetime.now().strftime("%Y-%m-%d")
            
            invoice_data = [invoice_no, client, pet, total_amount, date, "Unpaid"]
            self.controller.db.insert_invoice(invoice_data)
            messagebox.showinfo("Success", f"Invoice automatically created: {invoice_no}\nAmount: ${total_amount:.2f}")

            # Refresh invoices frame
            if "InvoicesFrame" in self.controller.frames:
                fn = getattr(self.controller.frames["InvoicesFrame"], "load_invoices", None)
                if callable(fn):
                    fn()
        except Exception as e:
            print(f"Error creating discharge invoice: {e}")

    def create_back_button(self):
        tk.Button(self, text="Back to Dashboard", bg="#334155", fg="white", 
                  command=lambda: self.controller.show_frame("DashboardFrame")).pack(pady=10)
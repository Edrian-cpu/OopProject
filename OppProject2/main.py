import tkinter as tk
import traceback
from datetime import datetime

from database import Database
from frames.dashboard import DashboardFrame
from frames.walkin import WalkInFrame
from frames.clients import ClientsFrame
from frames.animals import AnimalsFrame
from frames.appointments import AppointmentsFrame
from frames.invoices import InvoicesFrame
from frames.treatments import TreatmentsFrame
from frames.pet_status import PetStatusFrame
from frames.confine import ConfineFrame
from frames.reports import ReportsFrame
from frames.search import SearchFrame

class VetClinicApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Vet Clinic Management System")
        self.geometry("1000x600")
        self.configure(bg="#f4f6f9")

        # Initialize database
        self.db = Database()

        # ===== Container for all frames =====
        container = tk.Frame(self, bg="#f4f6f9")
        container.pack(fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # ===== Add all frames here =====
        self.frames = {}
        for F in (DashboardFrame, WalkInFrame, ClientsFrame, AnimalsFrame,
                  AppointmentsFrame, InvoicesFrame, TreatmentsFrame, PetStatusFrame, ConfineFrame, ReportsFrame, SearchFrame):
            try:
                frame = F(container, self)
                self.frames[F.__name__] = frame
                frame.grid(row=0, column=0, sticky="nsew")
            except Exception:
                print(f"❌ Error creating frame: {F.__name__}")
                traceback.print_exc()
                raise

        # Show the dashboard first
        self.show_frame("DashboardFrame")

    def show_frame(self, name):
        self.frames[name].tkraise()

    def process_walkin(self, walkin_data):
        """Process walk-in and create related records in all tables"""
        try:
            client_name, contact, address, pet_name, species, breed, age, reason, date = walkin_data

            # normalize and clean strings
            client_name = client_name.strip() if isinstance(client_name, str) else client_name
            contact = contact.strip() if isinstance(contact, str) else contact
            address = address.strip() if isinstance(address, str) else address
            pet_name = pet_name.strip() if isinstance(pet_name, str) else pet_name
            species = (species or "").strip()
            breed = (breed or "").strip()
            reason = reason.strip() if isinstance(reason, str) else reason
            date = date.strip() if isinstance(date, str) else date

            # Normalize species to title case and specifically standardize 'dog'
            if species:
                species_norm = species.lower()
                if species_norm == "dog":
                    species = "Dog"
                elif species_norm == "cat":
                    species = "Cat"
                else:
                    species = species.title()

            # Normalize breed: keep common dog-breed formatting (Title Case)
            if breed:
                breed = " ".join([w.capitalize() for w in breed.split()])

            # Ensure age is integer (if provided)
            try:
                age = int(age)
            except Exception:
                age = None

            # 1. Add to Clients table
            client_data = [client_name, contact, address]
            self.db.insert_client(client_data)

            # 2. Add to Animals table (use normalized species/breed)
            animal_data = [pet_name, species, breed, age, client_name]
            self.db.insert_animal(animal_data)

            # 3. Add to Appointments table
            appointment_data = [client_name, pet_name, date, "09:00", reason]
            self.db.insert_appointment(appointment_data)

            # IMPORTANT: Do NOT create a treatment or invoice record here.
            # Treatments and invoices should be created only from the Treatments/Invoices UI.

            # Refresh all frames
            self.refresh_all_frames()

            return True
        except Exception as e:
            print(f"Error processing walk-in: {e}")
            return False

    def add_treatment_cost(self, client_name, treatment_reason, cost):
        """Add treatment cost to invoice and auto-connect. If no invoice exists, create one."""
        try:
            # Get treatment cost based on reason/type
            treatment_costs = {
                "Checkup": 50,
                "Vaccination": 75,
                "Surgery": 500,
                "Dental Cleaning": 150,
                "X-Ray": 100,
                "Blood Test": 80,
                "Grooming": 60,
                "Wound Care": 120,
                "Physical Therapy": 100,
                "Medication": 40
            }

            treatment_cost = treatment_costs.get(treatment_reason, cost if cost else 50)

            # Find invoice for this client
            invoices = self.db.fetch_invoices()
            found = False
            for invoice in invoices:
                if invoice[2] == client_name:  # invoice[2] is client name
                    current_amount = invoice[4]  # invoice[4] is amount
                    new_amount = current_amount + treatment_cost

                    # Update invoice amount
                    self.db.update_invoice_amount(invoice[0], new_amount)
                    found = True
                    break

            # If no invoice exists for the client, create one now
            if not found:
                invoice_no = "INV-" + datetime.now().strftime("%Y%m%d%H%M%S")
                date = datetime.now().strftime("%Y-%m-%d")
                # Pet unknown here — leave blank or you can lookup latest pet for client
                pet = ""
                self.db.insert_invoice([invoice_no, client_name, pet, treatment_cost, date, "Unpaid"])

            # Refresh invoice frame
            if "InvoicesFrame" in self.frames:
                fn = getattr(self.frames["InvoicesFrame"], "load_invoices", None)
                if callable(fn):
                    fn()

        except Exception as e:
            print(f"Error adding treatment cost: {e}")

    def mark_invoice_paid(self, invoice_id):
        """Mark invoice as paid"""
        try:
            self.db.update_invoice_status(invoice_id, "Paid")
            fn = getattr(self.frames.get("InvoicesFrame"), "load_invoices", None)
            if callable(fn):
                fn()
        except Exception as e:
            print(f"Error marking invoice as paid: {e}")

    def mark_invoice_unpaid(self, invoice_id):
        """Mark invoice as unpaid"""
        try:
            self.db.update_invoice_status(invoice_id, "Unpaid")
            fn = getattr(self.frames.get("InvoicesFrame"), "load_invoices", None)
            if callable(fn):
                fn()
        except Exception as e:
            print(f"Error marking invoice as unpaid: {e}")

    def print_receipt(self, invoice_id):
        """Generate and print receipt"""
        try:
            invoice = self.db.fetch_invoice_by_id(invoice_id)
            if invoice:
                receipt_text = self.generate_receipt(invoice)
                self.show_receipt_window(receipt_text)
        except Exception as e:
            print(f"Error printing receipt: {e}")

    def generate_receipt(self, invoice):
        """Generate receipt text from invoice data"""
        receipt = f"""
{'='*50}
         VET CLINIC RECEIPT
{'='*50}

Invoice No:      {invoice[1]}
Date:            {invoice[5]}
Status:          {invoice[6] if len(invoice) > 6 else 'Unknown'}

{'='*50}
CLIENT INFORMATION
{'='*50}
Client Name:     {invoice[2]}
Pet Name:        {invoice[3]}

{'='*50}
INVOICE DETAILS
{'='*50}
Amount:          ${invoice[4]:.2f}

{'='*50}
Thank you for visiting!
{'='*50}
"""
        return receipt

    def show_receipt_window(self, receipt_text):
        """Display receipt in a new window"""
        receipt_win = tk.Toplevel(self)
        receipt_win.title("Receipt")
        receipt_win.geometry("600x400")

        text_widget = tk.Text(receipt_win, font=("Courier", 10), bg="white")
        text_widget.pack(fill="both", expand=True, padx=10, pady=10)
        text_widget.insert(1.0, receipt_text)
        text_widget.config(state="disabled")

        button_frame = tk.Frame(receipt_win)
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="Print", bg="#2563eb", fg="white",
                  command=lambda: self.print_to_printer(receipt_text)).pack(side="left", padx=5)
        tk.Button(button_frame, text="Close", bg="#334155", fg="white",
                  command=receipt_win.destroy).pack(side="left", padx=5)

    def print_to_printer(self, receipt_text):
        """Send receipt to printer"""
        try:
            import subprocess
            # Windows print using notepad
            with open("temp_receipt.txt", "w") as f:
                f.write(receipt_text)
            subprocess.Popen(["notepad", "/p", "temp_receipt.txt"])
        except Exception as e:
            print(f"Error printing: {e}")

    def refresh_all_frames(self):
        """Refresh all tables in open frames (call methods only when present)"""
        try:
            for name, frame in self.frames.items():
                # call any of these if implemented on the frame
                for method in ("load_walkins", "load_clients", "load_animals",
                               "load_appointments", "load_treatments", "load_invoices", "load_confined"):
                    fn = getattr(frame, method, None)
                    if callable(fn):
                        try:
                            fn()
                        except Exception as e:
                            print(f"Error refreshing {name}.{method}: {e}")
        except Exception as e:
            print(f"Error refreshing frames: {e}")

if __name__ == "__main__":
    app = VetClinicApp()
    app.mainloop()

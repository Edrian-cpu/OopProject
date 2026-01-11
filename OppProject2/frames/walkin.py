import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

class WalkInFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#f4f6f9")
        self.controller = controller

        tk.Label(self, text="Walk-In / New Appointment", font=("Segoe UI", 20), bg="#f4f6f9").pack(pady=10)

        self.create_form()
        self.create_back_button()

    def create_form(self):
        frame = tk.Frame(self, bg="#f4f6f9")
        frame.pack(pady=10)

        # Basic fields
        labels = ["Client Name", "Contact", "Address", "Pet Name", "Age"]
        self.entries = {}
        for i, label in enumerate(labels):
            tk.Label(frame, text=label+":", width=15, anchor="w", bg="#f4f6f9").grid(row=i, column=0, pady=5)
            entry = tk.Entry(frame, width=30)
            entry.grid(row=i, column=1, pady=5)
            self.entries[label] = entry

        # Rows for species, breed, and reason
        species_row = len(labels)
        breed_row = species_row + 1
        reason_row = breed_row + 1

        # Species combobox (more species added)
        tk.Label(frame, text="Species:", width=15, anchor="w", bg="#f4f6f9").grid(row=species_row, column=0, pady=5)
        species_options = ["Dog", "Cat", "Bird", "Reptile", "Small Mammal", "Fish", "Other"]
        self.species_combo = ttk.Combobox(frame, width=28, state="readonly", values=species_options)
        self.species_combo.grid(row=species_row, column=1, pady=5)
        self.species_combo.bind("<<ComboboxSelected>>", self.on_species_change)
        self.entries["Species"] = self.species_combo

        # Breed widgets: combobox for known species, entry for free text
        tk.Label(frame, text="Breed:", width=15, anchor="w", bg="#f4f6f9").grid(row=breed_row, column=0, pady=5)

        # Breed lists per species
        self.breeds_by_species = {
            "dog": ["Labrador Retriever", "German Shepherd", "Golden Retriever", "Bulldog", "Beagle", "Poodle", "Rottweiler", "Mixed"],
            "cat": ["Domestic Shorthair", "Domestic Longhair", "Persian", "Maine Coon", "Siamese", "Ragdoll", "Bengal", "Mixed"],
            "bird": ["Parakeet", "Cockatiel", "Lovebird", "Canary", "Finch", "Parrot", "Other"],
            "reptile": ["Bearded Dragon", "Leopard Gecko", "Corn Snake", "Ball Python", "Other"],
            "small mammal": ["Rabbit", "Guinea Pig", "Hamster", "Ferret", "Chinchilla", "Other"],
            "fish": ["Goldfish", "Betta", "Guppy", "Tetra", "Other"]
        }

        self.breed_combo = ttk.Combobox(frame, width=28, state="readonly", values=[])
        self.breed_entry = tk.Entry(frame, width=30)

        # Default show generic entry until species selected
        self.breed_entry.grid(row=breed_row, column=1, pady=5)
        self.entries["Breed"] = self.breed_entry

        # Reason combobox (vet clinic services)
        tk.Label(frame, text="Reason:", width=15, anchor="w", bg="#f4f6f9").grid(row=reason_row, column=0, pady=5)
        reason_options = [
            "Checkup",
            "Vaccination",
            "Surgery",
            "Dental Cleaning",
            "X-Ray",
            "Blood Test",
            "Grooming",
            "Wound Care",
            "Physical Therapy",
            "Medication",
            "Emergency",
            "Injury",
            "Illness",
            "Post-Surgery Follow-up",
            "Behavioral Consultation",
            "Nutrition Consultation"
        ]
        self.reason_combo = ttk.Combobox(frame, width=28, state="readonly", values=reason_options)
        self.reason_combo.grid(row=reason_row, column=1, pady=5)
        self.entries["Reason"] = self.reason_combo

        tk.Button(frame, text="Add Walk-In", bg="#2563eb", fg="white", command=self.add_walkin).grid(row=reason_row+1, column=0, columnspan=2, pady=10)

    def on_species_change(self, event):
        """Show appropriate breed widget for selected species."""
        species = (self.species_combo.get() or "").strip().lower()

        # hide both then show correct one
        try:
            self.breed_combo.grid_forget()
        except Exception:
            pass
        try:
            self.breed_entry.grid_forget()
        except Exception:
            pass

        # compute rows as in create_form
        species_row = len(["Client Name", "Contact", "Address", "Pet Name", "Age"])
        breed_row = species_row + 1

        if species in self.breeds_by_species:
            values = self.breeds_by_species.get(species, [])
            self.breed_combo['values'] = values
            self.breed_combo.set("")  # clear previous
            self.breed_combo.grid(row=breed_row, column=1, pady=5)
            self.entries["Breed"] = self.breed_combo
        else:
            # free-text breed
            self.breed_entry.grid(row=breed_row, column=1, pady=5)
            self.entries["Breed"] = self.breed_entry

    def add_walkin(self):
        # Labels expected for data order
        labels = ["Client Name", "Contact", "Address", "Pet Name", "Species", "Breed", "Age", "Reason"]
        data = []
        for label in labels:
            widget = self.entries.get(label)
            if widget is None:
                data.append("")
                continue
            try:
                value = widget.get().strip()
            except Exception:
                value = str(widget.get()).strip()
            data.append(value)

        if not all(data):
            messagebox.showerror("Error", "All fields are required!")
            return

        # Validate age is a number
        try:
            data[6] = int(data[6])
        except Exception:
            messagebox.showerror("Error", "Age must be a number!")
            return

        # append current date
        data.append(datetime.now().strftime("%Y-%m-%d"))
        # data format now: [client_name, contact, address, pet_name, species, breed, age, reason, date]

        # Insert walk-in and process to other tables
        try:
            self.controller.db.insert_walkin(data)
            self.controller.process_walkin(data)
            messagebox.showinfo("Success", "Walk-In added and records created in all modules!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add walk-in: {e}")
            return

        # Clear form
        for key, widget in list(self.entries.items()):
            try:
                if isinstance(widget, ttk.Combobox):
                    widget.set("")
                else:
                    widget.delete(0, tk.END)
            except Exception:
                pass

    def create_back_button(self):
        tk.Button(self, text="Back to Dashboard", bg="#334155", fg="white",
                  command=lambda: self.controller.show_frame("DashboardFrame")).pack(pady=10)
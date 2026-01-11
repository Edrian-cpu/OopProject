import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta

class ReportsFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#f4f6f9")
        self.controller = controller

        tk.Label(self, text="Reports Module", font=("Segoe UI", 20), bg="#f4f6f9").pack(pady=10)

        self.create_buttons()
        self.create_report_area()
        self.create_back_button()

    def create_buttons(self):
        """Create report generation buttons"""
        button_frame = tk.Frame(self, bg="#f4f6f9")
        button_frame.pack(pady=10, fill="x", padx=10)

        # Row 1
        tk.Button(button_frame, text="Daily Revenue", bg="#2563eb", fg="white", width=18,
                  command=self.generate_daily_revenue).grid(row=0, column=0, padx=5, pady=5)
        tk.Button(button_frame, text="Monthly Revenue", bg="#10b981", fg="white", width=18,
                  command=self.generate_monthly_revenue).grid(row=0, column=1, padx=5, pady=5)
        tk.Button(button_frame, text="Treatment Summary", bg="#f59e0b", fg="white", width=18,
                  command=self.generate_treatment_summary).grid(row=0, column=2, padx=5, pady=5)
        tk.Button(button_frame, text="Client Summary", bg="#8b5cf6", fg="white", width=18,
                  command=self.generate_client_summary).grid(row=0, column=3, padx=5, pady=5)

        # Row 2
        tk.Button(button_frame, text="Appointment Summary", bg="#ec4899", fg="white", width=18,
                  command=self.generate_appointment_summary).grid(row=1, column=0, padx=5, pady=5)
        tk.Button(button_frame, text="Species Report", bg="#14b8a6", fg="white", width=18,
                  command=self.generate_species_report).grid(row=1, column=1, padx=5, pady=5)
        tk.Button(button_frame, text="Outstanding Invoices", bg="#f97316", fg="white", width=18,
                  command=self.generate_outstanding_invoices).grid(row=1, column=2, padx=5, pady=5)
        tk.Button(button_frame, text="Print Report", bg="#6366f1", fg="white", width=18,
                  command=self.print_report).grid(row=1, column=3, padx=5, pady=5)

    def create_report_area(self):
        """Create area to display reports"""
        frame = tk.Frame(self, bg="white")
        frame.pack(pady=10, fill="both", expand=True, padx=20)

        # Scrollbar
        scrollbar = ttk.Scrollbar(frame)
        scrollbar.pack(side="right", fill="y")

        # Text widget
        self.report_text = tk.Text(frame, font=("Courier", 10), bg="white", yscrollcommand=scrollbar.set)
        self.report_text.pack(fill="both", expand=True)
        scrollbar.config(command=self.report_text.yview)

    def generate_daily_revenue(self):
        """Generate daily revenue report"""
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            invoices = self.controller.db.fetch_invoices()
            
            total_revenue = 0
            paid_revenue = 0
            unpaid_revenue = 0
            count = 0
            
            for invoice in invoices:
                if invoice[5] == today:  # invoice[5] is date
                    count += 1
                    amount = invoice[4]  # invoice[4] is amount
                    total_revenue += amount
                    
                    if invoice[6] == "Paid":  # invoice[6] is status
                        paid_revenue += amount
                    else:
                        unpaid_revenue += amount

            report = f"""
{'='*60}
                   DAILY REVENUE REPORT
{'='*60}
Date:                    {today}
Generated:               {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

{'='*60}
SUMMARY
{'='*60}
Total Invoices:          {count}
Total Revenue:           ${total_revenue:.2f}
Paid Revenue:            ${paid_revenue:.2f}
Unpaid Revenue:          ${unpaid_revenue:.2f}

{'='*60}
END OF REPORT
{'='*60}
"""
            self.display_report(report)
        except Exception as e:
            messagebox.showerror("Error", f"Error generating report: {e}")

    def generate_monthly_revenue(self):
        """Generate monthly revenue report"""
        try:
            today = datetime.now()
            month_start = today.strftime("%Y-%m-01")
            month_end = today.strftime("%Y-%m-%d")
            
            invoices = self.controller.db.fetch_invoices()
            
            total_revenue = 0
            paid_revenue = 0
            unpaid_revenue = 0
            count = 0
            
            for invoice in invoices:
                invoice_date = invoice[5]  # invoice[5] is date
                if month_start <= invoice_date <= month_end:
                    count += 1
                    amount = invoice[4]  # invoice[4] is amount
                    total_revenue += amount
                    
                    if invoice[6] == "Paid":  # invoice[6] is status
                        paid_revenue += amount
                    else:
                        unpaid_revenue += amount

            month_name = today.strftime("%B %Y")
            
            report = f"""
{'='*60}
                   MONTHLY REVENUE REPORT
{'='*60}
Month:                   {month_name}
Period:                  {month_start} to {month_end}
Generated:               {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

{'='*60}
SUMMARY
{'='*60}
Total Invoices:          {count}
Total Revenue:           ${total_revenue:.2f}
Paid Revenue:            ${paid_revenue:.2f}
Unpaid Revenue:          ${unpaid_revenue:.2f}

{'='*60}
END OF REPORT
{'='*60}
"""
            self.display_report(report)
        except Exception as e:
            messagebox.showerror("Error", f"Error generating report: {e}")

    def generate_treatment_summary(self):
        """Generate treatment summary report"""
        try:
            treatments = self.controller.db.fetch_treatments()
            
            treatment_types = {}
            total_treatments = 0
            
            for treatment in treatments:
                treatment_type = treatment[4]  # treatment[4] is treatment_type
                total_treatments += 1
                
                if treatment_type not in treatment_types:
                    treatment_types[treatment_type] = 0
                treatment_types[treatment_type] += 1

            # Calculate revenue by treatment
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

            report = f"""
{'='*60}
                   TREATMENT SUMMARY REPORT
{'='*60}
Generated:               {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

{'='*60}
TREATMENT BREAKDOWN
{'='*60}
Total Treatments:        {total_treatments}

"""
            total_treatment_revenue = 0
            for treatment_type, count in sorted(treatment_types.items()):
                cost = treatment_costs.get(treatment_type, 0)
                revenue = cost * count
                total_treatment_revenue += revenue
                report += f"{treatment_type:<30} {count:>5} (${revenue:.2f})\n"

            report += f"""
{'='*60}
Total Treatment Revenue: ${total_treatment_revenue:.2f}
{'='*60}
END OF REPORT
{'='*60}
"""
            self.display_report(report)
        except Exception as e:
            messagebox.showerror("Error", f"Error generating report: {e}")

    def generate_client_summary(self):
        """Generate client summary report"""
        try:
            clients = self.controller.db.fetch_clients()
            animals = self.controller.db.fetch_animals()
            invoices = self.controller.db.fetch_invoices()
            
            total_clients = len(clients)
            total_animals = len(animals)
            total_invoices = len(invoices)
            
            # Count animals by species
            species_count = {}
            for animal in animals:
                species = animal[2]  # animal[2] is species
                if species not in species_count:
                    species_count[species] = 0
                species_count[species] += 1

            # Calculate payment status
            paid_count = sum(1 for inv in invoices if inv[6] == "Paid")
            unpaid_count = sum(1 for inv in invoices if inv[6] == "Unpaid")

            report = f"""
{'='*60}
                   CLIENT SUMMARY REPORT
{'='*60}
Generated:               {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

{'='*60}
STATISTICS
{'='*60}
Total Clients:           {total_clients}
Total Animals:           {total_animals}
Total Invoices:          {total_invoices}

{'='*60}
ANIMALS BY SPECIES
{'='*60}
"""
            for species, count in sorted(species_count.items()):
                report += f"{species:<30} {count:>5}\n"

            report += f"""
{'='*60}
PAYMENT STATUS
{'='*60}
Paid Invoices:           {paid_count}
Unpaid Invoices:         {unpaid_count}

{'='*60}
END OF REPORT
{'='*60}
"""
            self.display_report(report)
        except Exception as e:
            messagebox.showerror("Error", f"Error generating report: {e}")

    def generate_appointment_summary(self):
        """Generate appointment summary report"""
        try:
            appointments = self.controller.db.fetch_appointments()
            
            total_appointments = len(appointments)
            reason_count = {}
            
            for appt in appointments:
                reason = appt[5]  # appt[5] is reason
                if reason not in reason_count:
                    reason_count[reason] = 0
                reason_count[reason] += 1

            report = f"""
{'='*60}
                   APPOINTMENT SUMMARY REPORT
{'='*60}
Generated:               {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

{'='*60}
APPOINTMENT STATISTICS
{'='*60}
Total Appointments:      {total_appointments}

{'='*60}
APPOINTMENTS BY REASON
{'='*60}
"""
            for reason, count in sorted(reason_count.items()):
                report += f"{reason:<40} {count:>5}\n"

            report += f"""
{'='*60}
END OF REPORT
{'='*60}
"""
            self.display_report(report)
        except Exception as e:
            messagebox.showerror("Error", f"Error generating report: {e}")

    def generate_species_report(self):
        """Generate detailed species report"""
        try:
            animals = self.controller.db.fetch_animals()
            
            species_data = {}
            
            for animal in animals:
                species = animal[2]  # animal[2] is species
                breed = animal[3]  # animal[3] is breed
                pet_name = animal[1]  # animal[1] is pet_name
                owner = animal[5]  # animal[5] is owner_name
                
                if species not in species_data:
                    species_data[species] = []
                
                species_data[species].append({
                    'name': pet_name,
                    'breed': breed,
                    'owner': owner
                })

            report = f"""
{'='*60}
                   SPECIES DETAILED REPORT
{'='*60}
Generated:               {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

"""
            for species in sorted(species_data.keys()):
                animals_list = species_data[species]
                report += f"""
{'='*60}
{species.upper()} ({len(animals_list)} total)
{'='*60}
"""
                for animal in animals_list:
                    report += f"Name: {animal['name']:<20} Breed: {animal['breed']:<25} Owner: {animal['owner']}\n"

            report += f"""
{'='*60}
END OF REPORT
{'='*60}
"""
            self.display_report(report)
        except Exception as e:
            messagebox.showerror("Error", f"Error generating report: {e}")

    def generate_outstanding_invoices(self):
        """Generate outstanding (unpaid) invoices report"""
        try:
            invoices = self.controller.db.fetch_invoices()
            
            outstanding = [inv for inv in invoices if inv[6] == "Unpaid"]
            total_outstanding = sum(inv[4] for inv in outstanding)

            report = f"""
{'='*60}
                   OUTSTANDING INVOICES REPORT
{'='*60}
Generated:               {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

{'='*60}
UNPAID INVOICES: {len(outstanding)}
TOTAL OUTSTANDING: ${total_outstanding:.2f}
{'='*60}

"""
            for inv in sorted(outstanding, key=lambda x: x[5]):
                report += f"Invoice: {inv[1]:<15} Client: {inv[2]:<20} Amount: ${inv[4]:>8.2f}  Date: {inv[5]}\n"

            report += f"""
{'='*60}
END OF REPORT
{'='*60}
"""
            self.display_report(report)
        except Exception as e:
            messagebox.showerror("Error", f"Error generating report: {e}")

    def display_report(self, report_text):
        """Display report in text widget"""
        self.report_text.config(state="normal")
        self.report_text.delete(1.0, tk.END)
        self.report_text.insert(1.0, report_text)
        self.report_text.config(state="disabled")

    def print_report(self):
        """Print the currently displayed report"""
        try:
            report_text = self.report_text.get(1.0, tk.END)
            if not report_text.strip():
                messagebox.showwarning("Warning", "No report to print!")
                return
            
            import subprocess
            with open("temp_report.txt", "w") as f:
                f.write(report_text)
            subprocess.Popen(["notepad", "/p", "temp_report.txt"])
            messagebox.showinfo("Success", "Report sent to printer!")
        except Exception as e:
            messagebox.showerror("Error", f"Error printing report: {e}")

    def create_back_button(self):
        tk.Button(self, text="Back to Dashboard", bg="#334155", fg="white", 
                  command=lambda: self.controller.show_frame("DashboardFrame")).pack(pady=10)
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

class InvoicesFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#f4f6f9")
        self.controller = controller

        tk.Label(self, text="Invoices Module", font=("Segoe UI", 20), bg="#f4f6f9").pack(pady=10)

        self.create_form()
        self.create_table()
        self.load_invoices()
        self.create_back_button()

    def create_form(self):
        frame = tk.Frame(self, bg="#f4f6f9")
        frame.pack(pady=10)

        # Select Client dropdown
        tk.Label(frame, text="Select Client:", width=15, anchor="w", bg="#f4f6f9").grid(row=0, column=0, pady=5)
        self.client_combo = ttk.Combobox(frame, width=30, state="readonly")
        self.client_combo.grid(row=0, column=1, pady=5)
        self.client_combo.bind("<<ComboboxSelected>>", self.on_client_select)
        self.load_clients()

        # Pet Name (auto-populated)
        tk.Label(frame, text="Pet Name:", width=15, anchor="w", bg="#f4f6f9").grid(row=1, column=0, pady=5)
        self.pet_entry = tk.Entry(frame, width=30, state="readonly")
        self.pet_entry.grid(row=1, column=1, pady=5)

        # Total Amount (auto-calculated from treatments)
        tk.Label(frame, text="Total Amount:", width=15, anchor="w", bg="#f4f6f9").grid(row=2, column=0, pady=5)
        self.amount_entry = tk.Entry(frame, width=30, state="readonly")
        self.amount_entry.grid(row=2, column=1, pady=5)

        # Date (auto-populated)
        tk.Label(frame, text="Date:", width=15, anchor="w", bg="#f4f6f9").grid(row=3, column=0, pady=5)
        self.date_entry = tk.Entry(frame, width=30)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.date_entry.grid(row=3, column=1, pady=5)

        tk.Button(frame, text="Create Invoice", bg="#2563eb", fg="white", command=self.add_invoice).grid(row=4, column=0, columnspan=2, pady=10)

    def load_clients(self):
        """Load clients into dropdown"""
        try:
            rows = self.controller.db.fetch_clients()
            client_names = [row[1] for row in rows]  # Get client names from second column
            self.client_combo['values'] = client_names
            self.client_data = {row[1]: row for row in rows}  # Store full client data
        except Exception as e:
            print(f"Error loading clients: {e}")

    def on_client_select(self, event):
        """Auto-populate pet name and total amount when client is selected"""
        try:
            selected_client = self.client_combo.get()
            if selected_client in self.client_data:
                # Fetch pet for this client
                rows = self.controller.db.fetch_animals()
                for row in rows:
                    if row[5] == selected_client:  # row[5] is owner_name
                        self.pet_entry.config(state="normal")
                        self.pet_entry.delete(0, tk.END)
                        self.pet_entry.insert(0, row[1])  # row[1] is pet_name
                        self.pet_entry.config(state="readonly")
                        break
                
                # Calculate total from treatments for this client
                total_amount = self.calculate_treatment_total(selected_client)
                self.amount_entry.config(state="normal")
                self.amount_entry.delete(0, tk.END)
                self.amount_entry.insert(0, str(total_amount))
                self.amount_entry.config(state="readonly")
        except Exception as e:
            print(f"Error selecting client: {e}")

    def calculate_treatment_total(self, client_name):
        """Calculate total amount from all treatments for this client"""
        try:
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
            
            treatments = self.controller.db.fetch_treatments()
            total = 0
            for treatment in treatments:
                # treatment format: (id, reason, pet, client, treatment_type, date, confined, notes)
                if treatment[3] == client_name:  # treatment[3] is client name
                    treatment_type = treatment[4]  # treatment[4] is treatment_type
                    total += treatment_costs.get(treatment_type, 50)
            
            return total
        except Exception as e:
            print(f"Error calculating total: {e}")
            return 0

    def create_table(self):
        frame = tk.Frame(self, bg="#f4f6f9")
        frame.pack(pady=10, fill="both", expand=True)

        columns = ("ID", "Invoice No", "Client", "Pet", "Amount", "Date", "Status", "Action")
        self.tree = ttk.Treeview(frame, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            if col == "Action":
                self.tree.column(col, width=150)
            else:
                self.tree.column(col, width=100)

        self.tree.pack(fill="both", expand=True, padx=20, pady=20)
        self.tree.bind("<Double-1>", self.on_row_double_click)

    def load_invoices(self):
        self.tree.delete(*self.tree.get_children())
        rows = self.controller.db.fetch_invoices()
        for row in rows:
            # row = (id, invoice_no, client, pet, amount, date, status)
            self.tree.insert("", "end", values=(
                row[0], row[1], row[2], row[3], f"${row[4]:.2f}", row[5], row[6], "Click to manage"
            ))

    def on_row_double_click(self, event):
        """Show options on double-click"""
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            values = self.tree.item(item, "values")
            invoice_id = values[0]
            status = values[6]
            
            self.show_invoice_options(invoice_id, status)

    def show_invoice_options(self, invoice_id, status):
        """Show invoice management options"""
        options_win = tk.Toplevel(self)
        options_win.title(f"Invoice {invoice_id} - Options")
        options_win.geometry("350x280")

        tk.Label(options_win, text=f"Invoice ID: {invoice_id}", font=("Arial", 12, "bold")).pack(pady=10)
        tk.Label(options_win, text=f"Current Status: {status}", font=("Arial", 11)).pack(pady=5)

        button_frame = tk.Frame(options_win)
        button_frame.pack(pady=20)

        # Mark as Paid button
        if status == "Unpaid":
            tk.Button(button_frame, text="✓ Mark as Paid", bg="#2563eb", fg="white", width=25,
                      command=lambda: self.mark_paid_and_close(invoice_id, options_win)).pack(pady=5)
        else:
            tk.Button(button_frame, text="✗ Mark as Unpaid", bg="#f59e0b", fg="white", width=25,
                      command=lambda: self.mark_unpaid_and_close(invoice_id, options_win)).pack(pady=5)

        # Print Receipt button
        tk.Button(button_frame, text="🖨️  Print Receipt", bg="#10b981", fg="white", width=25,
                  command=lambda: self.print_receipt_and_close(invoice_id, options_win)).pack(pady=5)

        # View Invoice button
        tk.Button(button_frame, text="👁️  View Invoice", bg="#8b5cf6", fg="white", width=25,
                  command=lambda: self.view_invoice(invoice_id)).pack(pady=5)

        # Close button
        tk.Button(button_frame, text="Close", bg="#6b7280", fg="white", width=25,
                  command=options_win.destroy).pack(pady=5)

    def mark_paid_and_close(self, invoice_id, window):
        """Mark invoice as paid and close window"""
        self.controller.mark_invoice_paid(invoice_id)
        self.load_invoices()
        window.destroy()
        messagebox.showinfo("Success", "Invoice marked as Paid!")

    def mark_unpaid_and_close(self, invoice_id, window):
        """Mark invoice as unpaid and close window"""
        self.controller.mark_invoice_unpaid(invoice_id)
        self.load_invoices()
        window.destroy()
        messagebox.showinfo("Success", "Invoice marked as Unpaid!")

    def print_receipt_and_close(self, invoice_id, window):
        """Print receipt and close window"""
        self.controller.print_receipt(invoice_id)
        window.destroy()
        messagebox.showinfo("Success", "Receipt printed!")

    def view_invoice(self, invoice_id):
        """View invoice details"""
        try:
            invoice = self.controller.db.fetch_invoice_by_id(invoice_id)
            if invoice:
                details = f"""
Invoice Details:
{'='*50}
Invoice No:      {invoice[1]}
Client:          {invoice[2]}
Pet:             {invoice[3]}
Amount:          ${invoice[4]:.2f}
Date:            {invoice[5]}
Status:          {invoice[6]}
{'='*50}
"""
                messagebox.showinfo("Invoice Details", details)
        except Exception as e:
            messagebox.showerror("Error", f"Error viewing invoice: {e}")

    def add_invoice(self):
        """Add invoice and refresh table"""
        client = self.client_combo.get()
        pet = self.pet_entry.get()
        amount = self.amount_entry.get()
        date = self.date_entry.get()

        if not all([client, pet, amount, date]):
            messagebox.showerror("Error", "All fields are required!")
            return

        try:
            amount = float(amount)
        except:
            messagebox.showerror("Error", "Amount must be a number!")
            return

        # Generate invoice number
        invoice_no = "INV-" + date.replace("-", "")
        
        data = [invoice_no, client, pet, amount, date, "Unpaid"]
        self.controller.db.insert_invoice(data)
        messagebox.showinfo("Success", "Invoice created successfully!")

        # Clear form
        self.client_combo.set("")
        self.pet_entry.config(state="normal")
        self.pet_entry.delete(0, tk.END)
        self.pet_entry.config(state="readonly")
        self.amount_entry.config(state="normal")
        self.amount_entry.delete(0, tk.END)
        self.amount_entry.config(state="readonly")
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

        # Refresh table
        self.load_invoices()

    def create_back_button(self):
        tk.Button(self, text="Back to Dashboard", bg="#334155", fg="white", 
                  command=lambda: self.controller.show_frame("DashboardFrame")).pack(pady=10)

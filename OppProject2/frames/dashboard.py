# ...existing code...
import tkinter as tk
import os, sys

# try to import matplotlib; if missing, disable plotting and show a placeholder
try:
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    MATPLOTLIB_AVAILABLE = True
except Exception:
    Figure = None
    FigureCanvasTkAgg = None
    MATPLOTLIB_AVAILABLE = False

class DashboardFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#f4f6f9")
        self.controller = controller

        self.create_sidebar()
        self.create_header()
        self.create_graph_area()

    # ===== Sidebar =====
    def create_sidebar(self):
        sidebar = tk.Frame(self, bg="#1e293b", width=230)
        sidebar.pack(side="left", fill="y")

        tk.Label(
            sidebar,
            text="🐾 Vet Clinic",
            bg="#1e293b",
            fg="white",
            font=("Segoe UI", 16, "bold")
        ).pack(pady=30)

        buttons = [
            ("Dashboard", "DashboardFrame"),
            ("Walk-In", "WalkInFrame"),
            ("Clients", "ClientsFrame"),
            ("Animals", "AnimalsFrame"),
            ("Appointments", "AppointmentsFrame"),
            ("Treatments", "TreatmentsFrame"),
            ("Invoices", "InvoicesFrame"),
            ("Reports", "ReportsFrame")
        ]

        for text, frame_name in buttons:
            tk.Button(
                sidebar,
                text=text,
                command=lambda f=frame_name: self.controller.show_frame(f),
                bg="#334155",
                fg="white",
                relief="flat",
                height=2,
                cursor="hand2"
            ).pack(fill="x", padx=15, pady=5)

    # ===== Header =====
    def create_header(self):
        header = tk.Frame(self, bg="white", height=70)
        header.pack(side="top", fill="x")
        tk.Label(
            header,
            text="Dashboard",
            font=("Segoe UI", 18, "bold"),
            bg="white"
        ).place(x=20, y=18)

    # ===== Graph Area =====
    def create_graph_area(self):
        main_frame = tk.Frame(self, bg="#f4f6f9")
        main_frame.pack(expand=True, fill="both", padx=10, pady=10)

        self.plot_graph(main_frame)

        # navigation buttons removed — keep a simple info label instead
        nav_frame = tk.Frame(self, bg="#f4f6f9")
        nav_frame.pack(pady=10)
        tk.Label(nav_frame, text="Use the sidebar or menu to navigate modules.", bg="#f4f6f9", fg="#374151").pack()

    # ===== Plot Graph =====
    def plot_graph(self, parent):
        # Sample data: Walk-ins per day
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        walkins = [5, 8, 3, 6, 7, 2, 4]  # Replace with real database data later

        if MATPLOTLIB_AVAILABLE:
            fig = Figure(figsize=(7, 5), dpi=100)
            ax = fig.add_subplot(111)
            ax.bar(days, walkins, color="#2563eb")
            ax.set_title("Walk-Ins per Day")
            ax.set_ylabel("Number of Walk-Ins")

            canvas = FigureCanvasTkAgg(fig, master=parent)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
        else:
            # fallback UI when matplotlib is not installed
            msg = (
                "Matplotlib is not installed.\n"
                "Install it to enable charts: pip install matplotlib"
            )
            tk.Label(parent, text=msg, bg="#f4f6f9", fg="#334155", font=("Segoe UI", 12), justify="center").pack(expand=True, fill="both")
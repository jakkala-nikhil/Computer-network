import tkinter as tk
from tkinter import ttk
import random
import time
from datetime import datetime


# ============================================================
# CSMA/CD STAR TOPOLOGY SIMULATION
# ============================================================

class CSMACDSimulation:

    def __init__(self, root):
        self.root = root
        self.root.title("CSMA/CD Simulation - Star Topology")
        self.root.geometry("1200x750")
        self.root.configure(bg="#f4f6f8")

        # -----------------------------
        # Simulation Variables
        # -----------------------------
        self.hosts = ["Host 1", "Host 2", "Host 3", "Host 4"]

        self.host_colors = {
            "Host 1": "#3498db",
            "Host 2": "#2ecc71",
            "Host 3": "#e67e22",
            "Host 4": "#9b59b6"
        }

        self.transmission_attempts = 0
        self.collisions = 0
        self.successful_transmissions = 0
        self.failed_transmissions = 0

        self.frame_number = 0
        self.running = False

        self.log_file = "csma_log.txt"

        # -----------------------------
        # Header
        # -----------------------------
        title = tk.Label(
            root,
            text="CSMA/CD Simulation in Star Topology",
            font=("Arial", 22, "bold"),
            bg="#f4f6f8",
            fg="#1f2937"
        )
        title.pack(pady=10)

        subtitle = tk.Label(
            root,
            text="Carrier Sense Multiple Access with Collision Detection",
            font=("Arial", 12),
            bg="#f4f6f8",
            fg="#555555"
        )
        subtitle.pack()

        # -----------------------------
        # Main Frame
        # -----------------------------
        main_frame = tk.Frame(root, bg="#f4f6f8")
        main_frame.pack(fill="both", expand=True, padx=15, pady=10)

        # -----------------------------
        # Canvas for Topology
        # -----------------------------
        self.canvas = tk.Canvas(
            main_frame,
            width=760,
            height=560,
            bg="white",
            highlightthickness=1,
            highlightbackground="#cccccc"
        )
        self.canvas.pack(side="left", padx=10)

        # -----------------------------
        # Right Control Panel
        # -----------------------------
        control_frame = tk.Frame(
            main_frame,
            width=360,
            bg="white",
            relief="solid",
            bd=1
        )
        control_frame.pack(
            side="right",
            fill="both",
            expand=True,
            padx=10
        )

        tk.Label(
            control_frame,
            text="Simulation Control",
            font=("Arial", 16, "bold"),
            bg="white"
        ).pack(pady=10)

        # Frame input
        tk.Label(
            control_frame,
            text="Number of Frames:",
            font=("Arial", 11),
            bg="white"
        ).pack()

        self.frame_entry = tk.Entry(
            control_frame,
            font=("Arial", 11),
            justify="center"
        )
        self.frame_entry.insert(0, "10")
        self.frame_entry.pack(pady=5)

        # Start button
        self.start_button = tk.Button(
            control_frame,
            text="START SIMULATION",
            font=("Arial", 11, "bold"),
            bg="#2563eb",
            fg="white",
            padx=10,
            pady=8,
            command=self.start_simulation
        )
        self.start_button.pack(pady=10)

        # Reset button
        self.reset_button = tk.Button(
            control_frame,
            text="RESET",
            font=("Arial", 11, "bold"),
            padx=20,
            pady=6,
            command=self.reset_simulation
        )
        self.reset_button.pack(pady=5)

        # -----------------------------
        # Statistics
        # -----------------------------
        tk.Label(
            control_frame,
            text="Simulation Statistics",
            font=("Arial", 15, "bold"),
            bg="white"
        ).pack(pady=(20, 5))

        self.attempt_label = tk.Label(
            control_frame,
            text="Transmission Attempts: 0",
            font=("Arial", 11),
            bg="white"
        )
        self.attempt_label.pack(anchor="w", padx=20, pady=3)

        self.collision_label = tk.Label(
            control_frame,
            text="Collisions: 0",
            font=("Arial", 11),
            bg="white"
        )
        self.collision_label.pack(anchor="w", padx=20, pady=3)

        self.success_label = tk.Label(
            control_frame,
            text="Successful Transmissions: 0",
            font=("Arial", 11),
            bg="white"
        )
        self.success_label.pack(anchor="w", padx=20, pady=3)

        self.failed_label = tk.Label(
            control_frame,
            text="Failed Transmissions: 0",
            font=("Arial", 11),
            bg="white"
        )
        self.failed_label.pack(anchor="w", padx=20, pady=3)

        # -----------------------------
        # Current Status
        # -----------------------------
        tk.Label(
            control_frame,
            text="Current Status",
            font=("Arial", 15, "bold"),
            bg="white"
        ).pack(pady=(20, 5))

        self.status_label = tk.Label(
            control_frame,
            text="Ready",
            font=("Arial", 11, "bold"),
            bg="white",
            fg="#2563eb",
            wraplength=300
        )
        self.status_label.pack(pady=5)

        # -----------------------------
        # Event Log
        # -----------------------------
        tk.Label(
            control_frame,
            text="Event Log",
            font=("Arial", 15, "bold"),
            bg="white"
        ).pack(pady=(15, 5))

        self.log_text = tk.Text(
            control_frame,
            height=15,
            width=42,
            font=("Consolas", 9)
        )
        self.log_text.pack(
            padx=10,
            pady=5,
            fill="both",
            expand=True
        )

        # -----------------------------
        # Draw Initial Topology
        # -----------------------------
        self.draw_topology()

        # Create fresh log file
        with open(self.log_file, "w") as file:
            file.write("CSMA/CD SIMULATION LOG\n")
            file.write("=" * 60 + "\n")

    # ========================================================
    # DRAW TOPOLOGY
    # ========================================================

    def draw_topology(self):

        self.canvas.delete("all")

        # Canvas center
        switch_x = 380
        switch_y = 280

        # Host positions
        positions = {
            "Host 1": (150, 100),
            "Host 2": (610, 100),
            "Host 3": (150, 460),
            "Host 4": (610, 460)
        }

        # Draw connections
        self.lines = {}

        for host, (x, y) in positions.items():

            line = self.canvas.create_line(
                x,
                y,
                switch_x,
                switch_y,
                width=3,
                fill="#555555"
            )

            self.lines[host] = line

        # Draw switch
        self.canvas.create_rectangle(
            switch_x - 75,
            switch_y - 45,
            switch_x + 75,
            switch_y + 45,
            fill="#1e3a8a",
            outline="#172554",
            width=3
        )

        self.canvas.create_text(
            switch_x,
            switch_y - 10,
            text="CENTRAL\nSWITCH",
            fill="white",
            font=("Arial", 15, "bold")
        )

        self.canvas.create_text(
            switch_x,
            switch_y + 30,
            text="Ethernet Switch",
            fill="white",
            font=("Arial", 9)
        )

        # Draw hosts
        for host, (x, y) in positions.items():

            self.canvas.create_rectangle(
                x - 55,
                y - 35,
                x + 55,
                y + 35,
                fill=self.host_colors[host],
                outline="#222222",
                width=2
            )

            self.canvas.create_text(
                x,
                y,
                text=host,
                fill="white",
                font=("Arial", 13, "bold")
            )

        # Title
        self.canvas.create_text(
            380,
            30,
            text="Four Hosts Connected to a Central Switch",
            font=("Arial", 15, "bold"),
            fill="#1f2937"
        )

    # ========================================================
    # LOGGING
    # ========================================================

    def write_log(self, message):

        timestamp = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        final_message = f"{timestamp} | {message}"

        with open(self.log_file, "a") as file:
            file.write(final_message + "\n")

        self.log_text.insert(
            tk.END,
            final_message + "\n"
        )

        self.log_text.see(tk.END)

    # ========================================================
    # UPDATE STATISTICS
    # ========================================================

    def update_statistics(self):

        self.attempt_label.config(
            text=f"Transmission Attempts: {self.transmission_attempts}"
        )

        self.collision_label.config(
            text=f"Collisions: {self.collisions}"
        )

        self.success_label.config(
            text=f"Successful Transmissions: {self.successful_transmissions}"
        )

        self.failed_label.config(
            text=f"Failed Transmissions: {self.failed_transmissions}"
        )

    # ========================================================
    # ANIMATE TRANSMISSION
    # ========================================================

    def animate_host(self, host, color):

        self.canvas.itemconfig(
            self.lines[host],
            fill=color,
            width=5
        )

        self.root.update()

        time.sleep(0.2)

        self.canvas.itemconfig(
            self.lines[host],
            fill="#555555",
            width=3
        )

    # ========================================================
    # SEND FRAME
    # ========================================================

    def send_frame(self, host, frame_number):

        max_retries = 5
        retry = 0

        while retry < max_retries:

            retry += 1

            self.transmission_attempts += 1
            self.update_statistics()

            self.status_label.config(
                text=f"{host} transmitting Frame {frame_number}",
                fg="#2563eb"
            )

            self.write_log(
                f"{host} | Frame {frame_number} | "
                f"Transmission Attempt {retry}"
            )

            self.animate_host(
                host,
                self.host_colors[host]
            )

            # Collision probability
            collision = random.random() < 0.30

            if collision:

                self.collisions += 1
                self.update_statistics()

                self.status_label.config(
                    text=f"COLLISION! {host} Frame {frame_number}",
                    fg="#dc2626"
                )

                self.write_log(
                    f"{host} | Frame {frame_number} | "
                    f"COLLISION DETECTED"
                )

                # Binary exponential backoff
                max_slot = (2 ** retry) - 1

                backoff = random.randint(
                    0,
                    max_slot
                )

                self.write_log(
                    f"{host} | Frame {frame_number} | "
                    f"Back-off = {backoff} slot(s)"
                )

                self.status_label.config(
                    text=f"{host} waiting {backoff} slot(s)",
                    fg="#d97706"
                )

                self.root.update()

                time.sleep(
                    min(backoff * 0.3, 2)
                )

            else:

                self.successful_transmissions += 1
                self.update_statistics()

                self.status_label.config(
                    text=f"{host} Frame {frame_number} SUCCESS",
                    fg="#16a34a"
                )

                self.write_log(
                    f"{host} | Frame {frame_number} | "
                    f"Transmission SUCCESSFUL"
                )

                return

        # Maximum retries reached
        self.failed_transmissions += 1
        self.update_statistics()

        self.status_label.config(
            text=f"{host} Frame {frame_number} FAILED",
            fg="#dc2626"
        )

        self.write_log(
            f"{host} | Frame {frame_number} | "
            f"Transmission FAILED after {max_retries} retries"
        )

    # ========================================================
    # START SIMULATION
    # ========================================================

    def start_simulation(self):

        if self.running:
            return

        self.running = True
        self.start_button.config(state="disabled")

        try:
            total_frames = int(
                self.frame_entry.get()
            )

            if total_frames <= 0:
                raise ValueError

        except ValueError:

            self.status_label.config(
                text="Enter a valid positive number of frames.",
                fg="#dc2626"
            )

            self.running = False
            self.start_button.config(
                state="normal"
            )

            return

        for frame in range(1, total_frames + 1):

            host = random.choice(self.hosts)

            self.send_frame(
                host,
                frame
            )

            self.root.update()

            time.sleep(0.3)

        self.status_label.config(
            text="Simulation Completed",
            fg="#16a34a"
        )

        self.write_log(
            "========== SIMULATION COMPLETED =========="
        )

        self.running = False

        self.start_button.config(
            state="normal"
        )

    # ========================================================
    # RESET
    # ========================================================

    def reset_simulation(self):

        self.transmission_attempts = 0
        self.collisions = 0
        self.successful_transmissions = 0
        self.failed_transmissions = 0

        self.running = False

        self.update_statistics()

        self.log_text.delete(
            "1.0",
            tk.END
        )

        self.status_label.config(
            text="Ready",
            fg="#2563eb"
        )

        self.draw_topology()

        with open(self.log_file, "w") as file:
            file.write("CSMA/CD SIMULATION LOG\n")
            file.write("=" * 60 + "\n")


# ============================================================
# MAIN PROGRAM
# ============================================================

if __name__ == "__main__":

    root = tk.Tk()

    app = CSMACDSimulation(root)

    root.mainloop()
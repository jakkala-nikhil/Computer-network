import tkinter as tk
from tkinter import ttk, messagebox
import socket
import threading
from datetime import datetime


# ============================================================
# CONFIGURATION
# ============================================================

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 5000


# ============================================================
# ETHERNET SWITCH MODEL
# ============================================================

class EthernetSwitch:

    def __init__(self, gui):
        self.gui = gui

        # Simulated MAC address table
        # MAC Address -> Switch Port
        self.mac_table = {}

        # Switch ports
        self.ports = {
            "Port 1": "Client 1",
            "Port 2": "Client 2",
            "Port 3": "Client 3"
        }

    # --------------------------------------------------------
    # MAC LEARNING
    # --------------------------------------------------------

    def learn_mac(self, mac_address, port):

        old_port = self.mac_table.get(mac_address)

        self.mac_table[mac_address] = port

        if old_port != port:
            self.gui.add_log(
                f"MAC LEARNING: {mac_address} -> {port}"
            )

        self.gui.update_mac_table(self.mac_table)

    # --------------------------------------------------------
    # FRAME PROCESSING
    # --------------------------------------------------------

    def process_frame(
        self,
        source_mac,
        destination_mac,
        data,
        source_port
    ):

        # Learn source MAC address
        self.learn_mac(
            source_mac,
            source_port
        )

        self.gui.add_log(
            "----------------------------------------"
        )

        self.gui.add_log(
            f"FRAME RECEIVED ON {source_port}"
        )

        self.gui.add_log(
            f"Source MAC      : {source_mac}"
        )

        self.gui.add_log(
            f"Destination MAC : {destination_mac}"
        )

        self.gui.add_log(
            f"Data            : {data}"
        )

        # ----------------------------------------------------
        # Check destination MAC
        # ----------------------------------------------------

        if destination_mac in self.mac_table:

            destination_port = self.mac_table[
                destination_mac
            ]

            # Destination is on the same port
            if destination_port == source_port:

                self.gui.add_log(
                    "Destination is on the same source port."
                )

                self.gui.add_log(
                    "Frame is not forwarded."
                )

                return

            # Known destination
            self.gui.add_log(
                f"KNOWN DESTINATION"
            )

            self.gui.add_log(
                f"FORWARDING: {source_port} -> "
                f"{destination_port}"
            )

            self.gui.animate_forwarding(
                source_port,
                destination_port
            )

        else:

            # Unknown destination
            self.gui.add_log(
                "UNKNOWN DESTINATION"
            )

            self.gui.add_log(
                "BROADCASTING FRAME TO OTHER PORTS"
            )

            for port in self.ports:

                if port != source_port:

                    self.gui.add_log(
                        f"Broadcast -> {port}"
                    )

                    self.gui.animate_broadcast(
                        source_port,
                        port
                    )


# ============================================================
# GRAPHICAL APPLICATION
# ============================================================

class EthernetSwitchGUI:

    def __init__(self, root):

        self.root = root

        self.root.title(
            "Ethernet Switch - MAC Learning Simulation"
        )

        self.root.geometry(
            "1250x800"
        )

        self.root.minsize(
            1100,
            700
        )

        self.root.configure(
            bg="#f3f4f6"
        )

        # Server variables
        self.server_running = False
        self.server_socket = None

        # ----------------------------------------------------
        # TITLE
        # ----------------------------------------------------

        title = tk.Label(
            root,
            text="Ethernet Switch Simulation",
            font=("Arial", 24, "bold"),
            bg="#f3f4f6",
            fg="#111827"
        )

        title.pack(
            pady=(10, 2)
        )

        subtitle = tk.Label(
            root,
            text="Client-Server Communication and MAC Address Learning",
            font=("Arial", 12),
            bg="#f3f4f6",
            fg="#4b5563"
        )

        subtitle.pack(
            pady=(0, 8)
        )

        # ----------------------------------------------------
        # MAIN FRAME
        # ----------------------------------------------------

        main_frame = tk.Frame(
            root,
            bg="#f3f4f6"
        )

        main_frame.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )

        # ====================================================
        # LEFT: GRAPHICAL TOPOLOGY
        # ====================================================

        topology_frame = tk.Frame(
            main_frame,
            bg="white",
            bd=1,
            relief="solid"
        )

        topology_frame.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(0, 8)
        )

        self.canvas = tk.Canvas(
            topology_frame,
            width=730,
            height=600,
            bg="white",
            highlightthickness=0
        )

        self.canvas.pack(
            fill="both",
            expand=True,
            padx=5,
            pady=5
        )

        self.draw_topology()

        # ====================================================
        # RIGHT PANEL
        # ====================================================

        right_frame = tk.Frame(
            main_frame,
            bg="white",
            bd=1,
            relief="solid",
            width=430
        )

        right_frame.pack(
            side="right",
            fill="both",
            padx=(8, 0)
        )

        right_frame.pack_propagate(False)

        # ====================================================
        # SERVER SECTION
        # ====================================================

        tk.Label(
            right_frame,
            text="Server Control",
            font=("Arial", 15, "bold"),
            bg="white"
        ).pack(
            pady=(10, 4)
        )

        self.server_status = tk.Label(
            right_frame,
            text="SERVER: STOPPED",
            font=("Arial", 10, "bold"),
            fg="#dc2626",
            bg="white"
        )

        self.server_status.pack()

        self.start_server_button = tk.Button(
            right_frame,
            text="START SERVER",
            command=self.start_server,
            font=("Arial", 10, "bold"),
            bg="#16a34a",
            fg="white",
            padx=15,
            pady=5
        )

        self.start_server_button.pack(
            pady=7
        )

        # ====================================================
        # FRAME TRANSMISSION
        # ====================================================

        tk.Label(
            right_frame,
            text="Frame Transmission",
            font=("Arial", 15, "bold"),
            bg="white"
        ).pack(
            pady=(10, 5)
        )

        # Source MAC
        tk.Label(
            right_frame,
            text="Source MAC Address",
            bg="white"
        ).pack()

        self.source_entry = tk.Entry(
            right_frame,
            width=38
        )

        self.source_entry.insert(
            0,
            "AA:AA:AA:AA:AA:01"
        )

        self.source_entry.pack(
            pady=2
        )

        # Destination MAC
        tk.Label(
            right_frame,
            text="Destination MAC Address",
            bg="white"
        ).pack()

        self.destination_entry = tk.Entry(
            right_frame,
            width=38
        )

        self.destination_entry.insert(
            0,
            "BB:BB:BB:BB:BB:02"
        )

        self.destination_entry.pack(
            pady=2
        )

        # Data
        tk.Label(
            right_frame,
            text="Frame Data",
            bg="white"
        ).pack()

        self.data_entry = tk.Entry(
            right_frame,
            width=38
        )

        self.data_entry.insert(
            0,
            "Hello Ethernet"
        )

        self.data_entry.pack(
            pady=2
        )

        # Source Port
        tk.Label(
            right_frame,
            text="Source Port",
            bg="white"
        ).pack()

        self.port_combo = ttk.Combobox(
            right_frame,
            values=[
                "Port 1",
                "Port 2",
                "Port 3"
            ],
            state="readonly",
            width=35
        )

        self.port_combo.current(0)

        self.port_combo.pack(
            pady=2
        )

        # Send button
        self.send_button = tk.Button(
            right_frame,
            text="SEND FRAME",
            command=self.send_frame,
            font=("Arial", 11, "bold"),
            bg="#2563eb",
            fg="white",
            padx=20,
            pady=6
        )

        self.send_button.pack(
            pady=8
        )

        # ====================================================
        # MAC ADDRESS TABLE
        # ====================================================

        tk.Label(
            right_frame,
            text="MAC Address Table",
            font=("Arial", 14, "bold"),
            bg="white"
        ).pack(
            pady=(5, 4)
        )

        table_frame = tk.Frame(
            right_frame,
            bg="white"
        )

        table_frame.pack(
            fill="x",
            padx=10
        )

        self.mac_tree = ttk.Treeview(
            table_frame,
            columns=("MAC", "PORT"),
            show="headings",
            height=5
        )

        self.mac_tree.heading(
            "MAC",
            text="MAC Address"
        )

        self.mac_tree.heading(
            "PORT",
            text="Port"
        )

        self.mac_tree.column(
            "MAC",
            width=230,
            anchor="center"
        )

        self.mac_tree.column(
            "PORT",
            width=100,
            anchor="center"
        )

        self.mac_tree.pack(
            fill="x"
        )

        # ====================================================
        # EVENT LOG
        # ====================================================

        tk.Label(
            right_frame,
            text="Event Log",
            font=("Arial", 14, "bold"),
            bg="white"
        ).pack(
            pady=(8, 3)
        )

        log_frame = tk.Frame(
            right_frame,
            bg="white"
        )

        log_frame.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=(0, 8)
        )

        self.log_text = tk.Text(
            log_frame,
            height=12,
            font=("Consolas", 8),
            wrap="word"
        )

        self.log_text.pack(
            side="left",
            fill="both",
            expand=True
        )

        scrollbar = ttk.Scrollbar(
            log_frame,
            orient="vertical",
            command=self.log_text.yview
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )

        self.log_text.configure(
            yscrollcommand=scrollbar.set
        )

        # ----------------------------------------------------
        # Create switch after GUI is ready
        # ----------------------------------------------------

        self.switch = EthernetSwitch(
            self
        )

        self.add_log(
            "Application started."
        )

        self.add_log(
            "Configure a frame and click SEND FRAME."
        )

    # ========================================================
    # DRAW NETWORK TOPOLOGY
    # ========================================================

    def draw_topology(self):

        self.canvas.delete(
            "all"
        )

        # Switch position
        switch_x = 365
        switch_y = 285

        # Client positions
        clients = {
            "Client 1": (120, 120),
            "Client 2": (610, 120),
            "Client 3": (120, 470)
        }

        # ----------------------------------------------------
        # Connection Lines
        # ----------------------------------------------------

        for client, (x, y) in clients.items():

            self.canvas.create_line(
                x,
                y,
                switch_x,
                switch_y,
                fill="#6b7280",
                width=4
            )

        # Server connection
        self.canvas.create_line(
            switch_x,
            switch_y + 45,
            switch_x,
            525,
            fill="#6b7280",
            width=4
        )

        # ----------------------------------------------------
        # Port Labels
        # ----------------------------------------------------

        self.canvas.create_text(
            235,
            190,
            text="Port 1",
            font=("Arial", 10, "bold"),
            fill="#374151"
        )

        self.canvas.create_text(
            505,
            190,
            text="Port 2",
            font=("Arial", 10, "bold"),
            fill="#374151"
        )

        self.canvas.create_text(
            235,
            385,
            text="Port 3",
            font=("Arial", 10, "bold"),
            fill="#374151"
        )

        # ----------------------------------------------------
        # Central Switch
        # ----------------------------------------------------

        self.canvas.create_rectangle(
            switch_x - 80,
            switch_y - 45,
            switch_x + 80,
            switch_y + 45,
            fill="#1e40af",
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
            switch_y + 28,
            text="Ethernet Switch",
            fill="white",
            font=("Arial", 9)
        )

        # ----------------------------------------------------
        # Client Colors
        # ----------------------------------------------------

        colors = {
            "Client 1": "#2563eb",
            "Client 2": "#16a34a",
            "Client 3": "#ea580c"
        }

        # ----------------------------------------------------
        # Draw Clients
        # ----------------------------------------------------

        for client, (x, y) in clients.items():

            self.canvas.create_rectangle(
                x - 65,
                y - 35,
                x + 65,
                y + 35,
                fill=colors[client],
                outline="#111827",
                width=2
            )

            self.canvas.create_text(
                x,
                y,
                text=client,
                fill="white",
                font=("Arial", 12, "bold")
            )

        # ----------------------------------------------------
        # Server
        # ----------------------------------------------------

        self.canvas.create_rectangle(
            switch_x - 70,
            525,
            switch_x + 70,
            575,
            fill="#7c3aed",
            outline="#4c1d95",
            width=2
        )

        self.canvas.create_text(
            switch_x,
            550,
            text="SERVER",
            fill="white",
            font=("Arial", 13, "bold")
        )

        # ----------------------------------------------------
        # Title
        # ----------------------------------------------------

        self.canvas.create_text(
            365,
            35,
            text="Client-Server Ethernet Star Topology",
            font=("Arial", 17, "bold"),
            fill="#111827"
        )

        # ----------------------------------------------------
        # MAC Learning Explanation
        # ----------------------------------------------------

        self.canvas.create_text(
            365,
            650,
            text="Frame → Learn Source MAC → Check Destination MAC → Forward / Broadcast",
            font=("Arial", 10, "bold"),
            fill="#374151"
        )

    # ========================================================
    # START SERVER
    # ========================================================

    def start_server(self):

        if self.server_running:

            messagebox.showinfo(
                "Server",
                "Server is already running."
            )

            return

        try:

            self.server_socket = socket.socket(
                socket.AF_INET,
                socket.SOCK_STREAM
            )

            self.server_socket.setsockopt(
                socket.SOL_SOCKET,
                socket.SO_REUSEADDR,
                1
            )

            self.server_socket.bind(
                (
                    SERVER_HOST,
                    SERVER_PORT
                )
            )

            self.server_socket.listen(5)

            self.server_running = True

            self.server_status.config(
                text=f"SERVER: RUNNING ({SERVER_PORT})",
                fg="#16a34a"
            )

            self.start_server_button.config(
                state="disabled"
            )

            self.add_log(
                f"Server started on "
                f"{SERVER_HOST}:{SERVER_PORT}"
            )

            server_thread = threading.Thread(
                target=self.server_loop,
                daemon=True
            )

            server_thread.start()

        except OSError as error:

            messagebox.showerror(
                "Server Error",
                f"Could not start server:\n{error}"
            )

            self.server_running = False

    # ========================================================
    # SERVER LOOP
    # ========================================================

    def server_loop(self):

        while self.server_running:

            try:

                client_socket, address = (
                    self.server_socket.accept()
                )

                self.add_log(
                    f"Client connection: {address}"
                )

                client_thread = threading.Thread(
                    target=self.handle_client,
                    args=(client_socket,),
                    daemon=True
                )

                client_thread.start()

            except OSError:

                break

            except Exception as error:

                self.add_log(
                    f"Server error: {error}"
                )

                break

    # ========================================================
    # HANDLE CLIENT
    # ========================================================

    def handle_client(
        self,
        client_socket
    ):

        try:

            data = client_socket.recv(
                4096
            )

            if data:

                frame = data.decode(
                    "utf-8"
                )

                self.process_received_frame(
                    frame
                )

                client_socket.send(
                    b"Frame received successfully."
                )

        except Exception as error:

            self.add_log(
                f"Client handling error: {error}"
            )

        finally:

            client_socket.close()

    # ========================================================
    # PROCESS SOCKET FRAME
    # ========================================================

    def process_received_frame(
        self,
        frame
    ):

        parts = frame.split(
            "|",
            3
        )

        if len(parts) != 4:

            self.add_log(
                "Invalid frame received."
            )

            return

        source_mac = parts[0]
        destination_mac = parts[1]
        source_port = parts[2]
        data = parts[3]

        self.switch.process_frame(
            source_mac,
            destination_mac,
            data,
            source_port
        )

    # ========================================================
    # SEND FRAME
    # ========================================================

    def send_frame(self):

        source_mac = (
            self.source_entry.get().strip()
        )

        destination_mac = (
            self.destination_entry.get().strip()
        )

        data = (
            self.data_entry.get().strip()
        )

        source_port = (
            self.port_combo.get().strip()
        )

        # ----------------------------------------------------
        # Validation
        # ----------------------------------------------------

        if not source_mac:

            messagebox.showerror(
                "Input Error",
                "Enter a source MAC address."
            )

            return

        if not destination_mac:

            messagebox.showerror(
                "Input Error",
                "Enter a destination MAC address."
            )

            return

        if not data:

            messagebox.showerror(
                "Input Error",
                "Enter frame data."
            )

            return

        if source_port not in [
            "Port 1",
            "Port 2",
            "Port 3"
        ]:

            messagebox.showerror(
                "Input Error",
                "Select a valid source port."
            )

            return

        # ----------------------------------------------------
        # Validate MAC Format
        # ----------------------------------------------------

        if not self.valid_mac(source_mac):

            messagebox.showerror(
                "Input Error",
                "Invalid source MAC format.\n"
                "Example: AA:AA:AA:AA:AA:01"
            )

            return

        if not self.valid_mac(destination_mac):

            messagebox.showerror(
                "Input Error",
                "Invalid destination MAC format.\n"
                "Example: BB:BB:BB:BB:BB:02"
            )

            return

        # ----------------------------------------------------
        # Process locally through switch
        # ----------------------------------------------------

        self.switch.process_frame(
            source_mac,
            destination_mac,
            data,
            source_port
        )

        # ----------------------------------------------------
        # Send through Python Socket
        # ----------------------------------------------------

        if self.server_running:

            try:

                client_socket = socket.socket(
                    socket.AF_INET,
                    socket.SOCK_STREAM
                )

                client_socket.settimeout(
                    3
                )

                client_socket.connect(
                    (
                        SERVER_HOST,
                        SERVER_PORT
                    )
                )

                frame = (
                    f"{source_mac}|"
                    f"{destination_mac}|"
                    f"{source_port}|"
                    f"{data}"
                )

                client_socket.send(
                    frame.encode(
                        "utf-8"
                    )
                )

                response = client_socket.recv(
                    1024
                ).decode(
                    "utf-8"
                )

                self.add_log(
                    f"SOCKET: {response}"
                )

                client_socket.close()

            except Exception as error:

                self.add_log(
                    f"Socket communication error: {error}"
                )

        else:

            self.add_log(
                "Server is not running. "
                "Frame simulated locally."
            )

    # ========================================================
    # MAC FORMAT VALIDATION
    # ========================================================

    @staticmethod
    def valid_mac(mac):

        parts = mac.split(":")

        if len(parts) != 6:

            return False

        for part in parts:

            if len(part) != 2:

                return False

            try:

                int(
                    part,
                    16
                )

            except ValueError:

                return False

        return True

    # ========================================================
    # UPDATE MAC TABLE
    # ========================================================

    def update_mac_table(
        self,
        table
    ):

        # Remove old rows
        for item in self.mac_tree.get_children():

            self.mac_tree.delete(
                item
            )

        # Add current MAC entries
        for mac, port in table.items():

            self.mac_tree.insert(
                "",
                "end",
                values=(
                    mac,
                    port
                )
            )

    # ========================================================
    # ADD EVENT LOG
    # ========================================================

    def add_log(
        self,
        message
    ):

        timestamp = datetime.now().strftime(
            "%H:%M:%S"
        )

        final_message = (
            f"[{timestamp}] {message}"
        )

        self.log_text.insert(
            tk.END,
            final_message + "\n"
        )

        self.log_text.see(
            tk.END
        )

    # ========================================================
    # FORWARDING ANIMATION
    # ========================================================

    def animate_forwarding(
        self,
        source_port,
        destination_port
    ):

        port_client = {
            "Port 1": "Client 1",
            "Port 2": "Client 2",
            "Port 3": "Client 3"
        }

        source_client = port_client.get(
            source_port
        )

        destination_client = port_client.get(
            destination_port
        )

        if source_client and destination_client:

            self.add_log(
                f"FORWARD: "
                f"{source_client} -> SWITCH -> "
                f"{destination_client}"
            )

    # ========================================================
    # BROADCAST
    # ========================================================

    def animate_broadcast(
        self,
        source_port,
        destination_port
    ):

        port_client = {
            "Port 1": "Client 1",
            "Port 2": "Client 2",
            "Port 3": "Client 3"
        }

        source_client = port_client.get(
            source_port
        )

        destination_client = port_client.get(
            destination_port
        )

        if source_client and destination_client:

            self.add_log(
                f"BROADCAST: "
                f"{source_client} -> SWITCH -> "
                f"{destination_client}"
            )

    # ========================================================
    # CLOSE APPLICATION
    # ========================================================

    def close_application(self):

        self.server_running = False

        if self.server_socket:

            try:

                self.server_socket.close()

            except Exception:

                pass

        self.root.destroy()


# ============================================================
# MAIN PROGRAM
# ============================================================

if __name__ == "__main__":

    root = tk.Tk()

    app = EthernetSwitchGUI(
        root
    )

    root.protocol(
        "WM_DELETE_WINDOW",
        app.close_application
    )

    root.mainloop()
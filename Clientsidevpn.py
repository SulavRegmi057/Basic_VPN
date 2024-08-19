import socket
import ssl
import tkinter as tk
from tkinter import scrolledtext
from tkinter import messagebox
from threading import Thread

class VPNClientGUI(tk.Tk):
    def __init__(self):
        super().__init__()

        # Window settings
        self.title("VPN Client")
        self.geometry("500x400")
        self.configure(bg="#f0f0f0")

        # Title Label
        self.title_label = tk.Label(self, text="VPN Client", font=("Helvetica", 16), bg="#f0f0f0", fg="#333333")
        self.title_label.pack(pady=10)

        # Message Display
        self.message_display = scrolledtext.ScrolledText(self, wrap=tk.WORD, height=15, font=("Helvetica", 12), bg="#ffffff", fg="#333333", state=tk.DISABLED)
        self.message_display.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        # Status Label
        self.status_label = tk.Label(self, text="Status: Disconnected", font=("Helvetica", 12), bg="#f0f0f0", fg="#ff6f61")
        self.status_label.pack(pady=5)

        # Connect and Disconnect buttons
        self.connect_button = tk.Button(self, text="Connect", command=self.connect_to_server, font=("Helvetica", 12), bg="#4caf50", fg="#ffffff", relief=tk.RAISED)
        self.connect_button.pack(side=tk.LEFT, padx=10, pady=10)
        self.disconnect_button = tk.Button(self, text="Disconnect", command=self.disconnect_from_server, font=("Helvetica", 12), bg="#f44336", fg="#ffffff", relief=tk.RAISED, state=tk.DISABLED)
        self.disconnect_button.pack(side=tk.LEFT, padx=10, pady=10)

        # Client socket
        self.client_socket = None
        self.thread = None

    def connect_to_server(self):
        if not self.client_socket:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
            context.load_verify_locations(cafile='server.crt')

            # Enable hostname verification
            context.check_hostname = True
            context.verify_mode = ssl.CERT_REQUIRED

            self.client_socket = context.wrap_socket(self.client_socket, server_hostname='10.0.2.15')
            try:
                self.client_socket.connect(('10.0.2.15', 8080))
                self.status_label.config(text="Status: Connected", fg="#4caf50")
                self.connect_button.config(state=tk.DISABLED)
                self.disconnect_button.config(state=tk.NORMAL)

                # Start listening for incoming messages
                self.thread = Thread(target=self.receive_messages)
                self.thread.start()
            except Exception as e:
                messagebox.showerror("Connection Error", str(e))
                self.client_socket = None

    def disconnect_from_server(self):
        if self.client_socket:
            self.client_socket.close()
            self.client_socket = None
            self.status_label.config(text="Status: Disconnected", fg="#ff6f61")
            self.connect_button.config(state=tk.NORMAL)
            self.disconnect_button.config(state=tk.DISABLED)
            self.message_display.config(state=tk.NORMAL)
            self.message_display.insert(tk.END, "Disconnected from server.\n")
            self.message_display.config(state=tk.DISABLED)

    def receive_messages(self):
        while self.client_socket:
            try:
                data = self.client_socket.recv(1024)
                if data:
                    message = data.decode('utf-8')
                    self.message_display.config(state=tk.NORMAL)
                    self.message_display.insert(tk.END, f"Received: {message}\n")
                    self.message_display.yview(tk.END)
                    self.message_display.config(state=tk.DISABLED)
            except Exception as e:
                self.message_display.config(state=tk.NORMAL)
                self.message_display.insert(tk.END, f"Error: {e}\n")
                self.message_display.config(state=tk.DISABLED)
                break

if __name__ == "__main__":
    app = VPNClientGUI()
    app.mainloop()

import socket
import ssl
import logging
import asyncio
import tkinter as tk
from tkinter import scrolledtext
from threading import Thread

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class VPNServerGUI(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("VPN Server")
        self.geometry("600x400")

        # Log display
        self.log_display = scrolledtext.ScrolledText(self, wrap=tk.WORD, state=tk.DISABLED)
        self.log_display.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        # Start and Stop buttons
        self.start_button = tk.Button(self, text="Start Server", command=self.start_server)
        self.start_button.pack(side=tk.LEFT, padx=10, pady=5)
        self.stop_button = tk.Button(self, text="Stop Server", command=self.stop_server, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=10, pady=5)

        self.server_task = None
        self.loop = asyncio.new_event_loop()

    def start_server(self):
        if not self.server_task:
            self.server_task = Thread(target=self.run_server)
            self.server_task.start()
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.log("Server started...")

    def stop_server(self):
        if self.server_task:
            self.loop.call_soon_threadsafe(self.loop.stop)
            self.server_task.join()
            self.server_task = None
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.log("Server stopped.")

    def log(self, message):
        self.log_display.config(state=tk.NORMAL)
        self.log_display.insert(tk.END, f"{message}\n")
        self.log_display.yview(tk.END)
        self.log_display.config(state=tk.DISABLED)

    def run_server(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(start_server(self))
        self.loop.run_forever()

async def handle_client(reader, writer, gui):
    """
    Handles communication with a connected client.
    Receives data from the client, processes it, and sends a response.
    """
    try:
        client_address = writer.get_extra_info('peername')
        gui.log(f"Connection established with {client_address}")

        data = await reader.read(1024)
        if not data:
            gui.log(f"Client {client_address} sent no data or disconnected")
            return

        message = data.decode('utf-8')
        gui.log(f"Received data from {client_address}: {message}")

        await asyncio.sleep(2)  # Delay to simulate processing

        response = "Hello from the server!"
        writer.write(response.encode('utf-8'))
        await writer.drain()

        gui.log(f"Sent response to {client_address}: {response}")

        await asyncio.sleep(2)  # Delay to simulate processing
    except Exception as e:
        gui.log(f"Error handling client {client_address}: {e}")
    finally:
        writer.close()
        await writer.wait_closed()
        gui.log(f"Connection with {client_address} closed")

async def start_server(gui):
    """
    Starts a TCP server that listens for incoming connections on port 8080.
    Utilizes SSL/TLS for secure communication.
    """
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain(certfile='/home/kali/VPN/server.crt', keyfile='/home/kali/VPN/server.key')

    server = await asyncio.start_server(
        lambda r, w: handle_client(r, w, gui), '0.0.0.0', 8080, ssl=context
    )

    addr = server.sockets[0].getsockname()
    gui.log(f"Server is listening on {addr}")

    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    app = VPNServerGUI()
    app.mainloop()


import socket
import threading
import tkinter as tk
from tkinter import messagebox

HOST = "localhost"
PORT = 5002

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

buffer = ""
while True:
    data = client.recv(1024).decode()
    if not data:
        raise ConnectionError("Failed to receive symbol from server")
    buffer += data
    if "\n" in buffer:
        line, buffer = buffer.split("\n", 1)
        if line.startswith("SYMBOL:"):
            symbol = line.split(":", 1)[1]
            break

root = tk.Tk()
root.title("Tic Tac Toe - " + symbol)

status_label = tk.Label(root, text=f"You are {symbol}. Waiting for updates...", font=("Arial", 12))
status_label.pack(pady=8)

buttons = []
receive_buffer = buffer

def update_board(state):
    for i in range(9):
        buttons[i]["text"] = state[i]

def receive():
    global receive_buffer
    while True:
        try:
            data = client.recv(1024).decode()
            if not data:
                break
            receive_buffer += data
            while "\n" in receive_buffer:
                line, receive_buffer = receive_buffer.split("\n", 1)
                if not line:
                    continue
                if line.startswith("WIN:"):
                    winner = line.split(":", 1)[1]
                    messagebox.showinfo("Game Over", "Winner: " + winner)
                    return
                if line.startswith("SYMBOL:"):
                    continue
                if len(line) == 9:
                    update_board(line)
                    status_label.config(text=f"You are {symbol}. Waiting for opponent...")
        except Exception as e:
            print("Receive error:", e)
            break

def send_move(i):
    try:
        client.sendall((str(i) + "\n").encode())
    except Exception as e:
        print("Send error:", e)

frame = tk.Frame(root)
frame.pack()

for i in range(9):
    btn = tk.Button(frame, text=" ", font=("Arial", 20), width=5, height=2,
                    command=lambda i=i: send_move(i))
    btn.grid(row=i//3, column=i%3)
    buttons.append(btn)

threading.Thread(target=receive, daemon=True).start()

root.mainloop()
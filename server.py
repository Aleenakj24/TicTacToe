
import socket
import threading

HOST = "localhost"
PORT = 5002

board = [" "] * 9
current_player = "X"
clients = []

def check_winner():
    wins = [(0,1,2),(3,4,5),(6,7,8),(0,3,6),(1,4,7),(2,5,8),(0,4,8),(2,4,6)]
    for a,b,c in wins:
        if board[a] == board[b] == board[c] and board[a] != " ":
            return board[a]
    if " " not in board:
        return "Draw"
    return None


def send_message(conn, message):
    conn.sendall((message + "\n").encode())


def handle_client(conn, symbol):
    global current_player
    send_message(conn, "SYMBOL:" + symbol)
    recv_buffer = ""

    while True:
        try:
            data = conn.recv(1024).decode()
            if not data:
                break
            recv_buffer += data
            while "\n" in recv_buffer:
                line, recv_buffer = recv_buffer.split("\n", 1)
                move = line.strip()
                if not move:
                    continue

                if symbol == current_player and move.isdigit() and 0 <= int(move) < 9 and board[int(move)] == " ":
                    board[int(move)] = symbol
                    winner = check_winner()

                    state = "".join(board)
                    for c in clients:
                        send_message(c, state)

                    if winner:
                        for c in clients:
                            send_message(c, "WIN:" + winner)
                        break

                    current_player = "O" if current_player == "X" else "X"
                else:
                    print(f"Invalid move {move} by {symbol}; current player is {current_player}")
        except Exception as e:
            print("Connection error:", e)
            break

    conn.close()

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(2)

    print("Server started... Waiting for players")

    while len(clients) < 2:
        conn, addr = server.accept()
        clients.append(conn)
        print("Player connected:", addr)

    initial_state = "".join(board)
    for c in clients:
        send_message(c, initial_state)

    threading.Thread(target=handle_client, args=(clients[0], "X")).start()
    threading.Thread(target=handle_client, args=(clients[1], "O")).start()

if __name__ == "__main__":
    main()

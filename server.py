import socket
import threading
from game import SeegaGame
import random

HOST = 'localhost'
PORT = 5555

clients = []
nicknames = []
game = SeegaGame()

def broadcast(msg):
    """
    Envia uma mensagem para todos os clientes conectados.

    Args:
        msg (str): A mensagem a ser enviada.
    """
    for client in clients:
        client.send(msg.encode())

def send_board():
    """
    Gera a representação textual do tabuleiro atual e envia para todos os jogadores.
    Também mostra de quem é a vez e quantas peças restam.
    """
    board_str = "\n  0 1 2 3 4\n"
    for i, row in enumerate(game.board):
        row_display = ' '.join(cell if cell != ' ' else '.' for cell in row)
        board_str += f"{i} {row_display}\n"
    board_str += f"\nÉ a vez de {game.turn} (Peças restantes: X={game.pieces['X']} O={game.pieces['O']})\n"
    broadcast(board_str)

def handle_client(conn, player_symbol):
    """
    Lida com a conexão de um cliente específico durante a partida.

    Args:
        conn (socket.socket): A conexão com o cliente.
        player_symbol (str): O símbolo do jogador ('X' ou 'O').
    """
    conn.send(f"Você é o jogador {player_symbol}\n".encode())
    send_board()
    while True:
        try:
            msg = conn.recv(1024).decode().strip()
            if not msg:
                break

            if msg.startswith("place"):
                if game.turn != player_symbol:
                    conn.send("Não é sua vez.\n".encode())
                    continue
                try:
                    _, x, y = msg.split()
                    x, y = int(x), int(y)
                    success, response = game.place_piece(x, y)
                    conn.send((response + '\n').encode())
                    send_board()
                except ValueError:
                    conn.send("Comando inválido. Use: place x y\n".encode())

            elif msg.startswith("move"):
                if game.turn != player_symbol:
                    conn.send("Não é sua vez.\n".encode())
                    continue
                try:
                    _, x1, y1, x2, y2 = msg.split()
                    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                    success, response = game.move_piece(x1, y1, x2, y2)
                    conn.send((response + '\n').encode())
                    send_board()

                    if "venceu" in response:
                        broadcast(f"[ENCERRAR_JOGO] {response}\n")
                        break
                except ValueError:
                    conn.send("Comando inválido. Use: move x1 y1 x2 y2\n".encode())

            else:
                if msg.lower() == "/desistir":
                    winner = 'O' if player_symbol == 'X' else 'X'
                    broadcast(f"[ENCERRAR_JOGO] Jogador {winner} venceu! {player_symbol} desistiu.\n")
                    break 
                else:
                    sender = f"Jogador {player_symbol}"
                    chat_msg = f"[{sender} diz]: {msg}\n"
                    for client in clients:
                        client.send(chat_msg.encode())

        except Exception as e:
            print(f"Erro com cliente {player_symbol}: {e}")
            break
        
def start_server():
    """
    Inicializa o servidor, escutando por até dois clientes e iniciando a partida
    assim que ambos estiverem conectados.
    """
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(2)
    print(f"[+] Servidor escutando em {HOST}:{PORT}")
    symbol_order = ['X', 'O']
    random.shuffle(symbol_order)
    while len(clients) < 2:
        conn, addr = server.accept()
        player_symbol = symbol_order[len(clients)]
        clients.append(conn)
        nicknames.append(player_symbol)

        thread = threading.Thread(target=handle_client, args=(conn, player_symbol))
        thread.start()

    print("[*] Dois jogadores conectados. Iniciando partida...")
    broadcast("[!] Dois jogadores conectados. Começando o jogo...\n")

if __name__ == "__main__":
    start_server()

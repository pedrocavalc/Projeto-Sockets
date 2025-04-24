import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, simpledialog
import re

HOST = 'localhost'
PORT = 5555

class SeegaClient:
    """
    Classe que representa o cliente gráfico do jogo Seega utilizando Tkinter.
    Responsável por renderizar o tabuleiro, comunicar com o servidor e exibir mensagens.
    """

    def __init__(self, master):
        """
        Inicializa a interface e conexão com o servidor.

        Args:
            master (tk.Tk): Janela principal do Tkinter.
        """
        self.master = master
        self.master.title("Seega - Cliente")
        self.master.configure(bg="#f0f0f0")

        self.selected = None
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((HOST, PORT))

        self.placing_phase = True
        self.my_symbol = None

        self.create_widgets()
        self.listen_thread = threading.Thread(target=self.receive_messages, daemon=True)
        self.listen_thread.start()

    def create_widgets(self):
        """
        Cria todos os componentes visuais da interface gráfica, incluindo tabuleiro, chat e botões.
        """
        # Label de status no topo
        self.status_label = tk.Label(self.master, text="Aguardando dados do servidor...", font=("Arial", 12, "bold"), bg="#f0f0f0", fg="#333")
        self.status_label.pack(pady=(10, 5))

        main_frame = tk.Frame(self.master, bg="#f0f0f0")
        main_frame.pack(padx=10, pady=5)

        # Tabuleiro
        self.board_frame = tk.Frame(main_frame, bg="#f0f0f0")
        self.board_frame.grid(row=0, column=0, padx=10)

        self.cells = [[None for _ in range(5)] for _ in range(5)]
        for i in range(5):
            for j in range(5):
                btn = tk.Button(self.board_frame, text=" ", width=4, height=2, font=("Arial", 12, "bold"),
                                bg="#ffffff", relief=tk.FLAT,
                                command=lambda x=i, y=j: self.cell_click(x, y))
                btn.grid(row=i, column=j, padx=2, pady=2)
                self.cells[i][j] = btn

        # Área de chat
        right_frame = tk.Frame(main_frame, bg="#f0f0f0")
        right_frame.grid(row=0, column=1, sticky="n")

        self.log = scrolledtext.ScrolledText(right_frame, width=40, height=20, font=("Courier", 10), bg="#fafafa", state='disabled')
        self.log.pack(pady=5)

        bottom_frame = tk.Frame(right_frame, bg="#f0f0f0")
        bottom_frame.pack(fill='x')

        self.entry = tk.Entry(bottom_frame, width=30, font=("Arial", 10))
        self.entry.pack(side='left', padx=(0, 5), pady=5)

        self.send_btn = tk.Button(bottom_frame, text="Enviar", command=self.send_message, bg="#4CAF50", fg="white", relief=tk.FLAT)
        self.send_btn.pack(side='right')

        self.quit_btn = tk.Button(right_frame, text="Desistir", command=self.send_resign, bg="#d32f2f", fg="white", relief=tk.FLAT)
        self.quit_btn.pack(pady=(10, 0), fill='x')

    def cell_click(self, x, y):
        """
        Lida com o clique em uma célula do tabuleiro.

        Args:
            x (int): Linha clicada.
            y (int): Coluna clicada.
        """
        current_piece = self.cells[x][y].cget("text")

        if self.placing_phase:
            command = f"place {x} {y}"
            self.sock.send(command.encode())
            return

        if self.selected is None:
            if current_piece == self.my_symbol:
                self.selected = (x, y)
                self.cells[x][y].config(bg="#add8e6")
                self.log_message(f"Selecionado: {x},{y}")
            else:
                self.log_message("Você só pode selecionar suas próprias peças.")
        else:
            x1, y1 = self.selected

            if (x, y) == (x1, y1):
                self.selected = None
                self.cells[x1][y1].config(bg="#ffffff")
                self.log_message("Seleção cancelada.")
            else:
                command = f"move {x1} {y1} {x} {y}"
                self.sock.send(command.encode())
                self.cells[x1][y1].config(bg="#ffffff")
                self.selected = None

    def send_message(self):
        """
        Envia a mensagem digitada no campo de entrada para o servidor.
        """
        msg = self.entry.get()
        if msg:
            self.sock.send(msg.encode())
            self.entry.delete(0, tk.END)

    def process_message(self, msg):
        """
        Processa as mensagens recebidas do servidor.

        Args:
            msg (str): Mensagem recebida.
        """
        if re.match(r"\[Jogador [XO] diz\]:", msg):
            self.log_message(msg)
        self.update_board_from_message(msg)

        if "Você é o jogador" in msg:
            self.my_symbol = msg.strip()[-1]
            self.status_label.config(text=f"Você é o jogador {self.my_symbol}")

        if "Peças restantes:" in msg and self.my_symbol:
            try:
                match = re.search(rf"{self.my_symbol}=(\d+)", msg)
                if match:
                    count = int(match.group(1))
                    self.placing_phase = count > 0
            except Exception as e:
                self.log_message(f"[Erro] ao interpretar peças restantes: {e}")

        if "É a vez de" in msg:
            self.status_label.config(text=msg.strip())

        if "[ENCERRAR_JOGO]" in msg:
            cleaned_msg = msg.replace("[ENCERRAR_JOGO]", "").strip()
            self.status_label.config(text="Jogo encerrado!")
            self.show_victory_popup(cleaned_msg)

    def show_victory_popup(self, message):
        """
        Exibe uma janela de popup informando o fim do jogo e quem venceu.

        Args:
            message (str): Mensagem de encerramento do jogo.
        """
        winner_match = re.search(r"Jogo encerrado! (\w) venceu!", message)
        if winner_match:
            winner = winner_match.group(1)
            if winner == self.my_symbol:
                msg = "Parabéns, você venceu!"
            else:
                msg = "Você perdeu. Mais sorte na próxima vez!"
            msg += f"\n\nDetalhes: {message}"
        else:
            msg = message

        self.master.after(0, lambda: tk.messagebox.showinfo("Fim de Jogo", msg))

    def receive_messages(self):
        """
        Loop de recebimento contínuo de mensagens do servidor via socket.
        Atualiza a interface conforme as mensagens chegam.
        """
        buffer = ""
        while True:
            try:
                data = self.sock.recv(1024).decode()
                if not data:
                    break

                buffer += data

                while '\n\n' in buffer:
                    msg, buffer = buffer.split('\n\n', 1)
                    self.process_message(msg)

                while '\n' in buffer and not buffer.startswith('  0'):
                    line, buffer = buffer.split('\n', 1)
                    if line.strip():
                        self.process_message(line.strip())
            except Exception as e:
                self.log_message(f"[Erro] Desconectado do servidor: {e}")
                break

    def log_message(self, msg):
        """
        Adiciona uma mensagem no log de chat da interface.

        Args:
            msg (str): Mensagem a ser exibida.
        """
        self.log.config(state='normal')
        self.log.insert(tk.END, msg + "\n")
        self.log.yview(tk.END)
        self.log.config(state='disabled')

    def update_board_from_message(self, msg):
        """
        Atualiza o tabuleiro com base em uma mensagem recebida do servidor.

        Args:
            msg (str): Mensagem contendo o estado do tabuleiro.
        """
        self.master.after(0, self._update_board_gui, msg)

    def _update_board_gui(self, msg):
        """
        Realiza a atualização visual do tabuleiro com base nas linhas formatadas do servidor.

        Args:
            msg (str): Mensagem com linhas representando o tabuleiro.
        """
        try:
            lines = msg.splitlines()
            board_lines = [line for line in lines if line.strip() and line.lstrip()[0] in "01234" and len(line.split()) == 6]
            if len(board_lines) != 5:
                return

            for i in range(5):
                row_data = board_lines[i].split()[1:]
                for j in range(5):
                    val = row_data[j]
                    text = val if val != '.' else ' '
                    bg = "#ffffff"
                    fg = "#000000"

                    if text == "X":
                        fg = "#d32f2f"
                    elif text == "O":
                        fg = "#1976d2"

                    self.cells[i][j].config(
                        text=text,
                        fg=fg,
                        bg=bg,
                        relief=tk.FLAT
                    )
        except Exception as e:
            self.log_message(f"[Erro] ao atualizar tabuleiro: {e}")

    def send_resign(self):
        """
        Envia um comando de desistência para o servidor após confirmação do usuário.
        """
        if tk.messagebox.askyesno("Confirmar Desistência", "Tem certeza que deseja desistir da partida?"):
            self.sock.send("/desistir".encode())

if __name__ == "__main__":
    root = tk.Tk()
    client = SeegaClient(root)
    root.mainloop()

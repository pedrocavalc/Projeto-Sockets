class SeegaGame:
    """
    Classe que representa a lógica do jogo Seega, com tabuleiro 5x5,
    duas fases (colocação e movimentação), e regras de captura e vitória.
    """

    def __init__(self):
        """
        Inicializa o estado do jogo, criando o tabuleiro, definindo o jogador inicial,
        quantidade de peças por jogador e iniciando a fase de colocação.
        """
        self.board = [[' ' for _ in range(5)] for _ in range(5)]
        self.turn = 'X'
        self.pieces = {'X': 12, 'O': 12}
        self.phase = 1
        self.placements_this_turn = 0

    def print_board(self):
        """
        Imprime o estado atual do tabuleiro no terminal.
        """
        print("\n  0 1 2 3 4")
        for i, row in enumerate(self.board):
            print(f"{i} " + ' '.join(row))
        print()

    def is_valid_position(self, x, y):
        """
        Verifica se a posição (x, y) está dentro dos limites do tabuleiro.

        Args:
            x (int): Linha
            y (int): Coluna

        Returns:
            bool: True se a posição for válida, False caso contrário.
        """
        return 0 <= x < 5 and 0 <= y < 5

    def place_piece(self, x, y):
        """
        Coloca uma peça no tabuleiro durante a fase 1 (colocação).

        Args:
            x (int): Linha onde a peça será colocada.
            y (int): Coluna onde a peça será colocada.

        Returns:
            tuple: (bool, str) indicando sucesso e uma mensagem explicativa.
        """
        if self.phase != 1:
            return False, "Fase 1 encerrada. Use 'move x1 y1 x2 y2'."
        if not self.is_valid_position(x, y) or self.board[x][y] != ' ' or (x == 2 and y == 2):
            return False, "Posição inválida."
        if self.pieces[self.turn] <= 0:
            return False, "Você já colocou todas as suas peças."

        self.board[x][y] = self.turn
        self.pieces[self.turn] -= 1
        self.placements_this_turn += 1

        if self.placements_this_turn == 2:
            self.turn = 'O' if self.turn == 'X' else 'X'
            self.placements_this_turn = 0

        if self.pieces['X'] == 0 and self.pieces['O'] == 0:
            self.phase = 2

        return True, "Peça colocada com sucesso."

    def move_piece(self, x1, y1, x2, y2):
        """
        Move uma peça do jogador durante a fase 2 (movimentação).

        Args:
            x1, y1 (int): Posição inicial.
            x2, y2 (int): Posição de destino.

        Returns:
            tuple: (bool, str) indicando sucesso e uma mensagem explicativa.
        """
        if self.phase != 2:
            return False, "Ainda estamos na fase de colocação."
        if not (self.is_valid_position(x1, y1) and self.is_valid_position(x2, y2)):
            return False, "Posição inválida."
        if self.board[x1][y1] != self.turn:
            return False, "Você só pode mover suas próprias peças."
        if self.board[x2][y2] != ' ':
            return False, "A posição de destino está ocupada."

        if abs(x1 - x2) + abs(y1 - y2) != 1:
            return False, "Movimento inválido. Só é permitido mover uma casa na horizontal ou vertical."

        self.board[x2][y2] = self.turn
        self.board[x1][y1] = ' '
        captured = self.check_capture(x2, y2)
        winner = self.check_win()
        if winner:
            return True, f"Jogo encerrado! {winner} venceu!"

        if not captured:
            self.turn = 'O' if self.turn == 'X' else 'X'
            return True, "Peça movida com sucesso."
        else:
            return True, "Captura realizada! Você pode jogar novamente."

    def check_capture(self, x, y):
        """
        Verifica se houve captura após uma movimentação.

        Args:
            x (int): Linha da nova posição da peça.
            y (int): Coluna da nova posição da peça.

        Returns:
            bool: True se uma ou mais peças inimigas foram capturadas.
        """
        enemy = 'O' if self.turn == 'X' else 'X'
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        captured = False

        for dx, dy in directions:
            adj_x, adj_y = x + dx, y + dy
            opp_x, opp_y = x + 2 * dx, y + 2 * dy

            if (self.is_valid_position(adj_x, adj_y) and
                self.board[adj_x][adj_y] == enemy):

                if (self.is_valid_position(opp_x, opp_y) and
                    self.board[opp_x][opp_y] == self.turn):
                    self.board[adj_x][adj_y] = ' '
                    self.pieces[enemy] -= 1
                    captured = True

        return captured

    def check_win(self):
        """
        Verifica se um dos jogadores venceu a partida.

        Returns:
            str or None: 'X' ou 'O' se houver um vencedor, None caso contrário.
        """
        count_x = sum(row.count('X') for row in self.board)
        count_o = sum(row.count('O') for row in self.board)

        if count_x == 0:
            return 'O'
        elif count_o == 0:
            return 'X'

        for row in self.board:
            if all(cell == 'X' for cell in row):
                return 'X'
            elif all(cell == 'O' for cell in row):
                return 'O'

        for col in range(5):
            col_cells = [self.board[row][col] for row in range(5)]
            if all(cell == 'X' for cell in col_cells):
                return 'X'
            elif all(cell == 'O' for cell in col_cells):
                return 'O'

        return None

    def get_game_state(self):
        """
        Retorna o estado atual do jogo em forma de dicionário.

        Returns:
            dict: Estado atual contendo o tabuleiro, jogador da vez, peças restantes e fase.
        """
        return {
            "board": self.board,
            "turn": self.turn,
            "pieces": self.pieces,
            "phase": self.phase
        }

class TicTacToe:
    def __init__(self, size=3):
        
        self.size = size
        self.board = [[' ' for _ in range(size)] for _ in range(size)]
        self.current_player = 'X' 
        self.game_over = False
        self.winner = None
    
    def is_valid_move(self, row, col):

        if self.game_over:
            return False
        
        if not (0 <= row < self.size and 0 <= col < self.size):
            return False
        
        return self.board[row][col] == ' '
    
    def __getitem__(self, index):

        if isinstance(index, tuple):
            row, col = index
            return self.board[row][col]
        else:
            return self.board[index]
    
    def __setitem__(self, index, value):

        if not isinstance(index, tuple) or len(index) != 2:
            raise ValueError("Index должен быть кортежем (row, col)")
        
        row, col = index
        
        if not self.is_valid_move(row, col):
            raise ValueError(f"Невозможно установить значение в позицию ({row}, {col})")
        
        if value not in ('X', 'O'):
            raise ValueError("Значение должно быть 'X' или 'O'")
        
        if value != self.current_player:
            raise ValueError(f"Сейчас ходит игрок {self.current_player}")
        
        self.board[row][col] = value
        

        if self.check_win(row, col):
            self.game_over = True
            self.winner = value

        elif self.check_draw():
            self.game_over = True
        else:

            self.current_player = 'O' if self.current_player == 'X' else 'X'
    
    def check_win(self, last_row, last_col):

        player = self.board[last_row][last_col]
        

        if all(self.board[last_row][col] == player for col in range(self.size)):
            return True
        
 
        if all(self.board[row][last_col] == player for row in range(self.size)):
            return True
        

        if last_row == last_col:
            if all(self.board[i][i] == player for i in range(self.size)):
                return True
        
 
        if last_row + last_col == self.size - 1:
            if all(self.board[i][self.size - 1 - i] == player for i in range(self.size)):
                return True
        
        return False
    
    def check_draw(self):

        for row in range(self.size):
            for col in range(self.size):
                if self.board[row][col] == ' ':
                    return False
        return True
    def make_move(self, row, col):

        try:
            if self[(row, col)] == ' ':
                
                    self[(row, col)] = self.current_player
                    return True
            return False
        except (ValueError, IndexError):
                return False
        
    def get_board_state(self):

        return [row[:] for row in self.board]
        
    def reset(self):
 
        self.board = [[' ' for _ in range(self.size)] for _ in range(self.size)]
        self.current_player = 'X'
        self.game_over = False
        self.winner = None
        
    def str(self):

        lines = []
        for i, row in enumerate(self.board):
            line = " | ".join(row)
            lines.append(line)
            if i < self.size - 1:
                lines.append("-" * (self.size * 4 - 3))
        return "\n".join(lines)



if __name__ == "__main__":
    game = TicTacToe()
    
    while not game.winner:
        moves = input().split()
        raw = int(moves[0])
        line = int(moves[1])
        while not game.make_move(raw, line):
            print("Некорректный ход, попробуйте снова.")
            moves = input().split()
            raw = int(moves[0])
            line = int(moves[1])
        game.make_move(raw, line)

    
    print(game)
    print(f"Победитель: {game.winner}")
    print(f"Игра окончена: {game.game_over}")

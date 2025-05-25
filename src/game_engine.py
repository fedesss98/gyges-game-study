from src.boards import GygesBoard
from players import Player

import numpy as np


class GygesGame:
    def __init__(self, white_pieces, black_pieces, board_size=6, max_turns=200):
        self.gameboard = GygesBoard(board_size)

        self._active_player = 1  # White player starts
        self.over = False
        self.winning_player = None
        self.max_turns = max_turns
        
        self.player0 = None
        self.player1 = None

        # White pieces are in row 0
        w_starting_row = self.closest_white_row
        b_starting_row = self.closest_black_row
        for i, piece in enumerate(white_pieces):
            self.gameboard[w_starting_row, i] = piece
        # Black pieces are in row -1
        for i, piece in enumerate(black_pieces):
            self.gameboard[b_starting_row, i] = piece

    
    @property
    def num_to_player(self):
        return {0: self.player0, 1: self.player1}

    @property
    def player_to_color(self):
        return {0: "B", 1: "W"}
    
    @property
    def active_player(self) -> Player:
        num_to_player = {0: self.player0, 1: self.player1}
        return num_to_player[self._active_player]
    
    @property
    def active_row(self):
        if self.active_player == 1:
            return self.closest_white_row
        elif self.active_player == 0:
            return self.closest_black_row

    @property
    def closest_white_row(self):
        # If no piece is set
        if np.sum(self.gameboard) == 0:
            return 1  # Starting white row
        for i, value in enumerate(np.sum(self.gameboard, axis=1)):
            if value != 0:
                return i
        
    @property
    def closest_black_row(self):
        # If no piece is set
        if np.sum(self.gameboard) == 0:
            return -2  # Starting black row
        # Reverse the list
        for i, value in enumerate(np.sum(self.gameboard, axis=1)[::-1]):
            if value != 0:
                return - (i + 1)
            
    @property
    def status_string(self):
        if self.over:
            return f"PLAYER {self.player_to_color[self.winning_player]} WINS!\n"
        else:
            return f"Player {self.player_to_color[self.active_player]} turn.\n"
        
    def add_players(self, player0, player1):
        for p, obj in zip([player0, player1], [self.player0, self.player1]):
            if isinstance(p, Player):
                obj = p
            else:
                obj = Player(p)
            print(f"Added player: {p} to the game.")
        self.player0._num = 0
        self.player1._num = 1

    def clean_board(self):
        for row in self.gameboard:
            for cell in row:
                cell.visited = False

        return self
            
    def select_cell(self, y, x):
        if self.gameboard[y, x] == 0:
            raise ValueError("Invalid Selection!\nNo Piece in the selected Cell")
        
        if self.active_player == 0 and y != self.closest_black_row:
            raise ValueError("Invalid Selection!\nSelected cell must be in the closest black row")
        if self.active_player == 1 and y != self.closest_white_row:
            raise ValueError("Invalid Selection!\nSelected cell must be in the closest black row")
        y_in_range = y != 0 and y != -1 and y != self.gameboard.size
        x_in_range = 0 <= x <= self.gameboard.size
        if y_in_range and x_in_range:
            self.clean_board()
            self.selected_cell = self.gameboard[y, x]
            self.selected_piece = self.gameboard[y, x].value
            # Selected Piece is ready to be moved and cell must be emptied
            self.gameboard[y, x] = 0
            return self.selected_piece
        else:
            raise ValueError("Invalid Selection!\nCell must be within boundaries")
        
    @staticmethod
    def _check_valid_move(dy, dx):
        if dx != 0 and dy != 0:
            raise ValueError("Invalid Move!\nYou can move only on x or y")
        if dx == 0 and dy == 0:
            raise ValueError("Invalid Move!\nYou must move x or y")
        if dx == 0:
            if dy not in [1, -1]:
                raise ValueError("Invalid Move!\nYou can move only by 1 or -1")
        if dy == 0:
            if dx not in [1, -1]:
                raise ValueError("Invalid Move!\nYou can move only by 1 or -1")

    def _check_winning_conditions(self, new_cell):
        if self.active_player == 1: 
            if new_cell.is_black_home:
                self.winning_player = self.active_player
                self.over = True
                return True
            elif new_cell.is_white_home:
                raise ValueError("Invalid Move!\nYou cannot finish in your own home row")
        elif self.active_player == 0:
            if new_cell.is_white_home:
                self.winning_player = self.active_player
                self.over = True
                return True
            elif new_cell.is_black_home:
                raise ValueError("Invalid Move!\nYou cannot finish in your own home row")
        else:
            return False
    
    def slide(self, path, visualize=False):
        current_cell = self.selected_cell
        for i, (dy, dx) in enumerate(path):
            y, x = current_cell.y, current_cell.x
            self.gameboard[y, x].visited = True
            new_y = int(y + dy)
            new_x = int(x + dx)
            if new_x < 0 or new_x >= self.gameboard.size:
                raise ValueError("Invalid Move!\nYou cannot move across borders")
            new_cell = self.gameboard[new_y, new_x]
            message = f"Piece {self.selected_piece} moved from cell {(y, x)} to cell: {(new_y, new_x)}"
            
            # Check winning conditions and returns only at the last step
            if i == len(path) - 1:
                if self._check_winning_conditions(new_cell):
                    return 0  # No more moves, game ends
                else:
                    # The game goes on
                    self.selected_cell = new_cell
                    # print(message)
                    if visualize:
                        print(self)
                    return new_cell.value
            else:
                # Prevent invalid passages on occupied cells or home rows
                if new_cell.is_black_home or new_cell.is_white_home:
                    raise ValueError("Invalid Move!\nYou cannot pass through the home row")
                if new_cell.value:
                    raise ValueError("Invalid Move!\nYou cannot pass through an occupied Cell")
            # print(message)
            current_cell = new_cell
            if visualize:
                print(self)

    def place_piece(self):
        y, x = self.selected_cell.y, self.selected_cell.x
        self.gameboard[y, x] = self.selected_piece

    def make_complete_movement(game, cell, strategies=[], seed=42):

        if isinstance(seed, np.random.Generator):
            rng = seed
        else:
            rng = np.random.default_rng(seed=seed)
        correct_moves = [
            (1, 0), (-1, 0), (0, -1), (0, 1)
        ]
        game.select_cell(*cell)
        jump = game.selected_piece
        i = 0
        jump = 2
        while jump > 0:
                random_strategy = rng.choice(correct_moves, jump, replace=True)
                if len(strategies) - 1 < i:
                    strategies.append(random_strategy)
                elif strategies[i] is None:
                    # Generate a random value
                    strategies[i] = random_strategy
                
                strategy = strategies[i]

                try:
                    jump = game.slide(strategy, visualize=False)
                except ValueError:
                    strategies[i] = None
                # When a valid strategy is found, overwrite the value
                strategies[i] = strategy
                i += 1

        game.place_piece()
        return strategies
    
    def play_game(self, max_turns=None, seed=None):
        if seed is None or isinstance(seed, np.random.Generator):
            rng = seed
        else:
            rng = np.random.default_rng(seed)

        max_turns = max_turns if max_turns is not None else self.max_turns
        while not self.over and t < max_turns:
            selected_cell = self.active_player.choose_piece(self.gameboard)

            movements = make_complete_movement(game, selected_cell, seed=rng)

            # The strategy is a collection of all the moves for a selected cell in a turn
            strategy[t] = [selected_cell, [m.tolist() for m in movements]]
            t += 1
            game.player = (game.player + 1) % 2 
        
        print(game)
    
    def __repr__(self):
        string = str(self.gameboard)
        string += self.status_string
        return string
        

if __name__ == "__main__":
    w_starting_config = [2, 1, 3, 2, 3, 1]
    b_starting_config = [2, 1, 3, 3, 1, 2]
    game = GygesGame(w_starting_config, b_starting_config)
    print(game)
    game.add_players("B", "W")
    game.play_game(max_turns=10)
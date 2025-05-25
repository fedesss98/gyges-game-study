try:
    from boards import GygesBoard
    from players import Player
except ModuleNotFoundError:
    from src.boards import GygesBoard
    from src.players import Player

from datetime import datetime
import json
import logging
import numpy as np
from pathlib import Path

BOARD_SIZE = 6
MAXIMUM_WRONG_CHOICES = 20
MAXIMUM_WRONG_MOVES = 1000

class GygesGame:
    def __init__(self, white_pieces, black_pieces, board_size=6, max_turns=200):
        self.gameboard = GygesBoard(board_size)

        self._active_player = 1  # White player starts
        self.is_playing = False
        self.over = False
        self.game_data = {}
        self.winning_player = None
        self.max_turns = max_turns
        
        self.player0 = None
        self.player1 = None

        # White pieces are in row 0
        self.w_starting_config = white_pieces
        self.b_starting_config = black_pieces
        w_starting_row = self.closest_white_row
        b_starting_row = self.closest_black_row
        for i, piece in enumerate(white_pieces):
            self.gameboard[w_starting_row, i] = piece
        # Black pieces are in row -1
        for i, piece in enumerate(black_pieces):
            self.gameboard[b_starting_row, i] = piece

    @property
    def player_to_color(self):
        return {0: "B", 1: "W"}
    
    @property
    def active_player(self) -> Player:
        num_to_player = {0: self.player0, 1: self.player1}
        return num_to_player[self._active_player]
    
    @active_player.setter
    def active_player(self, value):
        self._active_player = value
    
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
    def moves_dict(self):
        return {1: (-1, 0), 2: (1, 0), 3: (0, -1), 4: (0, 1)}
            
    @property
    def status_string(self):
        if self.over:
            return f"PLAYER {self.winning_player} WINS!\n"
        elif self.is_playing:
            return f"Player {self.active_player} turn.\n"
        else:
            return f"It's a DRAW!\n"
        
    def add_players(self, player0, player1):
        """Add players: remember that the last added player will start!"""
        if isinstance(player0, Player):
            self.player0 = player0
        else:
            self.player0 = Player(player0)
            print(f"Added player: {player1} to the game.")
        if isinstance(player1, Player):
            self.player1 = player1
        else:
            self.player1 = Player(player1)
            print(f"Added player: {player1} to the game.")
        
        self.player0._num = 0
        self.player1._num = 1

    def start(self):
        if not isinstance(self.player0, Player) or not isinstance(self.player1, Player):
            raise ValueError("Game cannot start without players!")
        
        self.over = False
        self.is_playing = True
        self.game_data = {}
        self.clean_board()
        print(f"Starting a new game of Gyges!\n\nInitial configuration:\n{self}")

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
            # # Selected Piece is ready to be moved and cell must be emptied
            # self.gameboard[y, x] = 0
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
                self.is_playing = False
                return True
            elif new_cell.is_white_home:
                raise ValueError("Invalid Move!\nYou cannot finish in your own home row")
        elif self.active_player == 0:
            if new_cell.is_white_home:
                self.winning_player = self.active_player
                self.over = True
                self.is_playing = False
                return True
            elif new_cell.is_black_home:
                raise ValueError("Invalid Move!\nYou cannot finish in your own home row")
        else:
            return False
    
    def slide(self, strategy, visualize=False):
        current_cell = self.selected_cell
        try:
            path = [self.moves_dict[k] for k in strategy]
        except KeyError:
            raise ValueError(f"Invalid Move!\nTry one in {self.moves_dict.keys()}")
        for i, (dy, dx) in enumerate(path):
            y, x = current_cell.y, current_cell.x
            self.gameboard[y, x].visited = True
            new_y = int(y + dy)
            new_x = int(x + dx)
            if new_x < 0 or new_x >= self.gameboard.size:
                raise ValueError("Invalid Move!\nYou cannot move across borders")
            new_cell = self.gameboard[new_y, new_x]
            message = f"Piece {self.selected_piece} moved from cell {(y, x)} to cell: {(new_y, new_x)}"
            # if new_cell.is_black_home or new_cell.is_white_home:
                # logging.warning(f"HOME ROW: {message}")
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

    def place_piece(self, starting_cell):
        # Remove Piece from its old cell and
        old_y, old_x = starting_cell
        self.gameboard[old_y, old_x] = 0
        # And place it in the new cell
        y, x = self.selected_cell.y, self.selected_cell.x
        self.gameboard[y, x] = self.selected_piece

    def make_complete_movement(self, cell):
        """
        A 'complete movement' is made up of:
        - piece selection
        - number of moves dependant upon the value of the piece and the strategy
        - piece placement in the final position
        """
        self.select_cell(*cell)
        available_moves = self.selected_piece
        strategies = []
        wrong_moves = 0
        max_wm = MAXIMUM_WRONG_MOVES
        while available_moves > 0 and wrong_moves < max_wm:
                strategy = self.active_player.choose_strategy(available_moves)
                # Try the strategy:
                try:
                    available_moves = self.slide(strategy, visualize=False)
                except ValueError:
                    self.active_player._turn_strategy.pop()
                    if self.active_player.soul == 'human':
                        print(f" invalid sequence of moves {strategy}")
                    # If this returns an error, nothing happens and a new strategy is chosen
                    wrong_moves += 1
                else:
                    # When a valid strategy is found, overwrite the value
                    if self.active_player.soul == 'human' and available_moves > 0:
                        print(f" you jumped on piece with value {available_moves}, continue...")
                    strategies.extend(strategy)
            
        if wrong_moves == max_wm:
            raise ValueError(f"Player {self.active_player} is stuck. Conceding.")

        return strategies
    
    def concede_game(self):
        print(f"\n*** Player {self.active_player} concedes ***\n")
        self.over = True
        self.winning_player = (self.active_player + 1) % 2
        self.is_playing = False
    
    def play_game(self, max_turns=None, verbose=False):
        if not self.is_playing:
            raise ValueError("You must explicitly start the game first!")
        t = 0
        max_turns = max_turns if max_turns is not None else self.max_turns
        wrong_choices = 0
        max_wc = MAXIMUM_WRONG_CHOICES
        wrong_pieces = []
        while not self.over and t < max_turns and wrong_choices < max_wc:
            # Active player takes turn
            try:
                chosen_cell = self.active_player.choose_piece(self.gameboard)
            except ValueError as e:
                # The player cannot chose any Piece and concedes
                self.concede_game()
            try:
                movements = self.make_complete_movement(chosen_cell)
            except ValueError as e:
                # Player is stuck, choose another cell
                wrong_choices += 1
                wrong_pieces.append(chosen_cell[1])
                self.active_player._turn_strategy = []
            else:
                self.place_piece(starting_cell=chosen_cell)
                wrong_pieces = []  # Reset array
                # The strategy is a collection of all the moves for a selected cell in a turn
                if self.active_player.verbose:
                    print(f"  strategy: {self.active_player.strategy}")
                self.game_data[t] = [chosen_cell, movements, self.gameboard.status.tolist()]
                # Prepare next turn
                t += 1
                # Next Player
                self.active_player = (self.active_player + 1) % 2
                if verbose:
                    print(self)
        
        if wrong_choices == max_wc:
            # The active player couldn't find a good piece and concedes
            self.concede_game()

        if not self.over:
            print("Time is up!\n")
            # Force the game to stop with a draw
            self.is_playing = False   

        print(self)

    def save(self, path=None):
        """Save the game dynamics in JSON format"""
        if path is None:
            root = Path(__file__).parent.parent
            now = datetime.now()
            file_id = f"{now.year}{now.month}{now.day}{now.hour}{now.minute}"
            path = Path(root / f"data/game_{file_id}.json")

        self.game_data['meta'] = {
            'name': str(path),
            'player0': {
                'name': self.player0.name, 
                'seed': self.player0._seed,
                'starting config': self.b_starting_config},
            'player1': {
                'name': self.player1.name, 
                'seed': self.player1._seed,
                'starting config': self.w_starting_config},
        }
        
        with open(path, "w") as f:
            json.dump(self.game_data, f)

    
    def __repr__(self):
        string = str(self.gameboard)
        string += self.status_string
        return string
        

if __name__ == "__main__":
    w_starting_config = [2, 1, 3, 2, 3, 1]
    b_starting_config = [2, 1, 3, 3, 1, 2]
    pw = Player("W", soul='random', seed=7568, verbose=True)
    pb = Player("B", soul='random', seed=56764, verbose=True)
    game = GygesGame(w_starting_config, b_starting_config)
    game.add_players(pb, pw)
    game.start()
    game.play_game(max_turns=500, verbose=True)
    game.save(path="data/try_game.json")

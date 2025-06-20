try:
    from boards import GygesBoard
except ModuleNotFoundError:
    from src.boards import GygesBoard
    

import numpy as np


class Player:
    def __init__(self, name, soul='random', seed=42, verbose=False):
        self.name = name
        self._num = None  # This will be assigned by the game
        self.soul = soul
        self.is_playing = False
        self._turn_strategy = []

        self.rng = None
        self._seed = self.seed(int(seed))
        
        self.verbose = verbose

    def seed(self, seed):
        if seed is None:
            return None
        if isinstance(seed, np.random.Generator):
            self.rng = seed
            return None
        else:
            self.rng = np.random.default_rng(seed=seed)
            return seed

    def active_row(self, board: GygesBoard):
        if self._num == 1:
            return self.closest_white_row(board)
        elif self._num == 0:
            return self.closest_black_row(board)
        
    def closest_white_row(self, board: GygesBoard):
        for i, value in enumerate(np.sum(board, axis=1)):
            if value != 0:
                return i
        
    def closest_black_row(self, board: GygesBoard):
        # Reverse the list and then check
        for i, value in enumerate(np.sum(board, axis=1)[::-1]):
            if value != 0:
                return - (i + 1)
            
    @property
    def moves_dict(self):
        return {1: (-1, 0), 2: (1, 0), 3:(0, -1), 4:(0, 1)}
    
    @property
    def strategy(self):
        return self._turn_strategy

    def choose_piece(self, board: GygesBoard):
        # Reset strategy
        self._turn_strategy = []
        active_row = self.active_row(board)
        cells_with_pieces = [
            i for i in range(board.size) 
            if board[active_row, i].value > 0]
        
        if self.soul == 'random':
            cell = int(self.rng.choice(cells_with_pieces))
        elif self.soul == 'human':
            while True:
                cell = int(input(
                    f"You can choose a Piece in row {active_row} ({cells_with_pieces}): "))
                if cell not in cells_with_pieces:
                    print("Bad column selection")
                else:
                    break
        cell = (active_row, cell)
        if self.verbose:
            print(f"{self.name}: select cell {cell} with value {board[cell]}.")
        return cell
    
    def choose_strategy(self, n_moves):
        movements = []
        if self.soul == 'human':
            while len(movements) < n_moves:
                movement = int(input(
                    "Input a move (1: UP), (2: DOWN), (3: LEFT), (4: RIGHT): "))
                if movement in self.moves_dict.keys():
                    movements.append(movement)
                else:
                    print(" invalid move")
        elif self.soul == 'random':
            movements = self.rng.choice(
                range(1, len(self.moves_dict) + 1), n_moves, replace=True)
            movements = movements.tolist()

        self.strategy.append(movements)
        return movements

    def __eq__(self, value):
        return self._num == value
    
    def __add__(self, other):
        if isinstance(other, Player):
            return self._num + other._num
        else:
            return self._num + other

    def __str__(self):
        return str(self.name)

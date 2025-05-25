from src.boards import GygesBoard

import numpy as np


class Player:
    def __init__(self, name, soul='random', seed=42, verbose=False):
        self.name = name
        self._num = None  # This will be assigned by the game
        self.soul = soul
        self.is_playing = False

        self.rng = None
        if seed is not None:
            self.seed(seed)
        
        self.verbose = verbose

    def seed(self, seed):
        if isinstance(seed, np.random.Generator):
            self.rng = seed
        else:
            self.rng = np.random.default_rng(seed=seed)
        self.rng = np.random.default_rng(seed=seed)

    def active_row(self, board: GygesBoard):
        if self._num == 1:
            return self.closest_white_row(board)
        elif self._num == 0:
            return self.closest_black_row(board)
        
    def closest_white_row(self, board: GygesBoard):
        for i, value in enumerate(np.sum(self.gameboard, axis=1)):
            if value != 0:
                return i
        
    def closest_black_row(self, board: GygesBoard):
        # Reverse the list and then check
        for i, value in enumerate(np.sum(self.gameboard, axis=1)[::-1]):
            if value != 0:
                return - (i + 1)

    def choose_piece(self, board: GygesBoard):
        active_row = self.active_row(board)
        cells_with_pieces = [
            i for i in range(board.size) 
            if board[active_row, i].value > 0]

        if self.soul == 'random':
            cell = int(self.rng.choice(cells_with_pieces))
        elif self.soul == 'human':
            while True:
                cell = input(
                    f"You can choose a Piece in row {active_row} ({cells_with_pieces}): ")
                if cell[0] != active_row:
                    print("Bad row selection")
                elif cell[1] not in cells_with_pieces:
                    print("Bad column selection")
                else:
                    break
        cell = (active_row, cell)
        if self.verbose:
            print(f"{self.name}: select cell {cell}.")
        return cell
    

    def __eq__(self, value):
        return self._num == value


    def __str__(self):
        return str(self.name)

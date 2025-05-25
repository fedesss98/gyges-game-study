import numpy as np


class GygesBoard:
    def __init__(self, size):
        self.size = size
        self.board = np.array([
            [Cell(x, y) for x in range(size)]
            for y in range(size + 2)
        ])
        # Set the home rows
        for j in range(size):
            self[0, j].is_white_home = True
            self[-1, j].is_black_home = True

    def __len__(self):
        return self.size

    def __getitem__(self, idx):
        return self.board[idx]

    def __setitem__(self, idx, value):
        self.board[idx].value = value

    def __iter__(self):
        return iter(self.board)

    def __repr__(self):
        string = ""
        for j in range(self.size + 2):
            if j == 0:
                j_idx = 'W'
            elif j == self.size + 1:
                j_idx = 'B'
            else:
                j_idx = j
            string += f"{j_idx}| {' '.join(f'{str(item):^3}' for item in self.board[j])} |\n"
        
        string += f"   {' '.join(f'{str(n):^3}' for n in range(self.size))} \n"
        return string


class Cell:
    def __init__(self, x=0, y=0, value=0):
        self.x = x
        self.y = y
        self.value = value
        self.visited = False
        self.is_white_home = False
        self.is_black_home = False

    def __add__(self, other):
        if isinstance(other, Cell):
            return Cell(value = self.value + other.value)
        elif isinstance(other, int) or isinstance(other, float):
            return Cell(value = self.value + other)
        else:
            raise ValueError("Can add only Cells, Integers or Floats")
        
    def __eq__(self, value):
        return self.value == value

    def __repr__(self):
        if self.is_white_home or self.is_black_home:
            return '-'
        if self.visited:
            return f"{self.value if self.value > 0 else ''}x"
        else:
            return str(self.value)


if __name__ == "__main__":
    b = GygesBoard(6)
    b[1, 2] = 1
    print(b)
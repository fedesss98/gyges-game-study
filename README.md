# Gygenator
This repository contains Python code to simulate a game of Gyges.

**Players** can be AI agents or real players prompted to input their moves.

## Gyges Game
Each Gyges Player has a *Home Row* in front of him and faces a 6x6 board.
The goal of the game is to take one piece into the adversary Home Row.

### Setup
Each Player places his six pieces on the first row of the board nearer to his Home Row. Each piece has a *value*: 2 pieces with value 1, 2 with value 2 and 2 with value 3.

### Game Mechanics
The game loop is like this:
1) The active Player selects a piece on the row nearest to his *Home Row*;
2) A random sequence of allowed moves (up, down, left, right) is selected, the length of which is given by the *value* of the selected piece;
3) The sequence of moves is evaluated step by step, to see if it results in a valid move overall (e.g. cannot pass through occupied cells or home rows if not at the last step of the movement). If the whole sequence is not valid, generate a new one;
4) At the end of the whole movement, if the piece ends up in an empty valid cell, the Player turn ends. Else, if the piece ends its movement in a cell where another piece is, another sequence of movements is allowed (it jumps on the piece) Repeat step 3) and 4) accordingly.
5) The active Player changes and the loop is repeated.

---
## Playing a Game
You can play a game running:
```bash
python play.py
```
This script accepts command-line arguments:
- **`-b`**: play as the black player (starting from the lower edge of the board, he starts second) *[default=False]*,
- **`-s`** or **`--seed`**: give a seed to the Random Number Generator of your opponent *[default = 42]*,
- **`--save-path`**: path to a JSON file in which to save the game.

## AI
This game is perfect for training an AI agent with Reinforcement Learning.

### Training
Training requires providing a number of *games* to the algorithm. Games need to be *encoded* in order to be understood by the machine. 

Each game turn can be encoded with a stack of matrices (*channels*).
Note that we consider each *jump* on a Piece as a new turn for the same Player, as opposed to a continuation of the old turn.
All matrices are *NxN*, where *N* is the size of the board. 
Key informations are encoded with numbers ranging from 0 to 1 (normalization helps machines).
1) **Current Player**: A matrix of zeros for Player 0 (Black) and ones for Player 1 (White);
2) **Initial Board State**: A matrix representing the normalized state of the board before the move, where each element has a value depending on the piece that sits on it;    
2) **Final Board State**: A matrix representing the normalized state of the board after, where each element has a value depending on the piece that sits on it;    
3) **Selectable Pieces**: These are the Pieces accessible to the active Player, in the row nearest to his Home Row. They are encoded as ones in a Matrix of zeros;
4) **Chosen Piece**: The Piece selected by the active Player. This can be encoded with a one in its starting position;
5) **Move**: Each step of the Piece is represented on a Matrix of zeros with the value corresponding to the number of the step, normalized;
6) **Reward**: Each move is evaluated from the final result of the match (1 for wins, -1 for draws and -5 for losses) multiplied by the *discount factor* which is inversely proportional to the number of moves remaining to the end of the game. This is a matrix filled with this value.


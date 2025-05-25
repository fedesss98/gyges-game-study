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
## AI
This game is perfect for training an AI agent with Reinforcement Learning


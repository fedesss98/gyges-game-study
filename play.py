from src.players import Player
from src.game_engine import GygesGame

import argparse
import numpy as np


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-b", action="store_true", help="Play as Black.")
    parser.add_argument("-s", "--seed", default=42, type=int, help="Seed for random generators.")
    parser.add_argument("--save-path", default=None, type=int, help="Path to JSON file where to save the file.")

    return parser.parse_args()


def choose_starting_config():
    # Prompt the user for a valid starting configuration
    while True:
        starting_config = input(
            "Input your starting configuration as a sequence of piece values: "
        )
        # Convert to list of integers
        starting_config = [int(i) for i in starting_config]
        print(starting_config)
        errors = 0
        for v in [1, 2, 3]:
            num = sum([1 for i in starting_config if i == v])
            if num != 2:
                print(f"You should have two pieces with value {v}!")
                errors += 1
        if errors == 0:
            break
    return starting_config


def main():
    args = parse_arguments()
    print(f"\n{'*'*10} Running a new game of Gyges {'*'*10}\n")
    rng = np.random.default_rng(seed=args.seed)
    
    starting_config = choose_starting_config()
        
    random_config = [2, 1, 3, 3, 1, 2]
    rng.shuffle(random_config)
    
    if not args.b:
        pw = Player("W", soul='human', verbose=True)
        w_starting_config = starting_config
        pb = Player("B", soul='random', seed=args.seed, verbose=True)
        b_starting_config = random_config
    else:
        pw = Player("W", soul='random', seed=args.seed, verbose=True)
        w_starting_config = random_config
        pb = Player("B", soul='human', verbose=True)
        b_starting_config = starting_config

    game = GygesGame(w_starting_config, b_starting_config)
    game.add_players(pb, pw)
    game.start()
    game.play_game(max_turns=1000, verbose=True)
    if args.save_path:
        game.save(path=args.save_path)


if __name__ == "__main__":
    main()
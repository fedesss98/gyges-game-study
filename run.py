from src.players import Player
from src.game_engine import GygesGame

import numpy as np

# Past seed 32579
SEED = 492
RUNS = 100

if __name__ == "__main__":
    print(f"\n{'*'*10} Running {RUNS} games {'*'*10}\n")
    generators_generator = np.random.default_rng(seed=SEED)
    w_starting_config = [2, 1, 3, 2, 3, 1]
    b_starting_config = [2, 1, 3, 3, 1, 2]
    for seed_p0, seed_p1 in generators_generator.integers(1, 99999, (RUNS, 2)):
        
        generators_generator.shuffle(w_starting_config)
        generators_generator.shuffle(b_starting_config)
        
        pw = Player("W", soul='random', seed=seed_p1, verbose=True)
        pb = Player("B", soul='random', seed=seed_p0, verbose=True)

        game = GygesGame(w_starting_config, b_starting_config)
        game.add_players(pb, pw)
        game.start()
        game.play_game(max_turns=1000, verbose=False)
        game.save(path=f"data/game_{seed_p0}_{seed_p1}.json")

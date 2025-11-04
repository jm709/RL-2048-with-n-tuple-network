import numpy as np
import pickle
import time
from pathlib import Path
from nTupleAgent import nTupleNetwork
from game import Board, IllegalAction, GameOver, LEFT, RIGHT, UP, DOWN

# ANSI color codes for terminal
COLORS = {
    0: '\033[48;5;250m',  # Empty - light gray
    1: '\033[48;5;231m',  # 2 - white
    2: '\033[48;5;229m',  # 4 - light yellow
    3: '\033[48;5;223m',  # 8 - yellow
    4: '\033[48;5;216m',  # 16 - orange
    5: '\033[48;5;209m',  # 32 - dark orange
    6: '\033[48;5;203m',  # 64 - red
    7: '\033[48;5;197m',  # 128 - dark red
    8: '\033[48;5;226m',  # 256 - bright yellow
    9: '\033[48;5;220m',  # 512 - gold
    10: '\033[48;5;214m',  # 1024 - orange-gold
    11: '\033[48;5;208m',  # 2048 - bright orange
    12: '\033[48;5;202m',  # 4096 - red-orange
    13: '\033[48;5;196m',  # 8192 - bright red
    14: '\033[48;5;160m',  # 16384 - dark red
    15: '\033[48;5;124m',  # 32768 - maroon
}
RESET = '\033[0m'
BOLD = '\033[1m'

ACTION_NAMES = {LEFT: "LEFT", RIGHT: "RIGHT", UP: "UP", DOWN: "DOWN"}


def load_agent(path):
    """Load a trained agent from pickle file"""
    with open(path, 'rb') as f:
        return pickle.load(f)


def print_board(board, score, move_num, last_action=None):
    """Pretty print the board with colors"""
    print("\n" + "=" * 50)
    print(f"Move: {move_num} | Score: {score}")
    if last_action is not None:
        print(f"Last Action: {ACTION_NAMES[last_action]}")
    print("=" * 50)

    for row in board:
        print("  ", end="")
        for cell in row:
            val = int(cell)
            if val == 0:
                tile_str = "."
            else:
                tile_str = str(2 ** val)

            color = COLORS.get(val, RESET)
            print(f"{color}{BOLD}{tile_str:>6}{RESET}", end="  ")
        print()
    print()


def play_game(agent, delay=0.5, verbose=True):
    """
    Play a single game with the trained agent

    Args:
        agent: Trained nTupleNetwork agent
        delay: Delay in seconds between moves (for visualization)
        verbose: Whether to print the board after each move

    Returns:
        dict with game statistics
    """
    b = Board(None)  # Initialize new game
    score = 0
    move_num = 0
    max_tile = 0

    if verbose:
        print_board(b.board, score, move_num)
        time.sleep(delay)

    while True:
        try:
            # Get best action from agent
            action = agent.best_action(b.board)

            # Make the move
            reward = b.move(action)
            score += reward
            move_num += 1

            # Spawn new tile
            b.spawn_tile()

            # Track max tile
            max_tile = max(max_tile, np.max(b.board))

            if verbose:
                print_board(b.board, score, move_num, action)
                time.sleep(delay)

        except GameOver:
            if verbose:
                print("GAME OVER - Board is full!")
            break
        except IllegalAction:
            if verbose:
                print("GAME OVER - No legal moves!")
            break
        except Exception as e:
            if verbose:
                print(f"GAME OVER - Error: {e}")
            break

    final_max_tile = 2 ** int(np.max(b.board))

    return {
        'score': score,
        'moves': move_num,
        'max_tile': final_max_tile,
        'board': b.board
    }


def play_multiple_games(agent, n_games=10, delay=0, verbose=False):
    """
    Play multiple games and show statistics

    Args:
        agent: Trained agent
        n_games: Number of games to play
        delay: Delay between moves (0 for fast simulation)
        verbose: Whether to print each game
    """
    results = []

    print(f"\nPlaying {n_games} games...")
    print("-" * 60)

    for i in range(n_games):
        result = play_game(agent, delay=delay, verbose=verbose)
        results.append(result)

        if not verbose:
            print(f"Game {i + 1:3d}: Score={result['score']:6.0f}, "
                  f"Moves={result['moves']:4d}, Max Tile={result['max_tile']:5d}")

    # Print statistics
    scores = [r['score'] for r in results]
    moves = [r['moves'] for r in results]
    max_tiles = [r['max_tile'] for r in results]

    print("\n" + "=" * 60)
    print("STATISTICS")
    print("=" * 60)
    print(f"Average Score:    {np.mean(scores):.1f} (±{np.std(scores):.1f})")
    print(f"Average Moves:    {np.mean(moves):.1f} (±{np.std(moves):.1f})")
    print(f"Average Max Tile: {np.mean(max_tiles):.1f}")
    print(f"Best Max Tile:    {max(max_tiles)}")
    print(f"Max Tile Distribution:")

    from collections import Counter
    tile_counts = Counter(max_tiles)
    for tile in sorted(tile_counts.keys(), reverse=True):
        count = tile_counts[tile]
        pct = 100 * count / n_games
        print(f"  {tile:5d}: {count:3d} games ({pct:5.1f}%)")


def main():
    # Load agent
    path = Path("tmp")
    saves = list(path.glob("*.pkl"))

    if len(saves) == 0:
        print("No saved agents found in 'tmp/' directory!")
        return

    print("Found saved agents:")
    for i, f in enumerate(saves):
        print(f"{i:2d} - {f.name}")

    k = input("\nEnter agent ID to load: ")
    if k.strip() == "":
        print("No agent selected!")
        return

    agent_path = saves[int(k)]
    print(f"\nLoading agent from {agent_path}...")
    n_games, agent = load_agent(agent_path)
    print(f"Agent trained on {n_games} games")

    # Menu
    while True:
        print("\n" + "=" * 60)
        print("OPTIONS")
        print("=" * 60)
        print("1. Watch one game (with visualization)")
        print("2. Watch one game (fast)")
        print("3. Simulate multiple games (statistics only)")
        print("4. Exit")

        choice = input("\nYour choice: ").strip()

        if choice == "1":
            delay = float(input("Delay between moves (seconds, e.g. 0.5): ") or "0.5")
            play_game(agent, delay=delay, verbose=True)

        elif choice == "2":
            play_game(agent, delay=0, verbose=True)

        elif choice == "3":
            n = int(input("Number of games to simulate: ") or "10")
            play_multiple_games(agent, n_games=n, delay=0, verbose=False)

        elif choice == "4":
            print("Goodbye!")
            break

        else:
            print("Invalid choice!")


if __name__ == "__main__":
    main()
from nTupleAgent import nTupleNetwork
from game import Board, IllegalAction, GameOver
import pickle
from collections import namedtuple
import numpy as np

Transition = namedtuple("Transition", "s, a, r, s_after, s_next")
Gameplay = namedtuple("Gameplay", "transition_history game_reward max_tile")


def game(board, agent):
    b = Board(board)
    game_r = 0
    num_a = 0
    history = []
    while True:
        s = b.copy_board()
        try:
            a_best = agent.best_action(s)
            r = b.move(a_best)
            game_r += r
            s_after = b.copy_board()
            b.spawn_tile()
            s_next = b.copy_board()
        except GameOver as e:
            # game ends when agent makes illegal moves or board is full
            r = None
            s_after = None
            s_next = None
            break
        except IllegalAction as e:
            # game ends when agent makes illegal moves or board is full
            r = None
            s_after = None
            s_next = None
            break

        finally:
            num_a += 1
            history.append(
                Transition(s=s, a=a_best, r=r, s_after=s_after, s_next=s_next)
            )
    gp = Gameplay(
        transition_history=history,
        game_reward=game_r,
        max_tile=2 ** np.max(b.board),
    )
    learn_from_gameplay(agent, gp)
    return gp


def learn_from_gameplay(agent, gp, alpha=0.1):
    for tr in gp.transition_history[:-1][::-1]:
        agent.learn(tr.s, tr.a, tr.r, tr.s_after, tr.s_next, alpha=alpha)


def load_agent(path):
    return pickle.load(path.open("rb"))

TUPLES = [
    # 4 horz
    [(0, 0), (0, 1), (0, 2), (0, 3)],
    [(1, 0), (1, 1), (1, 2), (1, 3)],
    [(2, 0), (2, 1), (2, 2), (2, 3)],
    [(3, 0), (3, 1), (3, 2), (3, 3)],
    # 4 vert
    [(0, 0), (1, 0), (2, 0), (3, 0)],
    [(0, 1), (1, 1), (2, 1), (3, 1)],
    [(0, 2), (1, 2), (2, 2), (3, 2)],
    [(0, 3), (1, 3), (2, 3), (3, 3)],
    # 9 box
    [(0, 0), (0, 1), (1, 0), (1, 1)],
    [(0, 2), (0, 3), (1, 2), (1, 3)],
    [(2, 0), (2, 1), (3, 0), (3, 1)],
    [(2, 2), (2, 3), (3, 2), (3, 3)],
    [(1, 0), (1, 1), (2, 0), (2, 1)],
    [(1, 2), (1, 3), (2, 2), (2, 3)],
    [(0, 1), (0, 2), (1, 1), (1, 2)],
    [(1, 1), (1, 2), (2, 1), (2, 2)],
    [(2, 2), (2, 3), (3, 1), (3, 2)],
]

if __name__ == "__main__":
    agent = None
    # prompt to load saved agents
    from pathlib import Path

    path = Path("tmp")
    saves = list(path.glob("*.pkl"))
    if len(saves) > 0:
        print("Found %d saved agents:" % len(saves))
        for i, f in enumerate(saves):
            print("{:2d} - {}".format(i, str(f)))
        k = input(
            "input the id to load an agent, input nothing to create a fresh agent:"
        )
        if k.strip() != "":
            k = int(k)
            n_games, agent = load_agent(saves[k])
            print("load agent {}, {} games played".format(saves[k].stem, n_games))
    if agent is None:
        print("initialize agent")
        n_games = 0
        agent = nTupleNetwork(TUPLES)
    n_session = 5000
    n_episode = 100
    print("training")
    try:
        for i_se in range(n_session):
            gameplays = []
            for i_ep in range(n_episode):
                gp = game(None, agent)
                gameplays.append(gp)
                n_games += 1


            n2048 = sum([1 for gp in gameplays if gp.max_tile == 2048])
            mean_maxtile = np.mean([gp.max_tile for gp in gameplays])
            maxtile = max([gp.max_tile for gp in gameplays])
            mean_gamerewards = np.mean([gp.game_reward for gp in gameplays])
            print(
                "Game# %d, tot. %dk games, " % (n_games, n_games / 1000)
                + "mean game rewards {:.0f}, mean max tile {:.0f}, 2048 rate {:.0%}, maxtile {}".format(
                    mean_gamerewards, mean_maxtile, n2048 / len(gameplays), maxtile
                ),
            )
    except KeyboardInterrupt:
        print("training interrupted")
        print("{} games played by the agent".format(n_games))
        if input("save the agent? (y/n)") == "y":
            fout = "tmp/{}_{}games.pkl".format(agent.__class__.__name__, n_games)
            pickle.dump((n_games, agent), open(fout, "wb"))
            print("agent saved to", fout)


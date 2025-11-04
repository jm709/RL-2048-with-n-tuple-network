import numpy as np
from game import LEFT, RIGHT, UP, DOWN, GameOver
from game import Board, IllegalAction


class nTupleNetwork:
    def __init__(self, tuples):
        self.TUPLES = tuples
        self.TARGET_TILE = 15
        self.LUTS = self._init_luts(self.TUPLES)

    def _init_luts(self, tuples):
        luts = []
        for tp in tuples:
            luts.append(np.zeros((self.TARGET_TILE + 1) ** len(tp)))
        return luts

    def best_action(self, s):
        cur_s = Board(s)
        best_reward = -1
        best_action = None
        for action in [LEFT, RIGHT, UP, DOWN]:
            try:
                new_state = Board(s)
                r = new_state.move(action)
                reward = self.value(new_state.copy_board()) + r
                if reward > best_reward:
                    best_reward = reward
                    best_action = action
            except IllegalAction:
                pass
        return best_action

    def tuple_index(self, t):
        t = t[::-1]
        k = 1
        n = 0
        for tile in t:
            if tile >= self.TARGET_TILE:
                raise ValueError("Tile too large")
            n += tile * k
            k *= self.TARGET_TILE
        return int(n)

    def value(self, board, delta=None):
        vals = []
        for (tp, LUT) in (zip(self.TUPLES, self.LUTS)):
            tiles = [board[i][j] for (i,j) in tp]
            id = self.tuple_index(tiles)
            if delta is not None:
                LUT[id] += delta
            v = LUT[id]
            vals.append(v)
        return np.mean(vals)

    def learn(self, s, a, r, s_after, s_next, alpha=0.01):
        a_next = self.best_action(s_next)
        b = Board(s_next)
        try:
            r_next = b.move(a_next)
            s_after_next = b.copy_board()
            v_after_next = self.value(s_after_next)
        except (IllegalAction, GameOver):
            r_next = 0
            v_after_next = 0

        delta = r_next + v_after_next - self.value(s_after)

        self.value(s_after, delta * alpha)


    # ok so we have this board thats actually a sick array 4x4
    # for the LUT each tuple slot has its own value.
    # so LUTS has target**len(tuple) so like if we have 8 tuples
    # [0,1,2,3],[4,5,6,7],[8,9,10,11],[12,13,14,15],[0,1,4,5],[2,3,6,7],[8,9,12,13],[10,11,14,15]
    # ok so lets say we have tuple 1 it's first slot would corrospond to slots 0-15, second to 16-32


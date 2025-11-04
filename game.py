import numpy as np
import random

UP = 0
RIGHT = 1
DOWN = 2
LEFT = 3


class GameOver(Exception):
    pass

class IllegalAction(Exception):
    pass

class Board:
    def __init__(self, board=None):
        if board is None:
            self.reset()
        else:
            self.board = board

    def reset(self):
        self.board = np.zeros((4, 4))
        self.spawn_tile()
        self.spawn_tile()

    def spawn_tile(self):
        zeros = [(i,j) for i in range (4) for j in range (4) if self.board[i, j] == 0]
        if not zeros:
            raise GameOver
        row, col = random.choice(zeros)
        self.board[row, col] = random.choices([1,2], (9,1), k=1)[0]

    def copy_board(self):
        return np.copy(self.board)

    def move(self, direction):
        old_board = self.board
        if direction == LEFT:
            score = self.move_left()
        if direction == RIGHT:
            score = self.move_right()
        if direction == DOWN:
            score = self.move_down()
        if direction == UP:
            score = self.move_up()
        if direction is None:
            raise GameOver()
        if np.array_equal(old_board, self.board):
            raise IllegalAction()
        else:
            return score

    def move_left(self):
        result_board = []
        t_score = 0
        for row in self.board:
            new_row, score = self._slide_row(row)
            t_score += score
            result_board.append(new_row)
        self.board = np.array(result_board)
        return t_score

    def move_right(self):
        self.board = np.rot90(self.board, k=2)
        score = self.move_left()
        self.board = np.rot90(self.board, k=2)
        return score

    def move_down(self):
        self.board = np.rot90(self.board, k=3)
        score = self.move_left()
        self.board = np.rot90(self.board, k=1)
        return score

    def move_up(self):
        self.board = np.rot90(self.board, k=1)
        score = self.move_left()
        self.board = np.rot90(self.board, k=3)
        return score

    def _slide_row(self, row):
        score = 0
        non_zero = row[row != 0]
        merged = []
        i = 0
        while i < len(non_zero):
            if i + 1 < len(non_zero) and non_zero[i] == non_zero[i + 1]:
                merged_value = non_zero[i] + 1
                merged.append(merged_value)
                score += merged_value
                i += 2
            else:
                merged.append(non_zero[i])
                i += 1
        result = np.array(merged + [0] * (4 - len(merged)))
        return result, score

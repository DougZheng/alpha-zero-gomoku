import sys
import numpy as np
from numba import jit

from .board import Board
from .board_gui import BoardGUI

class Gomoku():
    def __init__(self, args):
        self.n = args.n
        self.n_in_row = args.nir

    @jit(nopython=True)
    def get_init_board(self):
        # return initial board (numpy board)
        b = Board(self.n)
        return np.array(b.pieces)

    @jit(nopython=True)
    def get_board_size(self):
        # (a,b) tuple
        return (self.n, self.n)

    @jit(nopython=True)
    def get_action_size(self):
        # return number of actions
        return self.n * self.n

    @jit(nopython=True)
    def get_next_state(self, board, player, action):
        # if player takes action on board, return next (board,player)
        # action must be a valid move
        if action == self.n * self.n:
            return (board, -player)

        b = Board(self.n)
        b.pieces = np.copy(board)
        move = (int(action / self.n), action % self.n)
        b.execute_move(move, player)
        return (b.pieces, -player)

    @jit(nopython=True)
    def get_valid_moves(self, board, player):
        # return a fixed size binary vector
        valids = [0] * self.get_action_size()
        b = Board(self.n)
        b.pieces = np.copy(board)
        legal_moves = b.get_legal_moves(player)

        if len(legal_moves) == 0:
            return None
        for x, y in legal_moves:
            valids[self.n * x + y] = 1
        return np.array(valids)

    @jit(nopython=True)
    def get_game_ended(self, board, player):
        # return 2 if not ended, 1 if player 1 won, -1 if player 1 lost, 0 if tied
        # player = 1
        b = Board(self.n)
        b.pieces = np.copy(board)
        n = self.n_in_row

        for w in range(self.n):
            for h in range(self.n):
                if (w in range(self.n - n + 1) and board[w][h] != 0 and
                        len(set(board[i][h] for i in range(w, w + n))) == 1):
                    return board[w][h]
                if (h in range(self.n - n + 1) and board[w][h] != 0 and
                        len(set(board[w][j] for j in range(h, h + n))) == 1):
                    return board[w][h]
                if (w in range(self.n - n + 1) and h in range(self.n - n + 1) and board[w][h] != 0 and
                        len(set(board[w + k][h + k] for k in range(n))) == 1):
                    return board[w][h]
                if (w in range(self.n - n + 1) and h in range(n - 1, self.n) and board[w][h] != 0 and
                        len(set(board[w + l][h - l] for l in range(n))) == 1):
                    return board[w][h]
        if b.has_legal_moves():
            return 2
        return 0

    @jit(nopython=True)
    def get_canonical_form(self, board, player):
        # return state if player==1, else return -state if player==-1
        return player * board

    # modified
    @jit(nopython=True)
    def get_symmetries(self, board, pi):
        # mirror, rotational
        assert(len(pi) == self.n**2)  # 1 for pass
        pi_board = np.reshape(pi, (self.n, self.n))
        l = []

        for i in range(1, 5):
            for j in [True, False]:
                newB = np.rot90(board, i)
                newPi = np.rot90(pi_board, i)
                if j:
                    newB = np.fliplr(newB)
                    newPi = np.fliplr(newPi)
                l += [(newB, list(newPi.ravel()))]
        return l

    @jit(nopython=True)
    def string_representation(self, board):
        # 8x8 numpy array (canonical board)
        return board.tostring()


if __name__ == "__main__":
    board = Board(15)
    board_gui = BoardGUI(board, True)
    board_gui.loop()
    
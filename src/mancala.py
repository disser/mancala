#!/usr/bin/env python

import logging
import copy
import random
import sys
NUM_PITS = 6

class Board:
    def __init__(self, replay_nonempty=False, capture_empty=True):
        self.score = [0, 0]
        self.pits = [ [4] * NUM_PITS,
                      [4] * NUM_PITS ]
        self.play_again = False
        self.game_over = False
        self.replay_nonempty = replay_nonempty
        self.capture_empty = capture_empty

    def __str__(self):
        return "P0: %s,%d P1: %s,%d" % (self.pits[0], self.score[0], self.pits[1], self.score[1])

def move(board, player, position):
    assert player in (0, 1)
    assert position in range(NUM_PITS)

    board = copy.deepcopy(board)

    class ret:
        pass

    stones = board.pits[player][position]
    side = player
    pit = position
    board.pits[side][pit] = 0 # pick up stones in the pit
    pit += 1
    again = False
    while stones > 0:
        logging.debug("Current pit is %d" % pit)
        assert sum(board.pits[0]) + sum(board.pits[1]) + sum(board.score) + stones == 12*4, "%s + %s" % (board, stones)
        if pit == NUM_PITS: # reached the end of the board
            if side == player: # score only at our end
                stones -= 1
                board.score[player] += 1
                side ^= 1
                pit = 0
                if stones == 0:
                    again = True # we get to play again
                    break
            else:
                pit = 0
                side ^= 1
        else:
            assert side in range(2)
            assert pit in range(NUM_PITS)
            board.pits[side][pit] += 1
            stones -= 1
            pit += 1

    assert sum(board.pits[0]) + sum(board.pits[1]) + sum(board.score) == 12*4, board

    if sum(board.pits[player]) == 0: # did the player clear his side?
        board.score[player] += sum(board.pits[player ^ 1]) # claim opponent's stones
        board.pits[player ^ 1] = [0] * NUM_PITS # clear opponent's side
        board.game_over = True

    assert sum(board.pits[0]) + sum(board.pits[1]) + sum(board.score) == 12*4, board
    return board, again # don't go again


class Strategy(object):
    def __init__(self, player):
        self.player = player

    def best_play(self, board):
        best_score = None
        best_move = None
        best_board = None
        for position in range(NUM_PITS):
            if board.pits[self.player][position] == 0:
                continue
            attempt, again = move(board, self.player, position)
            while again and sum(attempt.pits[self.player]) > 0:
                next_move, attempt = self.best_play(attempt)
                logging.info("Next move from %d" % next_move)
                attempt, again = move(attempt, self.player, next_move)
            score = self.score_board(attempt)
            if best_score is None or score > best_score:
                best_score = score
                best_move = position
                best_board = attempt
        return best_move, best_board

    def score_board(self):
        pass


class RandomStrategy(Strategy):
    def score_board(self, board):
        return random.randint(1, 10)


class GreedyStrategy(Strategy):
    def score_board(self, board):
        return board.score[self.player]

class GreedierStrategy(Strategy):
    def score_board(self, board):
        my_score = board.score[self.player]
        # what would the other player do?
        their_strategy = GreedyStrategy(self.player ^ 1)
        their_move, their_board = their_strategy.best_play(board)
        their_score = their_board.score[self.player ^ 1]
        return my_score - their_score

class HumanStrategy(Strategy):
    def best_play(self, board):
        again = True
        while again:
            logging.info("Current board: %s" % board)
            my_move = None
            while my_move is None:
                try:
                    my_move = int(input("Your Move: "))
                    assert my_move in range(NUM_PITS)
                except KeyboardInterrupt:
                    sys.exit(0)
                except:
                    pass
                else:
                    break
            new_board, again = move(board, self.player, my_move)
            print "again", again
            board = new_board
        return my_move, board

class Game:
    def __init__(self, strategies):
        self.board = Board()
        self.strategies = strategies

    def play(self):
        player = 0
        while self.board.game_over == False:
            strategy = self.strategies[player]
            position, board = strategy.best_play(self.board)
            assert position in range(NUM_PITS)
            logging.info("Player %d moves from position %d, board=%s" % (player, position, board))
            # logging.info("Player 0 has %d stones and Player 1 has %d stones" % (sum(board.pits[0])+board.score[0],
            #                                                                     sum(board.pits[1])+board.score[1]))
            self.board = board
            player = player ^ 1

        logging.info("Game over!  Final score %s" % self.board.score)
        if self.board.score[0] > self.board.score[1]:
            return 0
        else:
            return 1


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    g = Game([GreedyStrategy(0), HumanStrategy(1)])
    g.play()
    print g.board

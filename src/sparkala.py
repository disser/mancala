#!/usr/bin/env python

import logging
from copy import deepcopy
import random
import sys

class Board:
    def __init__(self, num_pits=6, stones_per_pit=4, replay_nonempty=False, capture_empty=True):
        self.score = [0, 0]
        self.num_pits = num_pits
        self.stones_per_pit = stones_per_pit
        self.pits = [ [stones_per_pit] * num_pits,
                      [stones_per_pit] * num_pits ]
        self.next_player = 0
        self.game_over = False
        self.replay_nonempty = replay_nonempty
        self.capture_empty = capture_empty
        self.lineage = []

    def move(self, position, player=None):
        logging.debug(self)
        if player is None:
            player = self.next_player
        assert player in (0,1)
        assert position in range(self.num_pits)

        side = player
        self.next_player = player ^ 1
        stones = self.pits[side][position]
        assert stones > 0
        self.pits[side][position] = 0

        logging.debug("Player %d moves %d stones from position %d" % (player, stones, position))

        self.lineage.append({"player": player, "position": position, "stones": stones, "board": str(self)})

        while stones > 0:
            position += 1

            if position < self.num_pits:
                # regular stone drop
                self.pits[side][position] += 1
                stones -= 1

                if self.capture_empty and stones == 0 and side == player and self.pits[side][position] == 1:
                    logging.debug("Player %d captures %d stones at position %s" % (player, self.pits[side^1][-position-1], position))
                    self.score[player] += self.pits[side ^ 1][-position-1]
                    self.pits[side ^ 1][-position-1] = 0
                    break

            elif position == self.num_pits and side == player:
                # into our mancala
                self.score[player] += 1
                stones -= 1
                if stones == 0:
                    self.next_player = player
                    logging.debug("Player %d goes again" % player)
                    break
                else:
                    side ^= 1
                    position = -1
            elif position == self.num_pits:
                side ^= 1
                position = -1

        for side in (0, 1):
            if sum(self.pits[side]) == 0:
                self.score[side] += sum(self.pits[side ^ 1])
                self.pits[side ^ 1] = [0] * self.num_pits
                self.game_over = True
        self._sanity_check()

    def show_history(self):
        for play in self.lineage:
            print "Player %(player)s moved %(stones)s stones from position %(position)s" % play

    def _sanity_check(self):
        assert sum(self.score) + sum(self.pits[0]) + sum(self.pits[1]) == self.num_pits * self.stones_per_pit * 2, "Board %s failed sanity check" % str(self)

    def __str__(self):
        return "P0: %s=%d P1: %s=%d NEXT: %d" % (self.pits[0], self.score[0], self.pits[1], self.score[1], self.next_player)
 
    def valid_moves(self):
        return filter(lambda x: self.pits[self.next_player][x] > 0, range(self.num_pits))
        

def random_game(board, num_moves=1):
    # what are the legal moves?
    while num_moves > 0 and not board.game_over:
        valid_moves = board.valid_moves()
        position = random.choice(valid_moves)
        board.move(position)
        num_moves -= 1
    return board

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    human_player = 0
    computer_player = human_player ^ 1
    simulations = 10000
    board = Board()
    while not board.game_over:
        if board.next_player == human_player:
            print board
            try:
                your_move = int(input("Your move: "))
            except KeyboardInterrupt:
                sys.exit()
            except ValueError:
                pass
            board.move(your_move)
        else:
            print board
            most_wins = -1
            best_move = 0
            for potential_move in board.valid_moves():
                wins = 0
                for sim in range(simulations):
                    attempt = deepcopy(board)
                    attempt.move(potential_move)
                    random_game(attempt, num_moves=10)
                    logging.debug("test game: %s" % attempt)
                    if attempt.score[computer_player] > attempt.score[human_player]:
                        wins += 1
                if wins > most_wins:
                    best_move = potential_move
                    most_wins = wins
            print "Computer moves from position %s for win pct = %s%%" % (best_move, wins*100/simulations)
            board.move(best_move)

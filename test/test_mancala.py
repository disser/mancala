import pytest
import mancala

def test_board():
    b = mancala.Board()
    assert b.score == [0, 0]
    assert len(b.pits) == 2
    assert len(b.pits[0]) == 6
    assert len(b.pits[1]) == 6

def test_move_0():
    b = mancala.Board()
    bp, again = mancala.move(b, 0, 0)
    assert again == False
    assert bp.pits == [[0, 5, 5, 5, 5, 4], [4, 4, 4, 4, 4, 4]]
    assert bp.score == [0, 0]

def test_move_1():
    b = mancala.Board()
    bp, again = mancala.move(b, 0, 1)
    assert again == False
    assert bp.pits == [[4, 0, 5, 5, 5, 5], [4, 4, 4, 4, 4, 4]]
    assert bp.score == [0, 0]

def test_move_2():
    b = mancala.Board()
    bp, again = mancala.move(b, 0, 2)
    assert again == True
    assert bp.pits == [[4, 4, 0, 5, 5, 5], [4, 4, 4, 4, 4, 4]]
    assert bp.score == [1, 0]

def test_move_3():
    b = mancala.Board()
    bp, again = mancala.move(b, 0, 3)
    assert again == False
    assert bp.pits == [[4, 4, 4, 0, 5, 5], [5, 4, 4, 4, 4, 4]]
    assert bp.score == [1, 0]

def test_strategy():
    b = mancala.Board()
    s = mancala.GreedyStrategy(0)
    pos, bp = s.best_play(b)
    assert pos == 2
    assert bp.pits == [ [4, 4, 0, 0, 6, 6],
                        [5, 5, 4, 4, 4, 4]]
    assert bp.score == [2, 0]


def test_game_greedy_vs_random():
    g = mancala.Game([mancala.GreedyStrategy(0), mancala.RandomStrategy(1)])
    g.play()
    assert sum(g.board.pits[0]) + sum(g.board.pits[1]) == 0
    assert sum(g.board.score) == 12*4

def test_game_greedy_vs_greedy():
    g = mancala.Game([mancala.GreedyStrategy(0), mancala.GreedyStrategy(1)])
    g.play()
    assert sum(g.board.pits[0]) + sum(g.board.pits[1]) == 0
    assert sum(g.board.score) == 12*4

def test_game_greedy_vs_greedier():
    g = mancala.Game([mancala.GreedyStrategy(0), mancala.GreedierStrategy(1)])
    g.play()
    assert sum(g.board.pits[0]) + sum(g.board.pits[1]) == 0
    assert sum(g.board.score) == 12*4


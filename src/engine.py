"""
Setup engine and tell it what colour and difficulty
Easy, Medium, Hard
Easy = random move
Medium = depth 2
Hard = depth 3/4/5/6 whatever can get
"""
import math

piece_values = {
    'P': 10,
    'N': 30,
    'B': 30,
    'R': 50,
    'Q': 90,
    'K': 1e8
}

from .types import Eval_Move
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.board import Board

class Engine:
    def __init__(engine, color: chr, difficulty: chr) -> None:
        engine.color = color
        engine.difficulty = difficulty

    def select_and_make_move(engine) -> bool:
        """
        Choose move based on difficulty and every move update board.eval
        """
        if engine.difficulty == 'E':
            pass
        elif engine.difficulty == 'M':
            pass
        else:
            pass
        return True

    def minmax(engine, alpha, beta, is_maximising, depth, board: 'Board') -> Eval_Move:
        # Terminating conditions
        best_move = None
        if depth == 0 or board.checkmate or board.stalemate:
            return (engine.evaluate_position(board), best_move)

        # Minmax logic
        if not is_maximising:
            curr_color = 'W' if engine.color == 'B' else 'B'
        else:
            curr_color = engine.color

        # Maximiser code
        if is_maximising:
            best_eval = -math.inf
            for move in board.get_side_moves(curr_color):
                curr_eval, _ = engine.minmax(alpha, beta, False, depth - 1, )

                if curr_eval > best_eval:
                    best_eval = curr_eval
                    best_move = move
                    alpha = best_eval

                if beta <= alpha:
                    break
            return (engine.evaluate_position(board), best_move)

        # Minimiser code
        else:
            best_move = math.inf
            for move in board.get_side_moves(curr_color):
                curr_eval, _ = engine.minmax(alpha, beta, True, depth - 1, board)

                if curr_eval < best_eval:
                    best_eval = curr_eval
                    best_move = move
                    beta = best_eval

                if beta <= alpha:
                    break
            return (engine.evaluate_position(board), best_move)

    def evaluate_position(engine, board: 'Board'):
        """
        difference = (W_mobility + W_value / 10) - (B_mobility + B_value / 10)
        """
        pass
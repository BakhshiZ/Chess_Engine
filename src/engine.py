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
import random
from .types import Color, Eval_Move, MoveCoordinate, PieceType
from typing import Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from src.board import Board

class Engine:
    def __init__(engine, color: chr, difficulty: chr) -> None:
        engine.color = color
        engine.difficulty = difficulty
        engine.transposition_table: dict[int, Tuple[int, int, MoveCoordinate]] = {}

    def select_and_make_move(engine, board: 'Board') -> bool:
        """
        Choose move based on difficulty and every move update board.eval
        """
        # Randomly makes a move
        if engine.difficulty == 'E':
            move = random.choice(board.get_side_moves(engine.color))
            board.make_move(move)
            board_eval = engine.evaluate_position(board)
            return (board_eval, move)


        # Makes move with depth = 2
        elif engine.difficulty == 'M':
            depth = 2
        # Makes move with max depth
        else:
            depth = 4
        
        board_eval, move = engine.minmax(
            alpha=-math.inf, 
            beta=math.inf, 
            is_maximising=True, 
            depth=depth, 
            board=board
        )
        board.make_move(move)

        return (board_eval, move)

    def minmax(engine, alpha, beta, is_maximising, depth, board: 'Board') -> Eval_Move:
        if board.hash in engine.transposition_table:
            best_eval, stored_depth, best_move = engine.transposition_table[board.hash]
            if stored_depth >= depth:
                return (best_eval, best_move)

        # Terminating conditions
        best_move = None
        end_state = board.checkmate_stalemate_checker()

        if depth == 0 or end_state is not None:
            return (engine.evaluate_position(board), None)

        # Minmax logic
        if not is_maximising:
            curr_color = 'W' if engine.color == 'B' else 'B'
        else:
            curr_color = engine.color

        def move_score(engine, move: MoveCoordinate) -> int:
            return engine.heuristic_move_score(move, board)
    
        ordered_moves = list(board.get_side_moves(curr_color))
        ordered_moves.sort(
            key=move_score,
            reverse=is_maximising # Minimiser wants lowest score first, maxi wants high
        )

        # Maximiser code
        if is_maximising:
            best_eval = -math.inf
            for move in board.get_side_moves(curr_color):
                board.make_move(move, True)
                curr_eval, _ = engine.minmax(alpha, beta, False, depth - 1, board)
                board.undo_move()

                if curr_eval > best_eval:
                    best_eval = curr_eval
                    best_move = move
                    alpha = best_eval

                if beta <= alpha:
                    break
            engine.transposition_table[board.hash] = (best_eval, depth, best_move)
            return (best_eval, best_move)

        # Minimiser code
        else:
            best_eval = math.inf
            for move in board.get_side_moves(curr_color):
                board.make_move(move, True)
                curr_eval, _ = engine.minmax(alpha, beta, True, depth - 1, board)
                board.undo_move()

                if curr_eval < best_eval:
                    best_eval = curr_eval
                    best_move = move
                    beta = best_eval

                if beta <= alpha:
                    break
        
            engine.transposition_table[board.hash] = (best_eval, depth, best_move)
            return (best_eval, best_move)

    def evaluate_position(engine, board: 'Board'):
        """
        difference = (W_mobility + W_value / 10) - (B_mobility + B_value / 10)
        """
        board_eval = 0.0
        for row in range(8):
            for col in range(8):
                coord = (row, col)
                square = board.get_piece_info(coord)
                piece_type = square.PieceType
                piece_color = square.Color
                
                if piece_type is None:
                    continue
                
                piece_value = piece_values[piece_type]
                
                if piece_color == engine.color:
                    board_eval += piece_value
                else:
                    board_eval -= piece_value

        self_mobility = board.get_side_mobility(engine.color)
        enemy_color = 'W' if engine.color == 'B' else 'B'
        enemy_mobility = board.get_side_mobility(enemy_color)

        board_eval += (self_mobility - enemy_mobility)
        board_eval /= 10

        return board_eval
    
    def mvv_lva_score(engine, attacker_piece: PieceType, captured_piece: PieceType) -> int:
        """
        Returns Most Valuable Victim Least Valuable Attacker score (captured - attacker). 
        Better captures yield higher scores
        """
        attacker_val = piece_values.get(attacker_piece, 0)
        captured_val = piece_values.get(captured_piece, 1)

        # Default formula for move ordering
        return 10 * captured_val - attacker_val
    
    def heuristic_move_score(engine, move: MoveCoordinate, board: 'Board') -> int:
        """
        Function used to give moves a heuristic score to order them, valuing checks, captures
        and fight for center squares
        """
        enemy_color = 'W' if engine.color == 'B' else 'B'
        from_coord, to_coord = move
        score = 0

        attacker = board.get_piece_info(from_coord)
        target = board.get_piece_info(to_coord)

        """
        Simulate move, look for checks and attacks
        """
        # Checks
        board.make_move(move, is_simulation=True)

        if board.is_king_attacked(enemy_color):
            score += 100
        
        board.undo_move()

        # Captures (implementing MVV-LVA)
        if target.PieceType is not None:
            score += engine.mvv_lva_score(attacker.PieceType, target.PieceType)
        
        # Attacking center
        if to_coord in {(3, 3), (3, 4), (4, 3), (4, 4)}:
            score += 5

        return score
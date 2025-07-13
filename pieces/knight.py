from .shared import *
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.board import Board

def get_knight_moves(board: 'Board', piece_coordinate: Coordinate) -> Tuple[MoveCoordinate, ...]:
    legal_moves = []
    directions = [
        (1, -2), (-1, -2), # LLU, LLD
        (-2, -1), (-2, 1), # DDL, DDR
        (2, -1), (2, 1), # UUL, UUR
        (1, 2), (-1, 2) # RRU, RRD
    ]
    square = board.get_piece_info(piece_coordinate)
    old_coord = piece_coordinate

    for d_r, d_c in directions:
        new_row = square.Row + d_r
        new_col = square.Col + d_c
        
        # Making sure knights stay in bound
        if not (MIN_INDEX <= new_row <= MAX_INDEX and MIN_INDEX <= new_col <= MAX_INDEX):
            continue
        
        new_coord = (new_row, new_col)
        target_square = board.get_piece_info(new_coord)

        if target_square.PieceType is None or target_square.Color != square.Color:
            legal_moves.append((old_coord, new_coord))
    
    return legal_moves
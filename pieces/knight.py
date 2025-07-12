from src.types import Coordinate, MoveCoordinate
from src.constants import MIN_INDEX, MAX_INDEX
from typing import TYPE_CHECKING, Tuple
if TYPE_CHECKING:
    from src.board import Board
"""
DDL, DDR, LLU, LLD, RRU, RRD, UUL, UUR
"""

def get_knight_moves(board: 'Board', piece_coordinate: Coordinate) -> Tuple[MoveCoordinate, ...]:
    directions = [
        (-2, -1), (-2, 1), (1, -2), (-1, -2),
        (2, 1), (2, -1), (-1, -2), (-1, 2)
    ]
    square = board.get_piece_info(piece_coordinate)

    for d_r, d_c in directions:
        new_row = square.Row + d_r
        new_col = square.Col + d_c
        
        # Making sure knights stay in bound
        if not (MIN_INDEX <= new_row <= MAX_INDEX and MIN_INDEX <= new_col <= MAX_INDEX):
            continue
        
        
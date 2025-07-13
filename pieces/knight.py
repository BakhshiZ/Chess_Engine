from .shared import *
from .stepping_moves import stepping_moves
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.board import Board

def get_knight_moves(board: 'Board', piece_coord: Coordinate) -> Tuple[MoveCoordinate, ...]:
    directions = [
        (1, -2), (-1, -2), # LLU, LLD
        (-2, -1), (-2, 1), # DDL, DDR
        (2, -1), (2, 1), # UUL, UUR
        (1, 2), (-1, 2) # RRU, RRD
    ]

    return tuple(stepping_moves(board, piece_coord, directions))
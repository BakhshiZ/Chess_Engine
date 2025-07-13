from .shared import *
from typing import TYPE_CHECKING
from .sliding_moves import sliding_moves

if TYPE_CHECKING:
    from src.board import Board

def get_rook_moves(board: 'Board', piece_coord: Coordinate) -> Tuple[MoveCoordinate, ...]:
    directions = [
        (0, -1), (0, 1), # L, R
        (1, 0), (-1, 0) # U, D
    ]
    
    return tuple(sliding_moves(board, piece_coord, directions))
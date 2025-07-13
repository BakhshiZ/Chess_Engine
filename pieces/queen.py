from .shared import *
from .sliding_moves import sliding_moves
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.board import Board

def get_queen_moves(board: 'Board', piece_coordinate: Coordinate) -> Tuple[MoveCoordinate, ...]:
    directions = [
        (1, 0), (0, -1), (0, 1), (-1, 0), # U, L, R, D
        (1, -1), (1, 1), (-1, -1), (-1, 1) # UL, UR, DL, DR
    ]

    return tuple(sliding_moves(board, piece_coordinate, directions))
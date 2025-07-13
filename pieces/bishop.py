from .shared import *
from typing import TYPE_CHECKING
from .sliding_moves import bishop_rook_moves

if TYPE_CHECKING:
    from src.board import Board

def get_bishop_moves(board: 'Board', piece_coordinate: Coordinate) -> Tuple[MoveCoordinate, ...]:
    directions = [
        (1, -1), (1, 1), # UL, UR
        (-1, -1), (-1, 1) # DL, DR
    ]

    return tuple(bishop_rook_moves(board, piece_coordinate, directions))
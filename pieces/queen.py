from .shared import *
from .sliding_moves import sliding_moves
from typing import TYPE_CHECKING
from src.constants import ALL_DIRECTIONS

if TYPE_CHECKING:
    from src.board import Board

def get_queen_moves(board: 'Board', piece_coord: Coordinate) -> Tuple[MoveCoordinate, ...]:
    return tuple(sliding_moves(board, piece_coord, ALL_DIRECTIONS))
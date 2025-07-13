from .shared import *
from src.constants import ROOK_DIRECTIONS
from typing import TYPE_CHECKING
from .sliding_moves import sliding_moves

if TYPE_CHECKING:
    from src.board import Board

def get_rook_moves(board: 'Board', piece_coord: Coordinate) -> Tuple[MoveCoordinate, ...]:
    return tuple(sliding_moves(board, piece_coord, ROOK_DIRECTIONS))
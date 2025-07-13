from .shared import *
from typing import TYPE_CHECKING
from .stepping_moves import stepping_moves
from src.constants import ALL_DIRECTIONS

if TYPE_CHECKING:
    from src.board import Board

def get_king_moves(board: 'Board', piece_coord: Coordinate) -> Tuple[MoveCoordinate, ...]:
    return tuple(stepping_moves(board, piece_coord, ALL_DIRECTIONS))
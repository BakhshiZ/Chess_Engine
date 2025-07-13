from .shared import *
from .stepping_moves import stepping_moves
from typing import TYPE_CHECKING
from src.constants import KNIGHT_DIRECTIONS

if TYPE_CHECKING:
    from src.board import Board

def get_knight_moves(board: 'Board', piece_coord: Coordinate) -> Tuple[MoveCoordinate, ...]:
    return tuple(stepping_moves(board, piece_coord, KNIGHT_DIRECTIONS))
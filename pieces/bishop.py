from .shared import *
from src.constants import BISHOP_DIRECTIONS
from .sliding_moves import sliding_moves
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.board import Board

def get_bishop_moves(board: 'Board', piece_coord: Coordinate) -> Tuple[MoveCoordinate, ...]:
    return tuple(sliding_moves(board, piece_coord, BISHOP_DIRECTIONS))
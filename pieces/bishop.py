from .shared import *
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .shared import Board

def get_bishop_moves(board: 'Board', piece_coordinate: Coordinate) -> Tuple[MoveCoordinate, ...]:
    pass
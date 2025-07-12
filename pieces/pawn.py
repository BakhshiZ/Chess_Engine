from src.types import Coordinate, MoveCoordinate
from typing import Tuple, TYPE_CHECKING
if TYPE_CHECKING:
    from src.board import Board

def get_pawn_moves(board: 'Board', piece_coordinate: MoveCoordinate) -> Tuple[Coordinate]:
    # Checking squares straight ahead
    piece_info = board.get_piece_info(piece_coordinate)
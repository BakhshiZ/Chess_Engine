from .shared import *
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.board import Board

def stepping_moves(
        board: 'Board', 
        piece_coord: Coordinate, 
        directions: List[Tuple[int, int]]
) -> List[MoveCoordinate]:
    """
    Shared moves for king and knight to implement DRY (don't repeat yourself) principle
    """
    legal_moves = []
    square = board.get_piece_info(piece_coord)

    for d_r, d_c in directions:
        new_row = square.Row + d_r
        new_col = square.Col + d_c

        if not (0 <= new_row <= 7 and 0 <= new_col <= 7):
            continue

        new_coord = (new_row, new_col)
        target_square = board.get_piece_info(new_coord)

        if target_square.PieceType is None or target_square.Color != square.Color:
            legal_moves.append((piece_coord, new_coord))

    return legal_moves

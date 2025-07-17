from .shared import *
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.board import Board

def stepping_moves(
        board: 'Board', 
        piece_coord: Coordinate, 
        directions: List[Tuple[int, int]]
) -> Tuple[MoveCoordinate, ...]:
    """
    Shared moves for king and knight to implement DRY (don't repeat yourself) principle
    """
    legal_moves = []
    row, col = piece_coord
    square = board.board[row][col]

    for d_r, d_c in directions:
        new_row = row + d_r
        new_col = col + d_c

        if not (0 <= new_row <= 7 and 0 <= new_col <= 7):
            continue

        new_coord = (new_row, new_col)
        target_square = board.board[new_row][new_col]

        if target_square is None or target_square[0] != square[0]:
            legal_moves.append((piece_coord, new_coord))

    return tuple(legal_moves)

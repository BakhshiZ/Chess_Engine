from .shared import *
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from src.board import Board

def sliding_moves(
        board: 'Board',
        piece_coord: Coordinate,
        directions: List[Tuple[int, int]]
) -> List[MoveCoordinate]:
    """
    Shared moves for bishop, rook, queen to implement DRY principle
    """
    legal_moves = []
    square = board.get_piece_info(piece_coord)
    old_coord = piece_coord

    for d_r, d_c in directions:
        new_row = square.Row + d_r
        new_col = square.Col + d_c

        # Making sure in bounds
        while 0 <= new_row <= 7 and 0 <= new_col <= 7:
            new_coord = (new_row, new_col)
            target_square = board.get_piece_info(new_coord)

            """
            If square is empty, add and move onto next
            If square is enemy piece, capture and stop looking
            If square is friendly piece, stop looking
            """
            if target_square.PieceType is None: # Empty square
                legal_moves.append((old_coord, new_coord))

            elif target_square.Color != square.Color: # Enemy piece
                legal_moves.append((old_coord, new_coord))
                break

            else: # Friendly piece
                break  

            new_row += d_r
            new_col += d_c

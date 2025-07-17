from .shared import *
from src.constants import PAWN_CAPTURE_DIRECTIONS
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.board import Board

def get_pawn_moves(board: 'Board', piece_coord: Coordinate) -> Tuple[MoveCoordinate, ...]:
    legal_moves = []
    square = board.get_piece_info(piece_coord)
    start_row = 6 if square.Color == 'W' else 1
    direction = -1 if square.Color == 'W' else 1
    
    # Checking squares straight ahead
    old_coord = (square.Row, square.Col)
    new_row = square.Row + direction

    # Checking if square immediately ahead is clear
    if board.board[new_row][square.Col] is None and MIN_INDEX <= new_row <= MAX_INDEX:
        new_coord = (new_row, square.Col)
        legal_moves.append((old_coord, new_coord))
    
        # If pawn is on starting square, it can move forward twice
        if square.Row == start_row:
            two_ahead_row = square.Row + 2 * direction
            if MIN_INDEX <= two_ahead_row <= MAX_INDEX:
                if board.board[two_ahead_row][square.Col] is None:
                    new_coord = (two_ahead_row, square.Col)
                    legal_moves.append((old_coord, new_coord))

    # Diagonal squares for captures
    PAWN_CAPTURE_DIRECTIONS

    for d_r, d_c in PAWN_CAPTURE_DIRECTIONS[square.Color]:
        new_row = square.Row + d_r
        new_col = square.Col + d_c
        
        # Making sure pawns stay in bounds
        if not (MIN_INDEX <= new_col <= MAX_INDEX and MIN_INDEX <= new_row <= MAX_INDEX):
            continue
        
        new_coord = (new_row, new_col)
        target_square = board.get_piece_info((new_row, new_col))
        
        # If diagonal is an enemy piece then it is possible to go to
        if target_square.PieceType is not None and target_square.Color != square.Color:
            legal_moves.append((old_coord, new_coord))

    # Checking for en croissant
    last_move = board.move_history[-1]
    moved_old_coord, moved_new_coord, moved_piece, _, _ = last_move
    moved_old_row, _ = moved_old_coord
    moved_new_row, moved_new_col = moved_new_coord
    enemy_color = 'W' if square.Color == 'B' else 'B'
    if (moved_piece == f"{enemy_color}_P" and abs(moved_new_row - moved_old_row) == 2) and (
        moved_new_row == square.Row):
        en_croissant_col = moved_new_col
        en_croissant_row = moved_new_row + direction
        en_croissant_coord = (en_croissant_row, en_croissant_col)
        legal_moves.append((old_coord, en_croissant_coord))

    return tuple(legal_moves)
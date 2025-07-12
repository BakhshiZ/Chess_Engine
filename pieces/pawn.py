from src.types import Coordinate, MoveCoordinate
from typing import Tuple, TYPE_CHECKING
if TYPE_CHECKING:
    from src.board import Board

MIN_INDEX = 0
MAX_INDEX = 7

def get_pawn_moves(board: 'Board', piece_coordinate: MoveCoordinate) -> Tuple[MoveCoordinate, ...]:
    legal_moves = []
    square = board.get_piece_info(piece_coordinate)
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
    directions = {
        'B': [(1, -1), (1, 1)],
        'W': [(-1, -1), (-1, 1)]
    }

    for d_r, d_c in directions[square.Color]:
        new_row = square.Row + d_r
        new_col = square.Col + d_c
        # Making sure pawns stay in bounds
        if MIN_INDEX <= new_col <= MAX_INDEX and MIN_INDEX <= new_row <= MAX_INDEX:
            new_coord = (new_row, new_col)
            target_square = board.get_piece_info((new_row, new_col))
            # If diagonal is an enemy piece then it is possible to go to
            if target_square.PieceType is not None and target_square.Color != square.Color:
                legal_moves.append((old_coord, new_coord))
    
    return tuple(legal_moves)
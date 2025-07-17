from .shared import *
from typing import TYPE_CHECKING
from .stepping_moves import stepping_moves
from src.constants import ALL_DIRECTIONS

if TYPE_CHECKING:
    from src.board import Board

def get_king_moves(board: 'Board', piece_coord: Coordinate) -> Tuple[MoveCoordinate, ...]:
    legal_moves = list(stepping_moves(board, piece_coord, ALL_DIRECTIONS))

    row, col = piece_coord
    piece = board.get_piece_info(piece_coord)

    """
    King not in check
    Squares between king and rook empty
    Enemy pieces not looking at square
    """
    if piece.Color == 'W' and not board.white_king_moved:
        # Queenside
        if not board.white_rook_moved[0] and \
         board.get_piece_info((7, 1)).PieceType is None and \
         board.get_piece_info((7, 2)).PieceType is None and \
         board.get_piece_info((7, 3)).PieceType is None and \
         not board.is_king_attacked('B') and \
         not board.square_under_attack((7, 3), 'B') and \
         not board.square_under_attack((7, 2), 'B'):
            legal_moves.append(((7, 4), (7, 2)))

        # Kingside
        if not board.white_rook_moved[1] and \
         board.get_piece_info((7, 5)).PieceType is None and \
         board.get_piece_info((7, 6)).PieceType is None and \
         not board.is_king_attacked('B') and \
         not board.square_under_attack((7, 5), 'B') and \
         not board.square_under_attack((7, 6), 'B'):
            legal_moves.append(((7, 4), (7, 6)))

    elif piece.Color == 'B' and not board.black_king_moved:
        # Queenside
        if not board.black_rook_moved[0] and \
         board.board[0][1] == None and \
         board.board[0][2] == None and \
         board.board[0][3] == None and \
         not board.is_king_attacked('W') and \
         not board.square_under_attack((0, 2), 'W') and \
         not board.square_under_attack((0, 3), 'W'):
            legal_moves.append(((0, 4), (0, 2)))
        
        # Kingside
        if not board.black_rook_moved[1] and \
         board.get_piece_info((0, 5)).PieceType is None and \
         board.get_piece_info((0, 6)).PieceType is None and \
         not board.is_king_attacked('W') and \
         not board.square_under_attack((0, 5), 'W') and \
         not board.square_under_attack((0, 6), 'W'):
            legal_moves.append(((0, 4), (0, 6)))

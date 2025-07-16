from src.zobrist import zobrist_table
from pieces.stepping_moves import stepping_moves
from pieces.sliding_moves import sliding_moves
from src.types import *
from src.constants import *
from pieces import *
from typing import List, Tuple

class Board:
    def __init__(board) -> None:
        board.setup_board()

    def setup_board(board) -> None:
        board.board: List[List[Piece]] = [
            ["B_R", "B_N", "B_B", "B_Q", "B_K", "B_B", "B_N", "B_R"],
            ["B_P"] * 8,
            [None] * 8,
            [None] * 8,
            [None] * 8,
            [None] * 8,
            ["W_P"] * 8,
            ["W_R", "W_N", "W_B", "W_Q", "W_K", "W_B", "W_N", "W_R"]
            ]

        board.zobrist_table = zobrist_table
        board.curr_move = 'W'
        board.move_history: List[Moves] = []
        
        # Per side caching for engine
        board.B_move_cache: dict[Coordinate, Tuple[MoveCoordinate, ...]] = {}
        board.W_move_cache: dict[Coordinate, Tuple[MoveCoordinate, ...]] = {}
        
        # Keeping track of king positions in dictionary for o(1) lookup time
        board.king_pos = {
            'W': (7, 4), # Default start is e1
            'B': (0, 4) # Default start is e7
        }

        # Castling flags
        board.white_king_moved = False
        board.black_king_moved = False
        board.white_rook_moved = [False, False] # Queenside, Kingside
        board.black_rook_moved = [False, False] # Queenside, Kingside

        # Tuple to pass into move history
        board.flags = (board.white_king_moved, board.black_king_moved, board.white_rook_moved, board.black_rook_moved)

        # Terminating flags
        board.checkmate = False
        board.stalemate = False

    def make_move(board, move: MoveCoordinate, is_simulation: bool = False) -> bool:
        """
        Apply a move to the board.
        If is_simulation is True, skip validation and flag updates, but still update move_history for undoing.
        """

        # If move is being simulated, no need to validate
        if not is_simulation:
            if not board.can_make_move(move):
                return False

        old_coord, new_coord = move
        old_target = board.get_piece_info(old_coord)
        new_target = board.get_piece_info(new_coord)

        old_row, old_col = old_target.Row, old_target.Col
        new_row, new_col = new_target.Row, new_target.Col

        moved_piece = old_target.Color + '_' + old_target.PieceType
        captured_piece = (
            new_target.Color + '_' + new_target.PieceType
            if new_target.PieceType is not None
            else None
        )

        # Move piece
        board.board[new_row][new_col] = moved_piece
        board.board[old_row][old_col] = None

        # Use dummy flags if simulating (won't affect state)
        if is_simulation:
            dummy_flags: Flags = (
                board.white_king_moved,
                board.black_king_moved,
                list(board.white_rook_moved),
                list(board.black_rook_moved)
            )

            move_entry: Moves = (old_coord, new_coord, moved_piece, captured_piece, dummy_flags)
        else:
            # Update flags and add entry for move history
            updated_flags: Flags = board.update_flags_after_move(move)
            move_entry: Moves = (old_coord, new_coord, moved_piece, captured_piece, updated_flags)

        # If moved piece is a king, updated position in dictionary
        if old_target.PieceType == 'K':
            board.king_pos[old_target.Color] = new_coord

        board.curr_move = 'B' if board.curr_move == 'W' else 'W'
        board.move_history.append(move_entry)
        if not is_simulation:
            board.move_cache.clear()
        return True

    def undo_move(board) -> None:
        """
        Function to undo last move (for simulation purposes)
        """
        if not board.move_history:
            return
        moved_piece_original_coord, captured_piece_original_coord, moved_piece, captured_piece, prev_flags = board.move_history.pop()
        moved_piece_row, moved_piece_col = moved_piece_original_coord
        captured_piece_row, captured_piece_col = captured_piece_original_coord        

        board.board[moved_piece_row][moved_piece_col] = moved_piece
        board.board[captured_piece_row][captured_piece_col] = captured_piece

        # Moved_piece in form W_K or B_K, so [0] = color and [2] = type
        moved_color = moved_piece[0]
        moved_type = moved_piece[2]
        if moved_type == 'K':
            board.king_pos[moved_color] = moved_piece_original_coord

        board.white_king_moved, board.black_king_moved, \
            board.white_rook_moved, board.black_rook_moved = prev_flags
        board.curr_move = 'B' if board.curr_move == 'W' else 'W'

    def can_make_move(board, move: MoveCoordinate) -> bool:
        """
        Check if move is a valid move for pieces
        Call check_checker
        """
        old_coord, _ = move
        is_legal, is_safe = False, False
        legal_moves = set(board.get_piece_moves(old_coord))
        is_legal = move in legal_moves

        if not board.check_checker(move):
            is_safe = True
        return is_legal and is_safe

    def check_checker(board, move: MoveCoordinate) -> bool:
        """
        Simulate move and check if the king is in view of enemy piece
        """
        # Move history -> Tuple[OldCoord, NewCoord, MovedPiece, CapturedPiece, Flags]
        board.make_move(move, True)
        return_val = board.is_king_attacked(board.curr_move)
        board.undo_move()

        return return_val

    def get_piece_moves(board, coordinate: Coordinate) -> Tuple[MoveCoordinate, ...]:
        """
        Pass a coordinate and check all possible moves for that piece by calling the
        appropriate piece function
        """
        piece = board.get_piece_info(coordinate)
        piece_color = piece.Color
        piece_type = piece.PieceType
        move_cache = getattr(board, f"{piece_color}_move_cache")

        if coordinate in move_cache:
            return move_cache[coordinate]

        if piece_type == 'P':
            moves = get_pawn_moves(board, coordinate)
        elif piece_type == 'B':
            moves = get_bishop_moves(board, coordinate)
        elif piece_type == 'K':
            moves = get_king_moves(board, coordinate)
        elif piece_type == 'N':
            moves = get_knight_moves(board, coordinate)
        elif piece_type == 'Q':
            moves = get_queen_moves(board, coordinate)
        else:
            moves = get_rook_moves(board, coordinate)
        
        move_cache[coordinate] = moves
        return moves

    def get_moves_efficient(board, coordinate: Coordinate) -> Tuple[MoveCoordinate, ...]:
        piece = board.get_piece_info(coordinate)

        if piece.PieceType == 'P':
            return get_pawn_moves(board, coordinate)
        elif piece.PieceType == 'B':
            return get_bishop_moves(board, coordinate)
        elif piece.PieceType == 'N':
            return get_knight_moves(board, coordinate)
        elif piece.PieceType == 'R':
            return get_rook_moves(board, coordinate)
        elif piece.PieceType == 'Q':
            return get_queen_moves(board, coordinate)
        else:
            return get_king_moves(board, coordinate)

    def get_side_moves(board, color: Color) -> Tuple[MoveCoordinate, ...]:
        side_moves = []
        for row in range(8):
            for col in range(8):
                coord = (row, col)
                square = board.get_piece_info(coord)
                if square.PieceType is None or square.Color != color:
                    continue
                side_moves.extend(board.get_piece_moves(coord))
        
        return tuple(side_moves)

    def checkmate_stalemate_checker(board) -> bool:
        """
        Check a side has no legal moves, then if stalemate of checkmate
        """
        has_legal_moves = True

        for row in range(8):
            for col in range(8):
                coord = (row, col)
                piece = board.get_piece_info(coord)
                if piece.PieceType is None or piece.Color != board.curr_move:
                    continue
                
                # Checking if piece moves are legal
                for move in board.get_piece_moves(coord):
                    if board.can_make_move(move):
                        has_legal_moves = True
                        break

                if has_legal_moves:
                    break
        
        if has_legal_moves:
            board.checkmate = False
            board.stalemate = False
            return True
        
        # If no legal moves then check if in check. If yes then checkmate else stalemate
        enemy = 'W' if board.curr_move == 'B' else 'W'
        if board.is_king_attacked(enemy):
            board.checkmate = True
            board.stalemate = False
        else:
            board.checkmate = False
            board.stalemate = True

    # Helper functions
    def get_piece_info(board, piece_coord: Coordinate) -> PieceInfo:
        row, col = piece_coord
        if board.board[row][col] is None:
            return PieceInfo(Row=row, Col=col, Color=None, PieceType=None)

        color = board.board[row][col][0]
        piece_type = board.board[row][col][2]
        return PieceInfo(Row=row, Col=col, Color=color, PieceType=piece_type)
        
        """
        info = board.get_piece_info((6, 4))
        print(info.color, info.type)
        """

    def print_board(board) -> None:
        letters = "     a     b     c     d     e     f     g     h"
        print(letters)
        for row in range(ROW_COUNT):
            print(8 - row, end=" | ")
            for col in range(COL_COUNT):
                coord = (row, col)
                target = board.get_piece_info(coord)
                if target.PieceType is None:
                    print("   ", end=" | ")
                else:
                    print(f"{target.Color}_{target.PieceType}", end=" | ")
            print(8 - row)
            print('---------------------------------------------------')
        print(letters)

    def castling_mover(board, move: MoveCoordinate) -> None:
        old_coord, _ = move
        old_target = board.get_piece_info(old_coord)

        if old_target.Row == 7:
            if old_target.Col == 4:
                board.board[7][6] = "W_K"
                board.board[7][5] = "W_R"
                board.board[7][4] = None
                board.board[7][7] = None
            else:
                board.board[7][2] = "W_K"
                board.board[7][3] = "W_R"
                board.board[7][4] = None
                board.board[7][0] = None
        else:
            if old_target.Col == 4:
                board.board[0][6] = "B_K"
                board.board[0][5] = "B_R"
                board.board[0][4] = None
                board.board[0][7] = None
            else:
                board.board[0][2] = "B_K"
                board.board[0][3] = "B_R"
                board.board[0][4] = None
                board.board[0][0] = None

    def tuple_to_algebraic(tile: Coordinate) -> str:
        """
        Function to convert from form (7, 4) to e1
        """
        row, col = tile
        file = chr(col + ord('a')) # 0 - 7 = a (a + 0) - h (a + 7)
        rank = str(8 - row)
        return file + rank # a + 4 = a4
    
    def algebraic_to_tuple(tile: Coordinate) -> Tuple[int, int]:
        """
        Function to convert from form e1 to (7, 4)
        """
        file = tile[0].lower()
        rank = int(tile[1])
        col = ord(file) - ord('a') # 0 - 7 = a (97 - 97) - h (104 - 97)
        row = 8 - rank
        return (row, col)
    
    def update_flags_after_move(board, move: MoveCoordinate) -> Flags:
        """
        Update all flags after every move
        """
        _, new_coord = move
        piece = board.get_piece_info(new_coord)

        if piece.PieceType == 'K':
            if piece.Color == 'W':
                board.white_king_moved = True
            else:
                board.black_king_moved = True

        elif piece.PieceType == 'R':
            rook_index = 0 if piece.Col == 0 else 1
            if piece.Color == 'W':
                board.white_rook_moved[rook_index] = True
            else:
                board.black_rook_moved[rook_index] = True

        return (board.white_king_moved, board.black_king_moved, 
        board.white_rook_moved, board.black_rook_moved)

    
    def is_king_attacked(board, enemy_color: chr) -> bool:
        """
        function to check if king under attack
        * Check in L-Shape for knights
        * Check diagonals for pawn / bishop / queen
        * Check rook moves for queen / rook

        * Stepping moves -> Knights
        * Sliding moves -> Rook, Queen, Bishop
        """
        king_color = 'W' if enemy_color == 'B' else 'B'
        king_coord = board.king_pos[king_color]
        king_row, king_col = king_coord

        # Checking L-shapes for knights
        for _, target_coord in stepping_moves(board, king_coord, KNIGHT_DIRECTIONS):
            target_row, target_col = target_coord
            piece = board.get_piece_info(target_coord)

            if piece.PieceType is None:
                continue
            if piece.Color == enemy_color and piece.PieceType == 'N':
                return True
        
        # Checking for bishops and queen on diagonal
        for _, target_coord in sliding_moves(board, king_coord, BISHOP_DIRECTIONS):
            target_row, target_col = target_coord
            piece = board.get_piece_info((target_row, target_col))
            if piece.PieceType is None:
                            continue
            if piece.Color == enemy_color and piece.PieceType in ('B', 'Q'):
                return True

        # Checking for rooks and queens on straights
        for _, target_coord in sliding_moves(board, king_coord, ROOK_DIRECTIONS):
            target_row, target_col = target_coord
            piece = board.get_piece_info((target_row, target_col))
            if piece.PieceType is None:
                            continue
            if piece.Color == enemy_color and piece.PieceType in ('R', 'Q'):
                return True

        for directions in PAWN_CAPTURE_DIRECTIONS[king_color]:
            d_r, d_c = directions
            target_row = king_row + d_r
            target_col = king_col + d_c

            if not (0 <= target_row <= 7 and 0 <= target_col <= 7):
                continue

            piece = board.get_piece_info((target_row, target_col))

            if piece.PieceType is None:
                continue
            if piece.Color == enemy_color and piece.PieceType == 'P':
                return True

        return False
    
    def get_side_mobility(board, color: Color) -> int:
        mobility = 0
        for row in range(8):
            for col in range(8):
                coord = (row, col)
                square = board.get_piece_info(coord)
                
                if square.PieceType is None:
                    continue

                if square.Color == color:
                    mobility += len(board.get_moves_efficient(coord))
        
        return mobility

if __name__ == "__main__":
    board = Board()
    if not board.make_move(((6, 4), (5, 4))):
        print("ILLEGAL")
    else:
        board.print_board()
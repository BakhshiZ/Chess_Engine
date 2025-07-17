from src.zobrist import compute_zobrist_hash, zobrist_table
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
        board.hash = compute_zobrist_hash(board)
        board.curr_move = 'W'
        board.move_history: List[Moves] = []
        
        # Per side caching for engine
        board.cache: dict[str, Tuple[Coordinate, Tuple[MoveCoordinate]]] = {
            # 'B': dict[Coordinate, Tuple[MoveCoordinate, ...]] = {},
            'B': {},
            'W': {}
        }

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

    def make_move(board, move: MoveCoordinate, is_simulation: bool = False, promotion_piece: str = None) -> bool:
        """
        Apply a move to the board.
        If is_simulation is True, skip validation and flag updates, but still update move_history for undoing.
        promotion_piece: optional string ('Q', 'R', 'B', 'N') for user-specified promotion. Engine defaults to 'Q'.
        """

        if not is_simulation and not board.can_make_move(move):
            return False

        old_coord, new_coord = move
        old_row, old_col = old_coord
        new_row, new_col = new_coord

        old_square = board.board[old_row][old_col]
        new_square = board.board[new_row][new_col]

        moved_piece = old_square
        captured_piece = new_square

        is_en_passant = False
        promotion_final = None

        if captured_piece:
            captured_row = new_row
            captured_col = new_col

        # En passant capture
        if moved_piece[2] == 'P' and captured_piece is None:
            if abs(new_row - old_row) == 1 and abs(new_col - old_col) == 1:
                captured_row = old_row
                captured_col = new_col
                en_passant_piece = board.board[captured_row][captured_col]
                if en_passant_piece[2] == 'P' and en_passant_piece[0] != moved_piece[0]:
                    is_en_passant = True
                    captured_piece = f"{en_passant_piece.Color}_P"
                    board.board[captured_row][captured_col] = None

        # Detect castling
        is_castling = moved_piece.endswith("_K") and abs(new_col - old_col) == 2
        if is_castling:
            board.castling_mover(move)

        # Handle promotion
        if moved_piece[2] == 'P' and (new_row == 0 or new_row == 7):
            selected = promotion_piece if promotion_piece in ('Q', 'R', 'B', 'N') else 'Q'
            promotion_final = moved_piece[0] + '_' + selected
            board.board[new_row][new_col] = promotion_final
        else:
            board.board[new_row][new_col] = moved_piece

        board.board[old_row][old_col] = None

        # Zobrist: remove moved piece from old square
        board.hash ^= board.zobrist_table[moved_piece][board.zobrist_index_finder(old_row, old_col)]

        # Zobrist: remove captured piece if any
        if captured_piece:
            board.hash ^= board.zobrist_table[captured_piece][board.zobrist_index_finder(captured_row, captured_col)]

        # Zobrist: add final piece to new square
        final_piece = promotion_final if promotion_final else moved_piece
        board.hash ^= board.zobrist_table[final_piece][board.zobrist_index_finder(new_row, new_col)]

        # Zobrist: toggle side to move
        board.hash ^= board.zobrist_table["BLACK_TO_MOVE"]

        # Update king position
        if old_target.PieceType == 'K':
            board.king_pos[old_target.Color] = new_coord

        # Set flags
        if is_simulation:
            flags = (
                board.white_king_moved,
                board.black_king_moved,
                list(board.white_rook_moved),
                list(board.black_rook_moved),
            )
        else:
            flags = board.update_flags_after_move(move)

        # Record move history
        move_entry: Moves = (
            old_coord, new_coord, moved_piece, captured_piece,
            flags, is_en_passant, promotion_final
        )
        board.move_history.append(move_entry)

        if not is_simulation:
            board.cache[board.curr_move].clear()

        board.curr_move = 'B' if board.curr_move == 'W' else 'W'
        return True


    def undo_move(board) -> None:
        if not board.move_history:
            return

        move_entry = board.move_history.pop()
        old_coord, new_coord, moved_piece, captured_piece, prev_flags, is_en_passant, promotion_piece = move_entry
        old_row, old_col = old_coord
        new_row, new_col = new_coord

        board.white_king_moved, board.black_king_moved, \
            board.white_rook_moved, board.black_rook_moved = prev_flags

        # If it was a promotion, revert to pawn
        if promotion_piece:
            board.board[old_row][old_col] = moved_piece  # e.g., 'W_P'
            board.board[new_row][new_col] = None

            # Zobrist: remove promoted piece from new square
            board.hash ^= board.zobrist_table[promotion_piece][board.zobrist_index_finder(new_row, new_col)]

            # Zobrist: add pawn back to old square
            board.hash ^= board.zobrist_table[moved_piece][board.zobrist_index_finder(old_row, old_col)]

        # Undo castling
        elif moved_piece.endswith('_K') and abs(new_col - old_col) == 2:
            board.undo_castling((old_coord, new_coord))

        # Normal undo
        else:
            board.board[old_row][old_col] = moved_piece
            board.board[new_row][new_col] = None

            # Zobrist: remove moved piece from new square
            board.hash ^= board.zobrist_table[moved_piece][board.zobrist_index_finder(new_row, new_col)]

            # Zobrist: add it back to old square
            board.hash ^= board.zobrist_table[moved_piece][board.zobrist_index_finder(old_row, old_col)]

        # Handle en passant capture
        if is_en_passant and captured_piece:
            capture_row = new_row + (1 if moved_piece.startswith("W") else -1)
            board.board[capture_row][new_col] = captured_piece
            board.hash ^= board.zobrist_table[captured_piece][board.zobrist_index_finder(capture_row, new_col)]

        # Normal capture restore
        elif captured_piece:
            board.board[new_row][new_col] = captured_piece
            board.hash ^= board.zobrist_table[captured_piece][board.zobrist_index_finder(new_row, new_col)]

        # Restore king position
        if moved_piece.endswith('_K'):
            board.king_pos[moved_piece[0]] = old_coord

        # Zobrist: toggle side to move
        board.hash ^= board.zobrist_table["BLACK_TO_MOVE"]

        # Restore side to move
        board.curr_move = 'B' if board.curr_move == 'W' else 'W'

        # Clear cached moves for the player to move
        board.cache[board.curr_move].clear()

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
        row, col = coordinate
        piece = board.board[row][col]
        piece_color = piece[0]
        piece_type = piece[2]
        move_cache = board.cache[piece_color]

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
        elif piece_type == 'R':
            moves = get_rook_moves(board, coordinate)
        else:
            return []

        move_cache[coordinate] = moves
        return moves

    def get_moves_efficient(board, coordinate: Coordinate) -> Tuple[MoveCoordinate, ...]:
        row, col = coordinate
        piece = board.board[row][col]
        piece_type = piece[2]

        if piece_type == 'P':
            return get_pawn_moves(board, coordinate)
        elif piece_type == 'B':
            return get_bishop_moves(board, coordinate)
        elif piece_type == 'N':
            return get_knight_moves(board, coordinate)
        elif piece_type == 'R':
            return get_rook_moves(board, coordinate)
        elif piece_type == 'Q':
            return get_queen_moves(board, coordinate)
        elif piece_type == 'K':
            return get_king_moves(board, coordinate)
        else:
            return []

    def get_side_moves(board, color: Color) -> Tuple[MoveCoordinate, ...]:
        side_moves = []
        for row in range(8):
            for col in range(8):
                square = board.board[row][col]
                if square[2] is None or square[0] != color:
                    continue
                coord = (row, col)
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
                piece = board.board[row][col]
                if piece[2] is None or piece[0] != board.curr_move:
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
    def print_board(board) -> None:
        letters = "     a     b     c     d     e     f     g     h"
        print(letters)
        for row in range(ROW_COUNT):
            print(8 - row, end=" | ")
            for col in range(COL_COUNT):
                target = board.board[row][col]
                if target is None:
                    print("   ", end=" | ")
                else:
                    print(f"{target}", end=" | ")
            print(8 - row)
            print('---------------------------------------------------')
        print(letters)

    def castling_mover(board, move: MoveCoordinate) -> None:
        old_coord, _ = move
        row, col = old_coord
        old_target = board.board[row][col]

        if row == 7:
            if col == 4:
                board.board[7][6] = "W_K"
                board.board[7][5] = "W_R"
                board.board[7][4] = None
                board.board[7][7] = None

                # Remove king from original square (7, 4)
                king_old_index = board.zobrist_index_finder(7, 4)
                board.hash ^= board.zobrist_table["W_K"][king_old_index]

                # Add King to square (7, 6)
                king_new_index = board.zobrist_index_finder(7, 6)
                board.hash ^= board.zobrist_table["W_K"][king_new_index]

                # Remove rook from square (7, 7)
                rook_old_index = board.zobrist_index_finder(7, 7)
                board.hash ^= board.zobrist_table["W_R"][rook_old_index]

                # Add rook to square (7, 5)
                rook_new_index = board.zobrist_index_finder(7, 5)
                board.hash ^= board.zobrist_table["W_R"][rook_new_index]
            else:
                board.board[7][2] = "W_K"
                board.board[7][3] = "W_R"
                board.board[7][4] = None
                board.board[7][0] = None

                # Remove king from original square (7, 4)
                king_old_index = board.zobrist_index_finder(7, 4)
                board.hash ^= board.zobrist_table["W_K"][king_old_index]

                # Add King to square (7, 2)
                king_new_index = board.zobrist_index_finder(7, 2)
                board.hash ^= board.zobrist_table["W_K"][king_new_index]

                # Remove rook from square (7, 0)
                rook_old_index = board.zobrist_index_finder(7, 0)
                board.hash ^= board.zobrist_table["W_R"][rook_old_index]

                # Add rook to square (7, 3)
                rook_new_index = board.zobrist_index_finder(7, 3)
                board.hash ^= board.zobrist_table["W_R"][rook_new_index]
        else:
            if col == 4:
                board.board[0][6] = "B_K"
                board.board[0][5] = "B_R"
                board.board[0][4] = None
                board.board[0][7] = None

                # Remove king from original square (0, 4)
                king_old_index = board.zobrist_index_finder(0, 4)
                board.hash ^= board.zobrist_table["B_K"][king_old_index]

                # Add King to square (0, 6)
                king_new_index = board.zobrist_index_finder(0, 6)
                board.hash ^= board.zobrist_table["B_K"][king_new_index]

                # Remove rook from square (0, 7)
                rook_old_index = board.zobrist_index_finder(0, 7)
                board.hash ^= board.zobrist_table["B_R"][rook_old_index]

                # Add rook to square (0, 5)
                rook_new_index = board.zobrist_index_finder(0, 5)
                board.hash ^= board.zobrist_table["B_R"][rook_new_index]
            else:
                board.board[0][2] = "B_K"
                board.board[0][3] = "B_R"
                board.board[0][4] = None
                board.board[0][0] = None

                # Remove king from original square (0, 4)
                king_old_index = board.zobrist_index_finder(0, 4)
                board.hash ^= board.zobrist_table["B_K"][king_old_index]

                # Add King to square (0, 2)
                king_new_index = board.zobrist_index_finder(0, 2)
                board.hash ^= board.zobrist_table["B_K"][king_new_index]

                # Remove rook from square (0, 0)
                rook_old_index = board.zobrist_index_finder(0, 0)
                board.hash ^= board.zobrist_table["B_R"][rook_old_index]

                # Add rook to square (0, 3)
                rook_new_index = board.zobrist_index_finder(0, 3)
                board.hash ^= board.zobrist_table["B_R"][rook_new_index]

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
        row, col = new_coord
        piece = board.board[row][col]

        if piece[2] == 'K':
            if piece[0] == 'W':
                board.white_king_moved = True
            else:
                board.black_king_moved = True

        elif piece[2] == 'R':
            rook_index = 0 if col == 0 else 1
            if piece[0] == 'W':
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
            piece = board.board[target_row][target_col]

            if piece is None:
                continue
            if piece[0] == enemy_color and piece[2] == 'N':
                return True
        
        # Checking for bishops and queen on diagonal
        for _, target_coord in sliding_moves(board, king_coord, BISHOP_DIRECTIONS):
            target_row, target_col = target_coord
            piece = board.board[target_row][target_col]

            if piece is None:
                            continue
            if piece[0] == enemy_color and piece[2] in ('B', 'Q'):
                return True

        # Checking for rooks and queens on straights
        for _, target_coord in sliding_moves(board, king_coord, ROOK_DIRECTIONS):
            target_row, target_col = target_coord
            piece = board.board[target_row][target_col]
            
            if piece is None:
                            continue
            if piece[0] == enemy_color and piece[2] in ('R', 'Q'):
                return True

        for directions in PAWN_CAPTURE_DIRECTIONS[king_color]:
            d_r, d_c = directions
            target_row = king_row + d_r
            target_col = king_col + d_c

            if not (0 <= target_row <= 7 and 0 <= target_col <= 7):
                continue

            piece = board.board[target_row][target_col]

            if piece is None:
                continue
            if piece[0] == enemy_color and piece[2] == 'P':
                return True

        return False
    
    def get_side_mobility(board, color: Color) -> int:
        mobility = 0
        for row in range(8):
            for col in range(8):
                square = board.board[row][col]
                
                if square is None:
                    continue

                if square[2] == color:
                    coord = (row, col)
                    mobility += len(board.get_moves_efficient(coord))
        
        return mobility

    def square_under_attack(board, coord: Coordinate, by_color: str) -> bool:
        enemy_moves = board.get_side_moves(by_color)
        return coord in [target for _, target in enemy_moves]

    def zobrist_index_finder(row: int, col: int) -> int:
        return 8 * (7 - row) + col

    def undo_castling(board, move: MoveCoordinate) -> None:
        old_coord, new_coord = move
        row = old_coord[0]

        if new_coord[1] == 6:  # Kingside
            # Restore king
            board.board[row][4] = f"{board.curr_move}_K"
            board.board[row][6] = None

            # Restore rook
            board.board[row][7] = f"{board.curr_move}_R"
            board.board[row][5] = None

            # Zobrist: revert king move
            board.hash ^= board.zobrist_table[f"{board.curr_move}_K"][board.zobrist_index_finder(row, 6)]
            board.hash ^= board.zobrist_table[f"{board.curr_move}_K"][board.zobrist_index_finder(row, 4)]

            # Zobrist: revert rook move
            board.hash ^= board.zobrist_table[f"{board.curr_move}_R"][board.zobrist_index_finder(row, 5)]
            board.hash ^= board.zobrist_table[f"{board.curr_move}_R"][board.zobrist_index_finder(row, 7)]

        elif new_coord[1] == 2:  # Queenside
            # Restore king
            board.board[row][4] = f"{board.curr_move}_K"
            board.board[row][2] = None

            # Restore rook
            board.board[row][0] = f"{board.curr_move}_R"
            board.board[row][3] = None

            # Zobrist: revert king move
            board.hash ^= board.zobrist_table[f"{board.curr_move}_K"][board.zobrist_index_finder(row, 2)]
            board.hash ^= board.zobrist_table[f"{board.curr_move}_K"][board.zobrist_index_finder(row, 4)]

            # Zobrist: revert rook move
            board.hash ^= board.zobrist_table[f"{board.curr_move}_R"][board.zobrist_index_finder(row, 3)]
            board.hash ^= board.zobrist_table[f"{board.curr_move}_R"][board.zobrist_index_finder(row, 0)]

        # Update king_pos
        board.king_pos[board.curr_move] = (row, 4)

    def is_pawn_promotion(board, move: MoveCoordinate) -> bool:
        old_coord, new_coord = move
        old_row, old_col = old_coord
        new_row, new_col = new_coord

        piece = board.board[old_row][old_col]
        if piece[2] == 'P':
            if piece[0] == 'W' and new_row == 0:
                return True
            elif piece[0] == 'B' and new_row == 7:
                return True
        return False

    def ask_user_promotion() -> str:
        valid = {'Q', 'R', 'B', 'N'}
        while True:
            choice = input("Promote pawn to (Q/R/B/N)? ").upper()
            if choice in valid:
                return choice
            print("Invalid choice. Please choose Q, R, B, or N.")


if __name__ == "__main__":
    board = Board()
    if not board.make_move(((6, 4), (5, 4))):
        print("ILLEGAL")
    else:
        board.print_board()


"""
while True:
    display board

    move_str = input(f"{board.curr_move}'s move (e.g., e2 e4): ").strip().lower()
    if move_str.lower() == 'quit':
        break

    if len(move_str) != 5:
        print("Invalid input.")
        continue

    try:
        from_coord = (8 - int(move_str[1]), ord(move_str[0]) - ord('a'))
        to_coord = (8 - int(move_str[4]), ord(move_str[3]) - ord('a'))
        move = (from_coord, to_coord)
    except:
        print("Invalid coordinates.")
        continue

    # Check for promotion
    if is_pawn_promotion(board, move):
        promotion_piece = ask_user_promotion()
    else:
        promotion_piece = None

    # Make move
    if not board.make_move(move, is_simulation=False, promotion_piece=promotion_piece):
        print("Illegal move.")
        continue

    # Optional: check for end conditions
    result = board.checkmate_stalemate_checker()
    if result:
        print(result)
        break

"""
import copy
from pieces.stepping_moves import stepping_moves
from pieces.sliding_moves import sliding_moves
from src.types import Coordinate, MoveCoordinate, Flags, Moves, Piece, PieceInfo
from src.constants import *
from pieces import *
from typing import List, Tuple

class Board:
    def __init__(self) -> None:
        self.setup_board()

    def setup_board(self) -> None:
        self.board: List[List[Piece]] = [
            ["B_R", "B_N", "B_B", "B_Q", "B_K", "B_B", "B_N", "B_R"],
            ["B_P"] * 8,
            [None] * 8,
            [None] * 8,
            [None] * 8,
            [None] * 8,
            ["W_P"] * 8,
            ["W_R", "W_N", "W_B", "W_Q", "W_K", "W_B", "W_N", "W_R"]
            ]
        self.move_cache: dict[Coordinate, Tuple[MoveCoordinate, ...]] = {}
        self.curr_move = 'W'
        self.move_history: List[Moves] = []

        # Keeping track of king positions in dictionary for o(1) lookup time
        self.king_pos = {
            'W': (7, 4), # Default start is e1
            'B': (0, 4) # Default start is e7
        }

        # Castling flags
        self.white_king_moved = False
        self.black_king_moved = False
        self.white_rook_moved = (False, False) # Queenside, Kingside
        self.black_rook_moved = (False, False) # Queenside, Kingside

        # Tuple to pass into move history
        self.flags = (self.white_king_moved, self.black_king_moved, self.white_rook_moved, self.black_rook_moved)

        # Terminating flags
        self.checkmate = False
        self.stalemate = False

    def make_move(self, move: MoveCoordinate, is_simulation: bool = False) -> bool:
        """
        Apply a move to the board.
        If is_simulation is True, skip validation and flag updates, but still update move_history for undoing.
        """

        # If move is being simulated, no need to validate
        if not is_simulation:
            if not self.can_make_move(move):
                return False

        old_coord, new_coord = move
        old_target = self.get_piece_info(old_coord)
        new_target = self.get_piece_info(new_coord)

        old_row, old_col = old_target.Row, old_target.Col
        new_row, new_col = new_target.Row, new_target.Col

        moved_piece = old_target.Color + '_' + old_target.PieceType
        captured_piece = (
            new_target.Color + '_' + new_target.PieceType
            if new_target.PieceType is not None
            else None
        )

        # Move piece
        self.board[new_row][new_col] = moved_piece
        self.board[old_row][old_col] = None

        # Use dummy flags if simulating (won't affect state)
        if is_simulation:
            dummy_flags: Flags = copy.deepcopy(self.flags)
            move_entry: Moves = (old_coord, new_coord, moved_piece, captured_piece, dummy_flags)
        else:
            # Update flags and add entry for move history
            updated_flags: Flags = self.update_flags_after_move()
            move_entry: Moves = (old_coord, new_coord, moved_piece, captured_piece, updated_flags)

        # If moved piece is a king, updated position in dictionary
        if old_target.PieceType == 'K':
            self.king_pos[old_target.Color] = new_coord

        self.curr_move = 'B' if self.curr_move == 'W' else 'W'
        self.move_history.append(move_entry)
        if not is_simulation:
            self.move_cache.clear()
        return True

    def undo_move(self) -> None:
        """
        Function to undo last move (for simulation purposes)
        """
        if not self.move_history:
            return
        moved_piece_original_coord, captured_piece_original_coord, moved_piece, captured_piece, prev_flags = self.move_history.pop()
        moved_piece_row, moved_piece_col = moved_piece_original_coord
        captured_piece_row, captured_piece_col = captured_piece_original_coord        

        self.board[moved_piece_row][moved_piece_col] = moved_piece
        self.board[captured_piece_row][captured_piece_col] = captured_piece

        # Moved_piece in form W_K or B_K, so [0] = color and [2] = type
        moved_color = moved_piece[0]
        moved_type = moved_piece[2]
        if moved_type == 'K':
            self.king_pos[moved_color] = moved_piece_original_coord

        self.white_king_moved, self.black_king_moved, \
            self.white_rook_moved, self.black_rook_moved = prev_flags
        self.curr_move = 'B' if self.curr_move == 'W' else 'W'

    def can_make_move(self, move: MoveCoordinate) -> bool:
        """
        Check if move is a valid move for pieces
        Call check_checker
        """
        old_coord, _ = move
        is_legal, is_safe = False, False
        legal_moves = set(self.get_piece_moves(old_coord))
        is_legal = move in legal_moves

        if not self.check_checker(move):
            is_safe = True
        return is_legal and is_safe

    def check_checker(self, move: MoveCoordinate) -> bool:
        """
        Simulate move and check if the king is in view of enemy piece
        """
        # Move history -> Tuple[OldCoord, NewCoord, MovedPiece, CapturedPiece, Flags]
        self.make_move(move, True)
        return_val = self.is_king_attacked(self.curr_move)
        self.undo_move()

        return return_val

    def get_piece_moves(self, coordinate: Coordinate) -> Tuple[MoveCoordinate, ...]:
        """
        Pass a coordinate and check all possible moves for that piece by calling the
        appropriate piece function
        """
        if coordinate in self.move_cache:
            return self.move_cache[coordinate]

        piece_type = self.get_piece_info(coordinate).PieceType

        if piece_type == 'P':
            moves = get_pawn_moves(self, coordinate)
        elif piece_type == 'B':
            moves = get_bishop_moves(self, coordinate)
        elif piece_type == 'K':
            moves = get_king_moves(self, coordinate)
        elif piece_type == 'N':
            moves = get_knight_moves(self, coordinate)
        elif piece_type == 'Q':
            moves = get_queen_moves(self, coordinate)
        else:
            moves = get_rook_moves(self, coordinate)

        self.move_cache[coordinate] = moves
        return moves

    def checkmate_stalemate_checker(self, move: MoveCoordinate) -> bool:
        """
        Simulate move and check a side has no legal moves, then if stalemate of checkmate
        """
        pass

    # Helper functions
    def get_piece_info(self, piece_coord: Coordinate) -> PieceInfo:
        row, col = piece_coord
        if self.board[row][col] is None:
            return PieceInfo(Row=row, Col=col, Color=None, PieceType=None)

        color = self.board[row][col][0]
        piece_type = self.board[row][col][2]
        return PieceInfo(Row=row, Col=col, Color=color, PieceType=piece_type)
        
        """
        info = board.get_piece_info((6, 4))
        print(info.color, info.type)
        """

    def print_board(self) -> None:
        letters = "     a     b     c     d     e     f     g     h"
        print(letters)
        for row in range(ROW_COUNT):
            print(8 - row, end=" | ")
            for col in range(COL_COUNT):
                target = self.get_piece_info(coordinate=(row, col))
                if target.PieceType is None:
                    print("   ", end=" | ")
                else:
                    print(f"{target.Color}_{target.PieceType}", end=" | ")
            print(8 - row)
            print('---------------------------------------------------')
        print(letters)

    def castling_mover(self, move: MoveCoordinate) -> None:
        old_coord, _ = move
        old_target = self.get_piece_info(old_coord)

        if old_target.Row == 7:
            if old_target.Col == 4:
                self.board[7][6] = "W_K"
                self.board[7][5] = "W_R"
                self.board[7][4] = None
                self.board[7][7] = None
            else:
                self.board[7][2] = "W_K"
                self.board[7][3] = "W_R"
                self.board[7][4] = None
                self.board[7][0] = None
        else:
            if old_target.Col == 4:
                self.board[0][6] = "B_K"
                self.board[0][5] = "B_R"
                self.board[0][4] = None
                self.board[0][7] = None
            else:
                self.board[0][2] = "B_K"
                self.board[0][3] = "B_R"
                self.board[0][4] = None
                self.board[0][0] = None

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
    
    def update_flags_after_move(self) -> Flags:
        """
        Update all flags after every move
        """
        pass
    
    def is_king_attacked(self, enemy_color: chr) -> bool:
        """
        function to check if king under attack
        * Check in L-Shape for knights
        * Check diagonals for pawn / bishop / queen
        * Check rook moves for queen / rook

        * Stepping moves -> Knights
        * Sliding moves -> Rook, Queen, Bishop
        """
        king_color = 'W' if enemy_color == 'B' else 'B'
        king_coord = self.king_pos[king_color]
        king_row, king_col = king_coord

        # Checking L-shapes for knights
        for target_row, target_col in stepping_moves(self, king_coord, KNIGHT_DIRECTIONS):
            piece = self.get_piece_info((target_row, target_col))

            if piece.PieceType is None:
                continue
            if piece.Color == enemy_color and piece.PieceType == 'N':
                return True
        
        # Checking for bishops and queen on diagonal
        for target_row, target_col in sliding_moves(self, king_coord, BISHOP_DIRECTIONS):
            piece = self.get_piece_info((target_row, target_col))
            if piece.PieceType is None:
                            continue
            if piece.Color == enemy_color and piece.PieceType in ('B', 'Q'):
                return True

        # Checking for rooks and queens on straights
        for target_row, target_col in sliding_moves(self, king_coord, ROOK_DIRECTIONS):
            piece = self.get_piece_info((target_row, target_col))
            if piece.PieceType is None:
                            continue
            if piece.Color == enemy_color and piece.PieceType in ('R', 'Q'):
                return True

        for d_r, d_c in PAWN_CAPTURE_DIRECTIONS[king_color]:
            target_row = king_row + d_r
            target_col = king_col + d_c

            if not (0 <= target_row <= 7 and 0 <= target_col <= 7):
                continue

            piece = self.get_piece_info((target_row, target_col))

            if piece.PieceType is None:
                continue
            if piece.Color == enemy_color and piece.PieceType == 'P':
                return True

        return False
from src.types import Coordinate, MoveCoordinate, Flags, Moves, Piece, PieceInfo
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
        self.move_history: List[Moves] = []
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

    def make_move(self, move: MoveCoordinate) -> bool:
        """
        update board state after making move [DONE]
        update any flags [DONE]
        update move history after making move [DONE]
        """
        if not self.can_make_move(move):
            return False
        
        old_coord, new_coord = move
        
        old_target = self.get_piece_info(old_coord)
        new_target = self.get_piece_info(new_coord)

        old_row, old_col = old_target.Row, old_target.Col
        new_row, new_col = new_target.Row, new_target.Col

        # Getting information for move history
        moved_piece = old_target.Color + '_' + old_target.PieceType
        if new_target.PieceType is not None:
            captured_piece = new_target.Color + '_' + new_target.PieceType
        else:
            captured_piece = None
        flags: Flags = self.update_flags_after_move()

        # Updating board state
        self.board[new_row][new_col] = moved_piece
        self.board[old_row][old_col] = None

        # Updating move history        
        move_entry: Moves = (old_coord, new_coord, moved_piece, captured_piece, flags)
        self.move_history.append(move_entry)

        return True

    def can_make_move(self, move: MoveCoordinate) -> bool:
        """
        Check if move is a valid move for pieces
        Call check_checker
        """
        pass

    def check_checker(self, move: MoveCoordinate) -> bool:
        """
        Simulate move and check if the king is in view of enemy piece
        """
        pass

    def get_piece_moves(self, coordinate: Coordinate) -> Tuple[MoveCoordinate, ...]:
        """
        Pass a coordinate and check all possible moves for that piece by calling the
        appropriate piece function
        """
        pass

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
        for row in range(8):
            print(8 - row, end=" | ")
            for col in range(8):
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

    def update_flags_after_move(self) -> Flags:
        """
        Update castling and check flags after every move
        """
        pass

# if __name__ == '__main__':
#     board = Board()
#     board.print_board()
#     board.make_move(((6, 4), (4, 4)))
#     board.print_board()
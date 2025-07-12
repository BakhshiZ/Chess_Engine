from src.types import BoardPosition, Coordinate, Piece, PieceInfo
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

        # Castling flags
        self.white_king_moved = False
        self.black_king_moved = False
        self.white_rook_moved = [False, False] # Queenside, Kingside
        self.black_rook_moved = [False, False] # Queenside, Kingside

        # Terminating flags
        self.checkmate = False
        self.stalemate = False

    def make_move(self, move: Coordinate) -> bool:
        old_coord, new_coord = move
        """
        update board state after making move
        update move history after making move
        update any flags
        """

    def can_make_move(self, move: Coordinate) -> bool:
        pass

    def check_checker(self, move: Coordinate) -> bool:
        pass

    def get_piece_moves(self, coordinate: BoardPosition) -> List[Coordinate]:
        pass

    def checkmate_stalemate_checker(self, move: Coordinate) -> bool:
        pass

    def get_piece_info(self, coordinate: BoardPosition) -> PieceInfo:
        row, col = coordinate
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

if __name__ == '__main__':
    board = Board()
    board.print_board()
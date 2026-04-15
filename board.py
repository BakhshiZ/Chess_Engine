from constants import *

class Board:
    """
    Class for handling the chess board. Lowercase pieces are black pieces
    while uppercase pieces are white ones
    """
    def __init__(self):
        self.grid = [["r", "n", "b", "k", "q", "b", "n", "r"],
                ["p", "p", "p", "p", "p", "p", "p", "p"],
                [None, None, None, None, None, None, None, None],
                [None, None, None, None, None, None, None, None],
                [None, None, None, None, None, None, None, None]
                [None, None, None, None, None, None, None, None],
                ["P", "P", "P", "P", "P", "P", "P", "P"],
                ["R", "N", "B", "K", "Q", "B", "N", "R"]]

        # White Kingside, White Queenside, Black Kingside, Black Queenside
        self.can_castle = [True, True, True, True]
        self.en_passant_coords: Coords | None = None # Reset after every move
        self.current_move = 'w'

    def get_piece_at(self, coords: Coords) -> Piece:
        piece = self.grid[coords.row][coords.col]

        if piece is None:
            return Piece(None, None)
        
        piece_type = PIECE_MAP[piece]
        piece_color = 'w' if piece == piece.Upper() else 'b'

        return Piece(piece_type, piece_color)
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
        self.move_history: list[MoveHistory] = []

    def get_piece_at(self, coords: Coords) -> Piece:
        piece = self.grid[coords.row][coords.col]

        if piece is None:
            return Piece(None, None)
        
        piece_type = PIECE_MAP[piece]
        piece_color = 'w' if piece == piece.Upper() else 'b'

        return Piece(piece_type, piece_color)
    
    def make_move(self, move: Move) -> None:
        start_coords = move.start
        end_coords = move.end
        capture_flag = move.is_capture
        castle_flags = move.is_castle
        promotion_flag = move.is_promotion
        en_passant_flag = move.is_en_passant
        new_type = move.promoted_to
        
        en_passantable_pawn = self.en_passant_coords
        """
        E6, E4, E4, True, [F, F, F, F], False, False, None

        D3, D5, D5, False, [F, F, F, F], False, False, None

        E5, D6, D5, False, [F, F, F, F], False, True, None
        """
        self.en_passant_coords = None
        moved_piece = self.get_piece_at(start_coords)
        
        if en_passant_flag:
            pawn_row = start_coords.row
            pawn_col = end_coords.col

            pawn_coords = Coords(pawn_row, pawn_col)

            captured_piece = self.get_piece_at(pawn_coords)

            self.grid[pawn_row][pawn_col] = None
        
        else:
            captured_piece = self.get_piece_at(end_coords)

        if promotion_flag:
            self.grid[end_coords.row][end_coords.col] = self._get_piece_chr(moved_piece, new_type)
        else:
            self.grid[end_coords.row][end_coords.col] = self.grid[start_coords.row][start_coords.col]
        self.grid[start_coords.row][start_coords.col] = None

        if moved_piece.type == "pawn" and abs(end_coords.row - start_coords.row) == 2:
            self.en_passant_coords = end_coords
        
        self.current_move = 'b' if self.current_move == 'w' else 'w'

        move_history_entry = MoveHistory(
            start=start_coords,
            end=end_coords,
            en_passantable_pawn=en_passantable_pawn,
            is_promotion=promotion_flag,
            is_en_passant=en_passant_flag,
            is_capture=capture_flag,
            is_castle=castle_flags,
            new_type=new_type,
            moved_piece=moved_piece,
            captured_piece=captured_piece
        )

        self.move_history.append(move_history_entry)

    def _get_piece_chr(self, piece: Piece, new_type: PIECE_TYPE=None) -> chr | None:
        if new_type:
            piece_chr = new_type[0] if new_type != "knight" else 'n'            
        else:
            piece_chr = piece.type[0] if piece.type != "knight" else 'n'

        if piece.color == 'w':
            piece_chr = piece_chr.upper()

        return piece_chr
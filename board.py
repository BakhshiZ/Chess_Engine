from constants import *
from typing import Union, cast

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
                [None, None, None, None, None, None, None, None],
                [None, None, None, None, None, None, None, None],
                ["P", "P", "P", "P", "P", "P", "P", "P"],
                ["R", "N", "B", "K", "Q", "B", "N", "R"]]

        # White Kingside, White Queenside, Black Kingside, Black Queenside
        self.can_castle = [True, True, True, True]
        self.en_passant_coords: Coords | None = None # Reset after every move
        self.current_move = 'w'
        self.move_history: list[MoveHistory] = []

    def get_piece_at(self, coords: Coords) -> Piece:
        piece = self.grid[coords.rank][coords.file]

        if piece is None:
            return Piece(None, None)

        piece_type = PIECE_MAP[piece.lower()]
        piece_color = 'w' if piece == piece.upper() else 'b'

        return Piece(piece_type, piece_color)

    def make_move(self, move: Move) -> None:
        """
        Function to update board state and move history
        """
        start_coords = move.start
        end_coords = move.end
        capture_flag = move.is_capture
        castle_flags = move.is_castle
        promotion_flag = move.is_promotion
        en_passant_flag = move.is_en_passant
        new_type = move.promoted_to

        en_passantable_pawn = self.en_passant_coords
        self.en_passant_coords = None
        moved_piece = self.get_piece_at(start_coords)

        if en_passant_flag:
            pawn_rank = start_coords.rank
            pawn_file = end_coords.file

            pawn_coords = Coords(pawn_rank, pawn_file)

            captured_piece = self.get_piece_at(pawn_coords)

            self.grid[pawn_rank][pawn_file] = None

        else:
            captured_piece = self.get_piece_at(end_coords)

        if promotion_flag:
            self.grid[end_coords.rank][end_coords.file] = self._get_piece_chr(moved_piece, new_type)
        else:
            self.grid[end_coords.rank][end_coords.file] = self.grid[start_coords.rank][start_coords.file]
        self.grid[start_coords.rank][start_coords.file] = None

        if moved_piece.type == "pawn" and abs(end_coords.rank - start_coords.rank) == 2:
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

    def _get_piece_chr(self, piece: Piece, new_type: PIECE_TYPE=None) -> Union[str, None]:
        """
        Helper function to return character stored in grid given a piece type and fileour
        """
        if piece.type is None:
            return None

        if new_type:
            piece_chr = new_type[0] if new_type != "knight" else 'n'            
        else:
            piece_chr = piece.type[0] if piece.type != "knight" else 'n'

        if piece.color == 'w':
            piece_chr = piece_chr.upper()

        return piece_chr
    
    def _alg_to_coords(self, square: SQUARE) -> Coords:
        rank = 8 - int(square[1])
        file = FILES.index(square[0])
        
        coord = Coords(rank, file)
        return coord
    
    def _coords_to_alg(self, coords: Coords) -> SQUARE:
        rank = RANKS[coords.rank]
        file = FILES[coords.file]
        square = file + rank

        return cast(SQUARE, square)
    
    def __str__(self):
        return_str = ""
        for rank in range(8):
            for file in range(8):
                if self.grid[rank][file] is None:
                    return_str += "  | "
                else:
                    return_str += f"{self.grid[rank][file]} | "
            return_str += '\n--------------------------------\n'
        return return_str

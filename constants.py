from typing import Literal, NamedTuple, Union
from dataclasses import dataclass, field

type COLOR = Literal[None, 'w', 'b']
type PIECE_TYPE = Literal[None, "p", "n", "b", "r", "q", "k"]
type PROMOTION_OPTION = Literal[None, "knight", "bishop", "rook", "queen"]
FILES = "abcdefgh"
RANKS = "12345678"
type SQUARE = Literal["a1", "a2", "a3", "a4", "a5", "a6", "a7", "a8",
                      "b1", "b2", "b3", "b4", "b5", "b6", "b7", "b8",
                      "c1", "c2", "c3", "c4", "c5", "c6", "c7", "c8",
                      "d1", "d2", "d3", "d4", "d5", "d6", "d7", "d8",
                      "e1", "e2", "e3", "e4", "e5", "e6", "e7", "e8",
                      "f1", "f2", "f3", "f4", "f5", "f6", "f7", "f8",
                      "g1", "g2", "g3", "g4", "g5", "g6", "g7", "g8",
                      "h1", "h2", "h3", "h4", "h5", "h6", "h7", "h8"
                      ]
PROMOTION_PIECE = ("n", "b", "r", "q")

class Coords(NamedTuple):
    rank: int
    file: int

class Move(NamedTuple):
    start: Coords
    end: Coords
    is_capture: bool = False
    is_castle: list[bool] = [False, False, False, False]
    is_promotion: bool = False
    is_en_passant: bool = False
    promoted_to: PIECE_TYPE | None = None

class Direction(NamedTuple):
    rank_offset: int
    file_offset: int

@dataclass
class Piece:
    """Class for storing information about a piece on a tile"""
    type: PIECE_TYPE
    color: COLOR

@dataclass
class MoveHistory:
    """Class for storing move history to allow for undo"""
    start: Coords
    end: Coords
    moved_piece: Piece
    en_passantable_pawn: Coords | None = None
    is_promotion: bool = False
    is_en_passant: bool = False
    is_capture: bool = False
    is_castle: list[bool] = field(default_factory=list)
    new_type: PIECE_TYPE | None = None
    captured_piece: Piece | None = None

BISHOP_DIRECTIONS = (
    Direction(-1, -1), # UL
    Direction(-1, 1),  # UR
    Direction(1, 1),   # DR
    Direction(1, -1))  # DL

# U, D, R, L
ROOK_DIRECTIONS = (
    Direction(-1, 0), 
    Direction(1, 0), 
    Direction(0, 1), 
    Direction(0, -1))

KING_DIRECTIONS = BISHOP_DIRECTIONS + ROOK_DIRECTIONS
QUEEN_DIRECTIONS = KING_DIRECTIONS

KNIGHT_DIRECTIONS = (
    Direction(-2, -1), Direction(-2, 1),  # Up 2, Left/Right 1
    Direction(2, -1),  Direction(2, 1),   # Down 2, Left/Right 1
    Direction(-1, -2), Direction(1, -2),  # Left 2, Up/Down 1
    Direction(-1, 2),  Direction(1, 2),   # Right 2, Up/Down 1
)

PAWN_CAPTURE_DIRECTIONS = (-1, 1)
PIECE_MAP = {
    'p': "pawn",
    'n': "knight",
    'b': "bishop",
    'r': "rook",
    'q': "queen",
    'k': "king",
    None: None
}


"""
To undo moves, you need

castling values (true or false)
captured piece at tile
promoted piece value
move
"""
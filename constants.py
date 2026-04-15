from typing import Literal, NamedTuple
from attr import dataclass

type COLOR = Literal[None, 'w', 'b']
type PIECE_TYPE = Literal[None, "pawn", "knight", "bishop", "rook", "queen", "king"]
type PROMOTION_OPTION = Literal[None, "n", "b", "r", "q"]

@dataclass
class Piece:
    """Class for storing information about a piece on a tile"""
    type: PIECE_TYPE
    color: COLOR

class Coords(NamedTuple):
    row: int
    col: int

class Move(NamedTuple):
    start: Coords
    end: Coords
    is_capture: bool = False
    is_castle: bool = False
    is_promotion: bool = False
    promoted_to: PIECE_TYPE | None = None
    is_en_passant: bool = False

class Direction(NamedTuple):
    row_offset: int
    col_offset: int

# UL, UR, DR, DL
BISHOP_DIRECTIONS = (
    Direction(-1, -1), 
    Direction(-1, 1), 
    Direction(1, 1), 
    Direction(1, -1))

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
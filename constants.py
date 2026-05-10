from typing import Literal, NamedTuple

FILES = "abcdefgh"
RANKS = "12345678"
type COLOR = Literal[None, 'w', 'b']
type PIECE_TYPE = Literal[None, "p", "n", "b", "r", "q", "k"]

class Coord(NamedTuple):
    row: int
    col: int

type Move = tuple[Coord, Coord]

class MoveHistoryEntry(NamedTuple):
    start_coords: Coord
    end_coords: Coord
    captured_piece: PIECE_TYPE
    captured_color: COLOR

BISHOP_DIRECTIONS = (
    (-1, -1), # UL
    (-1, 1),  # UR
    (1, 1),   # DR
    (1, -1))  # DL

# U, D, R, L
ROOK_DIRECTIONS = (
    (-1, 0), 
    (1, 0), 
    (0, 1), 
    (0, -1))

KING_DIRECTIONS = BISHOP_DIRECTIONS + ROOK_DIRECTIONS
QUEEN_DIRECTIONS = KING_DIRECTIONS

KNIGHT_DIRECTIONS = (
    (-2, -1), (-2, 1),  # Up 2, Left/Right 1
    (2, -1),  (2, 1),   # Down 2, Left/Right 1
    (-1, -2), (1, -2),  # Left 2, Up/Down 1
    (-1, 2),  (1, 2),   # Right 2, Up/Down 1
)
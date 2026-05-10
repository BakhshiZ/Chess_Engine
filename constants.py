from typing import Literal, NamedTuple

FILES = "abcdefgh"
RANKS = "12345678"
type COLOR = Literal[None, 'w', 'b']
type PIECE_TYPE = Literal[None, "p", "n", "b", "r", "q", "k"]
type SQUARE = Literal["a1", "a2", "a3", "a4", "a5", "a6", "a7", "a8",
                      "b1", "b2", "b3", "b4", "b5", "b6", "b7", "b8",
                      "c1", "c2", "c3", "c4", "c5", "c6", "c7", "c8",
                      "d1", "d2", "d3", "d4", "d5", "d6", "d7", "d8",
                      "e1", "e2", "e3", "e4", "e5", "e6", "e7", "e8",
                      "f1", "f2", "f3", "f4", "f5", "f6", "f7", "f8",
                      "g1", "g2", "g3", "g4", "g5", "g6", "g7", "g8",
                      "h1", "h2", "h3", "h4", "h5", "h6", "h7", "h8"
                      ]
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
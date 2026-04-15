from typing import Literal, NamedTuple

type COLOR = Literal['w', 'b']

class Coords(NamedTuple):
    row: int
    col: int

class Move(NamedTuple):
    start: Coords
    end: Coords

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
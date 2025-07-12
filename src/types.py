from typing import Literal, Tuple, Union
from dataclasses import dataclass

# Coorindates types
Coordinate = Tuple[int, int]
OldCoord = Coordinate
NewCoord = Coordinate
MoveCoordinate = Tuple[OldCoord, NewCoord]

# Piece attributes
Color = Literal['W', 'B']
PieceType = Literal['P', 'N', 'B', 'R', 'Q', 'K']

@dataclass(frozen=True)
class PieceInfo:
    Row: int
    Col: int
    Color: Union[Color, None]
    PieceType: Union[PieceType, None]

# Pieces can be in form of "W_K" or None
Piece = Union[str | None]
CapturedPiece = Piece
MovedPiece = Piece

# Castling flags 
Flags = Tuple[bool, bool, Tuple[bool, bool], Tuple[bool, bool]]

Moves = Tuple[OldCoord, NewCoord, MovedPiece, CapturedPiece, Flags]

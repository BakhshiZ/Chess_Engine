from typing import Tuple, Literal
from dataclasses import dataclass

BoardPosition = Tuple[int, int]
OldCoord = BoardPosition
NewCoord = BoardPosition
Coordinate = Tuple[OldCoord, NewCoord]

Piece = str | None

@dataclass(frozen=True)
class PieceInfo:
    Row: int
    Col: int
    Color: Literal['W', 'B']
    PieceType: Literal['P', 'N', 'B', 'Q', 'K']
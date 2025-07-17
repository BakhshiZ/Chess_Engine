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

# Checker for if last move was en passant and what promotion was
DidEnPassant = bool
PromotionPiece = Piece

# Castling flags 
Flags = Tuple[bool, bool, Tuple[bool, bool], Tuple[bool, bool]]

# Move entry for move history
Moves = Tuple[OldCoord, NewCoord, MovedPiece, CapturedPiece, Flags, DidEnPassant, PromotionPiece]

# Return for engine minimax
Eval_Move = Tuple[float, MoveCoordinate]
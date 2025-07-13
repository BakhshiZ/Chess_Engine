MIN_INDEX = 0
MAX_INDEX = 7
ROW_COUNT = 8
COL_COUNT = 8

ALL_DIRECTIONS = [
    (1, 0), (0, -1), (0, 1), (-1, 0), # U, L, R, D
    (1, -1), (1, 1), (-1, -1), (-1, 1) # UL, UR, DL, DR
]

BISHOP_DIRECTIONS = [
    (1, -1), (1, 1), # UL, UR
    (-1, -1), (-1, 1) # DL, DR
]

KNIGHT_DIRECTIONS = [
    (1, -2), (-1, -2), # LLU, LLD
    (-2, -1), (-2, 1), # DDL, DDR
    (2, -1), (2, 1), # UUL, UUR
    (1, 2), (-1, 2) # RRU, RRD
]

ROOK_DIRECTIONS = [
    (0, -1), (0, 1), # L, R
    (1, 0), (-1, 0) # U, D
]

PAWN_CAPTURE_DIRECTIONS = {
    'W': [(-1, -1), (-1, 1)],
    'B': [(1, -1), (1, 1)]
},
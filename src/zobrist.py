import random
from typing import List, TYPE_CHECKING
if TYPE_CHECKING:
    from src.board import Board

PIECES = [
    "W_P", "W_N", "W_B", "W_R", "W_Q", "W_K",
    "B_P", "B_N", "B_B", "B_R", "B_Q", "B_K"
]
# Using fixed seed so that the zobrist table is always the same
random.seed(42)

"""
Computes the Zobrist hash for the current board state.

STEPS:
1. Get bitboards: [DONE]
    * Build 12 bitboards (1 for each piece type).
    * Each bitboard is a 64-bit integer where each bit represents a square.
    * A bit is set to 1 if that piece occupies that square.

2. Initialize the Zobrist table: [DONE]
    * A static lookup table with 12 keys (one per piece type).
    * Each key maps to a list of 64 random 64-bit integers (one for each square).
    * Each (piece, square) pair has a unique random number.

3. Build the Zobrist hash:
    * Start with hash = 0.
    * For each piece type:
        * For each bit set to 1 in the corresponding bitboard:
            * XOR the hash with ZOBRIST_TABLE[piece][square_index].

Returns:
    A 64-bit integer representing the unique hash of the current board state.
"""
    
def initialise_bitboards(board: 'Board') -> dict[str, int]:
    """
    STEP 1
    --------------------------------------
    Index for bitboard goes from 0 - 63
    
    a8 = 56, b8 = 57... g8 = 62, h8 = 63
    .                               .
    .                               .
    .                               .
    a1 = 0; b1 = 1.... g1 = 6; h1 = 7
    --------------------------------------
    0, 8, 16, 24, 32, 40, 48, 56 = new rows
    
    row with index 0 is 8th rank
    row with index 1 is 7th rank
    .
    .
    .
    row with index 6 is 2nd rank
    row with index 7 is 1st rank
    --------------------------------------
    8 * (7 - row) + col is each square's index
    """
    bitboards = {
    # White side bitboards
    "W_P": 0b00000000_00000000_00000000_00000000_00000000_00000000_00000000_00000000,
    "W_N": 0b00000000_00000000_00000000_00000000_00000000_00000000_00000000_00000000,
    "W_B": 0b00000000_00000000_00000000_00000000_00000000_00000000_00000000_00000000,
    "W_R": 0b00000000_00000000_00000000_00000000_00000000_00000000_00000000_00000000,
    "W_Q": 0b00000000_00000000_00000000_00000000_00000000_00000000_00000000_00000000,
    "W_K": 0b00000000_00000000_00000000_00000000_00000000_00000000_00000000_00000000,

    # Black side bitboards
    "B_P": 0b00000000_00000000_00000000_00000000_00000000_00000000_00000000_00000000,
    "B_N": 0b00000000_00000000_00000000_00000000_00000000_00000000_00000000_00000000,
    "B_B": 0b00000000_00000000_00000000_00000000_00000000_00000000_00000000_00000000,
    "B_R": 0b00000000_00000000_00000000_00000000_00000000_00000000_00000000_00000000,
    "B_Q": 0b00000000_00000000_00000000_00000000_00000000_00000000_00000000_00000000,
    "B_K": 0b00000000_00000000_00000000_00000000_00000000_00000000_00000000_00000000
    }

    for piece in PIECES:
        for row in range(8):
            for col in range(8):
                piece_at_square = board[row][col]
                if piece_at_square == piece:
                    # Using OR to update bit when piece is at square
                    bit_index = (8 * (7 - row)) + col
                    mask = 1 << bit_index
                    bitboards[piece] = bitboards[piece] | mask

    return bitboards

"""
STEP 2
------------------------
Zobrist hash table is a lookup table where we have map in form
(piece, square) and it returns a random 64-bit number representing 
which square the piece is on.

e.g. if white queen is on a3, return 62 and if on a2, return 21, etc etc 
"""
zobrist_table = {
    "W_P": [random.getrandbits(64) for _ in range(64)],
    "W_N": [random.getrandbits(64) for _ in range(64)], 
    "W_B": [random.getrandbits(64) for _ in range(64)], 
    "W_R": [random.getrandbits(64) for _ in range(64)], 
    "W_Q": [random.getrandbits(64) for _ in range(64)], 
    "W_K": [random.getrandbits(64) for _ in range(64)],
    "B_P": [random.getrandbits(64) for _ in range(64)], 
    "B_N": [random.getrandbits(64) for _ in range(64)], 
    "B_B": [random.getrandbits(64) for _ in range(64)], 
    "B_R": [random.getrandbits(64) for _ in range(64)], 
    "B_Q": [random.getrandbits(64) for _ in range(64)], 
    "B_K": [random.getrandbits(64) for _ in range(64)],
    "BLACK_TO_MOVE": [random.getrandbits(64)]
    }

def compute_zobrist_hash(board: 'Board') -> int:
    """
    STEP 3
    -------------------------------
    Iterate through all the pieces and their bitboards. Check wherever
    bitboard bit is 1 and where it is, XOR the hash value with the zobrist_table
    value. Return final hash value
    """
    hash_val = 0
    bitboards = initialise_bitboards(board)

    for piece in PIECES:
        for i in range(64):
            """
            Make the i-th bit the least significant bit and check if it equals 1
            """
            if (bitboards[piece] >> i & 1):
                hash_val = hash_val ^ zobrist_table[piece][i]
    
    return hash_val
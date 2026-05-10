from constants import *
from typing import cast

class Board:
    """
    Class for handling the chess board. Lowercase pieces are black pieces
    while uppercase pieces are white ones
    """
    def __init__(self):
        self.grid = [["r", "n", "b", "q", "k", "b", "n", "r"],
                ["p", "p", "p", "p", "p", "p", "p", "p"],
                [None, None, None, None, None, None, None, None],
                [None, None, None, None, None, None, None, None],
                [None, None, None, None, None, None, None, None],
                [None, None, None, None, None, None, None, None],
                ["P", "P", "P", "P", "P", "P", "P", "P"],
                ["R", "N", "B", "Q", "K", "B", "N", "R"]]

        self.current_move = 'w'
        self.move_history: list[MoveHistoryEntry] = []

    def make_move(self, move: Move) -> None:
        start_coords, end_coords = move
        self.move_history.append(MoveHistoryEntry(
            start_coords=start_coords,
            end_coords=end_coords,
            captured_piece=self.grid[end_coords.row][end_coords.col],
            captured_color=self._get_piece_color(end_coords)
        ))

        self.grid[end_coords.row][end_coords.col] = self.grid[start_coords.row][start_coords.col]
        self.grid[start_coords.row][start_coords.col] = None
        self.current_move = 'b' if self.current_move == 'w' else 'w'

    def undo_move(self) -> None:
        if len(self.move_history) == 0:
            return
        
        last_move = self.move_history.pop()
        start_coords = last_move.start_coords
        end_coords = last_move.end_coords
        captured_piece = last_move.captured_piece
        captured_color = last_move.captured_color

        self.grid[start_coords.row][start_coords.col] = self.grid[end_coords.row][end_coords.col]
        if captured_piece is not None:
            if captured_color == 'w':
                captured_piece = captured_piece.upper()

        self.grid[end_coords.row][end_coords.col] = captured_piece

    def _alg_to_coords(self, square: SQUARE):
        rank = 8 - int(square[1])
        file = FILES.index(square[0])
        
        coord = (rank, file)
        return coord
    
    def _coords_to_alg(self, coords) -> SQUARE:
        rank = RANKS[coords.rank - 1]
        file = FILES[coords.file]
        square = file + rank

        return cast(SQUARE, square)
    
    def _get_piece_color(self, coords: Coord) -> COLOR:
        if self.grid[coords.row][coords.col] is None:
            return None

        # lowercase letters = black
        if 97 <= ord(self.grid[coords.row][coords.col]) <= 122:
            return 'b'
        else:
            return 'w'

    def __str__(self):
        return_str = ""
        for rank in range(8):
            for file in range(8):
                if self.grid[rank][file] is None:
                    return_str += "  | "
                else:
                    return_str += f"{self.grid[rank][file]} | "
            return_str += '\n--------------------------------\n'
        return return_str
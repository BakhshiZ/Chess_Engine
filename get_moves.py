from typing import TYPE_CHECKING
from constants import *

if TYPE_CHECKING:
    from board import Board

class MoveGenerator:

    def __init__(self, board: Board):
        self.board = board
        self.en_passant_target = None

    def _get_sliding_moves(self, old_coords: Coord, piece_type: PIECE_TYPE) -> list[Move]:
        """
        Function to get moves for sliding pieces (bishop, rook and queen)
        """
        legal_moves = []
        direction = self._get_directions(piece_type)

        for dr, dc in direction:
            new_row = old_coords.row + dr
            new_col = old_coords.col + dc
            while (0 <= new_row <= 7 and 0 <= new_col <= 7):
                new_coords = Coord(new_row, new_col)

                if self.board._get_piece_color(new_coords) is None:
                    legal_moves.append((old_coords, new_coords))
                elif self.board._get_piece_color(new_coords) != self.board.current_move:
                    legal_moves.append((old_coords, new_coords))
                    break
                else:
                    break

                new_row += dr
                new_col += dc

        return legal_moves
    
    def _get_stepping_moves(self, old_coords: Coord, piece_type: PIECE_TYPE) -> list[Move]:
        """
        Function to get moves for stepping pieces (king, knight)
        """
        legal_moves = []
        direction = self._get_directions(piece_type)

        for dr, dc in direction:
            new_row = old_coords.row + dr
            new_col = old_coords.col + dc

            if not (0 <= new_row <= 7 and 0 <= new_col <= 7):
                continue
            new_coords = Coord(new_row, new_col)

            if self.board._get_piece_color(new_coords) is None:
                legal_moves.append((old_coords, new_coords))
            elif self.board._get_piece_color(new_coords) != self.board.current_move:
                legal_moves.append((old_coords, new_coords))
                break
            else:
                break

        return legal_moves
    
    def _get_directions(self, piece_type: PIECE_TYPE):
        if piece_type == 'b':
            direction = BISHOP_DIRECTIONS
        elif piece_type == 'k':
            direction = KING_DIRECTIONS
        elif piece_type == 'n':
            direction = KNIGHT_DIRECTIONS
        elif piece_type == 'q':
            direction = QUEEN_DIRECTIONS
        elif piece_type == 'r':
            direction = ROOK_DIRECTIONS
        else:
            direction = []
        
        return direction

    def _get_pawn_moves(self, old_coords: Coord) -> list[Move]:
        legal_moves = []
        
        if self.board.current_move == 'w':
            direction = -1
            starting_row = 6
        else:
            direction = 1
            starting_row = 1
        # One step move
        one_step_row = old_coords.row + direction
        new_coords = Coord(one_step_row, old_coords.col)
        if self.board.grid[one_step_row][old_coords.col] is None:
            legal_moves.append((old_coords, new_coords))
        
            if old_coords.row == starting_row:
                two_step_row = one_step_row + direction
                new_coords = Coord(two_step_row, old_coords.col)
                if self.board.grid[two_step_row][old_coords.col] is None:
                    legal_moves.append((old_coords, new_coords))
        return legal_moves
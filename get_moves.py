from typing import TYPE_CHECKING
from constants import *

if TYPE_CHECKING:
    from board import Board

class MoveGenerator:

    def __init__(self, board: Board):
        self.board = board

    def _get_side_pseudo_legal_moves(self) -> list[Move]:
        pseudo_legal_moves = []
        for row in range(8):
            for col in range(8):
                coords = Coord(row, col)
                if self.board._get_piece_color(coords) == self.board.current_move:
                    if self.board.grid[row][col] in ['p', 'P']:
                        pseudo_legal_moves += self._get_pawn_moves(coords)
                    elif self.board.grid[row][col] in ['b', 'B']:
                        pseudo_legal_moves += self._get_sliding_moves(coords, 'b')
                    elif self.board.grid[row][col] in ['n', 'N']:
                        pseudo_legal_moves += self._get_stepping_moves(coords, 'n')
                    elif self.board.grid[row][col] in ['r', 'R']:
                        pseudo_legal_moves += self._get_sliding_moves(coords, 'r')
                    elif self.board.grid[row][col] in ['q', 'Q']:
                        pseudo_legal_moves += self._get_sliding_moves(coords, 'q')
                    else:
                        pseudo_legal_moves += self._get_stepping_moves(coords, 'k')
        
        return pseudo_legal_moves
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
        """
        Function to get all possible pawn moves

        TO-DO:
            add en passant
            add promotion
        """
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

            # Two step move
            if old_coords.row == starting_row:
                two_step_row = one_step_row + direction
                new_coords = Coord(two_step_row, old_coords.col)
                if self.board.grid[two_step_row][old_coords.col] is None:
                    legal_moves.append((old_coords, new_coords))

        # Captures
        pawn_capture_directions = (
            (direction, -1),
            (direction, 1)
        )

        for dr, dc in pawn_capture_directions:
            new_row = old_coords.row + dr
            new_col = old_coords.col + dc
            new_coords = Coord(new_row, new_col)
            if not (0 <= new_row <= 7 and 0 <= new_col <= 7):
                continue

            if self.board._get_piece_color(new_coords) != self.board.current_move:
                legal_moves.append((old_coords, new_coords))
        return legal_moves
    
    def _is_king_in_check(self, king_coords: Coord) -> bool:
        """
        Function that checks outwards from king to see if it is under attack
        """

        # Knight
        for dr, dc in KNIGHT_DIRECTIONS:
            attacker_row = king_coords.row + dr
            attacker_col = king_coords.col + dc
            attacker_coords = Coord(attacker_row, attacker_col)
            
            if not (0 <= attacker_row <= 7 and 0 <= attacker_col <= 7):
                continue
            
            if self.board._get_piece_color(attacker_coords) != self.board.current_move and \
                self.board.grid[attacker_row][attacker_col] in ['n', 'N']:
                return True
        
        # Bishop & Queen (diagonal)
        for dr, dc in BISHOP_DIRECTIONS:
            attacker_row = king_coords.row + dr
            attacker_col = king_coords.col + dc

            while (0 <= attacker_row <= 7 and 0 <= attacker_col <= 7):
                attacker_coords = Coord(attacker_row, attacker_col)
                if self.board._get_piece_color(attacker_coords) is None:
                    attacker_row += dr
                    attacker_col += dc
                elif self.board._get_piece_color(attacker_coords) == self.board.current_move:
                    break
                elif self.board._get_piece_color(attacker_coords) != self.board.current_move and \
                    self.board.grid[attacker_row][attacker_col] in ['b', 'B', 'q', 'Q']:
                    return True
                else:
                    break
        
        # Rook & Queen (vertical + horizontal)
        for dr, dc in ROOK_DIRECTIONS:
            attacker_row = king_coords.row + dr
            attacker_col = king_coords.col + dc

            while (0 <= attacker_row <= 7 and 0 <= attacker_col <= 7):
                attacker_coords = Coord(attacker_row, attacker_col)
                
                if self.board._get_piece_color(attacker_coords) is None:
                    attacker_row += dr
                    attacker_col += dc
                elif self.board._get_piece_color(attacker_coords) == self.board.current_move:
                    break
                elif self.board._get_piece_color(attacker_coords) != self.board.current_move and \
                    self.board.grid[attacker_row][attacker_col] in ['r', 'R', 'q', 'Q']:
                    return True
                else:
                    break
        # Pawn
        if self.board.current_move == 'w':
            direction = -1
        else:
            direction = 1

        for dc in [-1, 1]:
            attacker_row = king_coords.row + direction
            attacker_col = king_coords.col + dc
            attacker_coords = Coord(attacker_row, attacker_col)

            if not (0 <= attacker_row <= 7 and 0 <= attacker_col <= 7):
                continue

            if self.board._get_piece_color(attacker_coords) != self.board.current_move and \
                self.board.grid[attacker_row][attacker_col] in ['p', 'P']:
                return True
        
        # King (to prevent illegal moves)
        for dr, dc in KING_DIRECTIONS:
            attacker_row = king_coords.row + dr
            attacker_col = king_coords.col + dc
            attacker_coords = Coord(attacker_row, attacker_col)

            if not (0 <= attacker_row <= 7 and 0 <= attacker_col <= 7):
                continue

            if self.board._get_piece_color(attacker_coords) != self.board.current_move and \
                  self.board.grid[attacker_row][attacker_col] in ['k', 'K']:
                return True

        return False
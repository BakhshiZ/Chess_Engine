from typing import TYPE_CHECKING
from constants import *

if TYPE_CHECKING:
    from board import Board

class MoveGenerator:

    def __init__(self, board: Board):
        self.board = board
        self.en_passant_target = None

    def get_side_legal_moves(self):
        """
        Add checker for if in check
        """
        legal_moves = []
        for row in range(8):
            for col in range(8):
                coords = (row, col)
                piece = self.board.get_piece_at(coords=coords)

                if piece.color is None or piece.color != self.board.current_move:
                    continue

                if piece.type == "pawn":
                    legal_moves.append(self._get_pawn_moves(coords))
                elif piece.type == "knight":
                    legal_moves.append(self._get_stepping_moves(coords, KNIGHT_DIRECTIONS))
                elif piece.type == "bishop":
                    legal_moves.append(self._get_sliding_moves(coords, BISHOP_DIRECTIONS))
                elif piece.type == "rook":
                    legal_moves.append(self._get_sliding_moves(coords, ROOK_DIRECTIONS))
                elif piece.type == "queen":
                    legal_moves.append(self._get_sliding_moves(coords, QUEEN_DIRECTIONS))
                else:
                    legal_moves.append(self._get_stepping_moves(coords, KING_DIRECTIONS))
                
    def _get_sliding_moves(self, curr_coords: Coords, directions: tuple[Direction,...]) -> list[Move]:
        """
        Function to find all moves for bishop, rook and queen
        """
        legal_moves = []
        curr_piece = self.board.get_piece_at(coords=curr_coords)
        
        for d in directions:
            new_row = curr_coords.row + d.row_offset
            new_col = curr_coords.col + d.col_offset

            while (0 <= new_row <= 7 and 0 <= new_col <= 7):
                target_coords = Coords(row=new_row, col=new_col)
                target_tile = self.board.get_piece_at(coords=target_coords)

                if target_tile.color is None:
                    legal_moves.append(Move(curr_coords, target_coords))
                    
                elif target_tile.color != curr_piece.color:
                    legal_moves.append(Move(
                        start=curr_coords, 
                        end=target_coords,
                        is_capture=True
                        ))
                    break

                else:
                    break
            
                new_row += d.row_offset
                new_col += d.col_offset
        
        return legal_moves
    
    def _get_stepping_moves(self, curr_coords: Coords, directions: tuple[Direction, ...]) -> list[Move]:
        """
        Function to find all moves for knight and king
        """
        legal_moves = []
        curr_piece = self.board.get_piece_at(coords=curr_coords)

        for d in directions:
            new_row = curr_coords.row + d.row_offset
            new_col = curr_coords.col + d.col_offset

            if not (0 <= new_row <= 7 and 0 <= new_col <= 7):
                continue
            
            target_coords = Coords(row=new_row, col=new_col)
            target_tile = self.board.get_piece_at(coords=target_coords)

            if target_tile.color != curr_piece.color:
                legal_moves.append(Move(
                    start=curr_coords,
                    end=target_coords,
                    is_capture=True
                ))

            else:
                continue
        
        return legal_moves
    
    def _get_pawn_moves(self, curr_coords: Coords) -> list[Move]:
        """
        Function to find all moves for pawn
        """
        legal_moves = []
        curr_piece = self.board.get_piece_at(coords=curr_coords)
        starting_row = 6 if curr_piece.color == 'w' else 1
        direction = -1 if curr_piece.color == 'w' else 1
        promotion_row = 0 if curr_piece.color == 'w' else 7

        # Move once
        one_step_row = curr_coords.row + direction
        one_step_coords = Coords(row=one_step_row, col=curr_coords.col)
        one_step_tile = self.board.get_piece_at(coords=one_step_coords)

        if one_step_tile.color is None:
            # Promotion
            if one_step_row == promotion_row:
                for new_type in ["n", "b", "r", "q"]:
                    self._add_promotion_moves(legal_moves, curr_coords, one_step_coords, new_type)
            else:
                legal_moves.append(Move(
                    start=curr_coords, 
                    end=one_step_coords
                    ))

                # Move twice
                if curr_coords.row == starting_row:
                    two_step_row = curr_coords.row + 2 * direction
                    two_step_coords = Coords(row=two_step_row, col=curr_coords.col)
                    two_step_tile = self.board.get_piece_at(two_step_coords)

                    if two_step_tile.color is None:
                        legal_moves.append(Move(
                            start=curr_coords,
                            end=two_step_coords
                        ))

        # Captures
        for col_offset in PAWN_CAPTURE_DIRECTIONS:
            capture_col = curr_coords.col + col_offset
            if not (0 <= capture_col <= 7):
                continue

            capture_coords = Coords(row=one_step_row, col=capture_col)
            capture_tile = self.board.get_piece_at(coords=capture_coords)

            if capture_tile and capture_tile.color != curr_piece.color:
                if one_step_row == promotion_row:
                    for new_type in ["n", "b", "r", "q"]:
                        self._add_promotion_moves(legal_moves, curr_coords, 
                                                capture_coords, new_type, capture_flag=True)
                else:
                    legal_moves.append(Move(
                    start=curr_coords, 
                    end=capture_coords,
                    is_capture=True
                    ))

            # En passant
            checking_coords = Coords(row=curr_coords.row, col=capture_col)

            if checking_coords == self.board.en_passant_coords:
                target_coords = Coords(row=one_step_row, col=capture_col)

                legal_moves.append(Move(
                    start=curr_coords, 
                    end=target_coords,
                    is_en_passant=True
                    ))
                
    def _add_promotion_moves(self, legal_moves: list[Move], curr_coords: Coords, 
                             end_coords: Coords, new_type: PROMOTION_OPTION, capture_flag=False) -> list[Move]:
        legal_moves.append(Move(
            start=curr_coords,
            end=end_coords,
            is_capture=capture_flag,
            is_promotion=True,
            promoted_to=new_type
        ))

    def _king_in_check(self, coords: Coords) -> bool:
        """
        Function to see if after making move king is exposed. Check all sliding squares
        outward from king to see if sliding piece is present and check if knights can attack king
        """
        
        # Checking knight moves
        for n_d in KNIGHT_DIRECTIONS:
            knight_row = coords.row + n_d.row_offset
            knight_col = coords.col + n_d.col_offset
            if not (0 <= knight_row <= 7 and 0 <= knight_col <= 7):
                continue
            knight_coords = Coords(knight_row, knight_col)

            king = self.board.get_piece_at(coords)
            curr_tile = self.board.get_piece_at(knight_coords)
            
            if curr_tile.color == king.color:
                break

            if curr_tile.type is not "knight":
                continue
            return True
        
        # Checking sliding moves
        for r_d in ROOK_DIRECTIONS:
            rook_row = coords.row + r_d.row_offset
            rook_col = coords.col + r_d.col_offset

            while not (0 <= rook_row <= 7 and 0 <= rook_col <= 7):
                rook_coords = Coords(rook_row, rook_col)
                curr_tile = self.board.get_piece_at(rook_coords)

                if curr_tile.color is None:
                    rook_row += r_d.row_offset
                    rook_col += r_d.col_offset

                elif curr_tile.color == king.color:
                    break

                elif curr_tile.type not in ["rook", "queen"]:
                    continue
                
                return True
        
        for b_d in BISHOP_DIRECTIONS:
            bishop_row = coords.row + b_d.row_offset
            bishop_col = coords.col + b_d.col_offset

            while not (0 <= bishop_row <= 7 and 0 <= bishop_col <= 7):
                bishop_coords = Coords(bishop_row, bishop_col)
                curr_tile = self.board.get_piece_at(bishop_coords)

                if curr_tile.color is None:
                    bishop_row += b_d.row_offset
                    bishop_col += b_d.col_offset

                elif curr_tile.color == king.color:
                    break

                elif curr_tile.type not in ["bishop", "queen"]:
                    continue
                
                elif curr_tile.type == "knight":
                    return True

                bishop_row += b_d.row_offset
                bishop_col += b_d.col_offset

        return False
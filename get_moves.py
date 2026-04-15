from typing import TYPE_CHECKING
from constants import *

if TYPE_CHECKING:
    from board import Board

class MoveGenerator:

    def __init__(self, board: Board):
        self.board = board
        self.en_passant_target = None

    def get_all_legal_moves(self):
        pass

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
        one_step_coords = Coords(row=one_step_row, col=curr_coords.cols)
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
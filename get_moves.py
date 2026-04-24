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
        for rank in range(8):
            for file in range(8):
                coords = Coords(rank, file)
                piece = self.board.get_piece_at(coords=coords)

                if piece.color != self.board.current_move:
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
        
        return legal_moves

    def _get_sliding_moves(self, curr_coords: Coords, directions: tuple[Direction,...]) -> list[Move]:
        """
        Function to find all moves for bishop, rook and queen
        """
        legal_moves = []
        curr_piece = self.board.get_piece_at(coords=curr_coords)
        
        for d in directions:
            new_rank = curr_coords.rank + d.rank_offset
            new_file = curr_coords.file + d.file_offset

            while (0 <= new_rank <= 7 and 0 <= new_file <= 7):
                target_coords = Coords(rank=new_rank, file=new_file)
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
            
                new_rank += d.rank_offset
                new_file += d.file_offset
        
        return legal_moves
    
    def _get_stepping_moves(self, curr_coords: Coords, directions: tuple[Direction, ...]) -> list[Move]:
        """
        Function to find all moves for knight and king
        """
        legal_moves = []
        curr_piece = self.board.get_piece_at(coords=curr_coords)

        for d in directions:
            new_rank = curr_coords.rank + d.rank_offset
            new_file = curr_coords.file + d.file_offset

            if not (0 <= new_rank <= 7 and 0 <= new_file <= 7):
                continue
            
            target_coords = Coords(rank=new_rank, file=new_file)
            target_tile = self.board.get_piece_at(coords=target_coords)

            if target_tile.color != curr_piece.color and target_tile.color is not None:
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
        starting_rank = 6 if curr_piece.color == 'w' else 1
        direction = -1 if curr_piece.color == 'w' else 1
        promotion_rank = 0 if curr_piece.color == 'w' else 7

        # Move once
        one_step_rank = curr_coords.rank + direction
        one_step_coords = Coords(rank=one_step_rank, file=curr_coords.file)
        one_step_tile = self.board.get_piece_at(coords=one_step_coords)

        if one_step_tile.color is None:
            # Promotion
            if one_step_rank == promotion_rank:
                for new_type in PROMOTION_PIECE:
                    self._add_promotion_moves(legal_moves, curr_coords, one_step_coords, new_type)
            else:
                legal_moves.append(Move(
                    start=curr_coords, 
                    end=one_step_coords
                    ))

                # Move twice
                if curr_coords.rank == starting_rank:
                    two_step_rank = curr_coords.rank + 2 * direction
                    two_step_coords = Coords(rank=two_step_rank, file=curr_coords.file)
                    two_step_tile = self.board.get_piece_at(two_step_coords)

                    if two_step_tile.color is None:
                        legal_moves.append(Move(
                            start=curr_coords,
                            end=two_step_coords
                        ))

        # Captures
        for file_offset in PAWN_CAPTURE_DIRECTIONS:
            capture_file = curr_coords.file + file_offset
            if not (0 <= capture_file <= 7):
                continue

            capture_coords = Coords(rank=one_step_rank, file=capture_file)
            capture_tile = self.board.get_piece_at(coords=capture_coords)

            if capture_tile is not None and capture_tile.color != curr_piece.color:
                if one_step_rank == promotion_rank:
                    for new_type in PROMOTION_PIECE:
                        self._add_promotion_moves(legal_moves, curr_coords, 
                                                capture_coords, new_type, capture_flag=True)
                else:
                    legal_moves.append(Move(
                    start=curr_coords, 
                    end=capture_coords,
                    is_capture=True
                    ))

            # En passant
            checking_coords = Coords(rank=curr_coords.rank, file=capture_file)

            if checking_coords == self.board.en_passant_coords:
                target_coords = Coords(rank=one_step_rank, file=capture_file)

                legal_moves.append(Move(
                    start=curr_coords, 
                    end=target_coords,
                    is_en_passant=True
                    ))
        return legal_moves

    def _add_promotion_moves(self, legal_moves: list[Move], curr_coords: Coords, 
                             end_coords: Coords, new_type: PIECE_TYPE, capture_flag=False) -> list[Move]:
        legal_moves.append(Move(
            start=curr_coords,
            end=end_coords,
            is_capture=capture_flag,
            is_promotion=True,
            promoted_to=new_type
        ))
        return legal_moves

    def _king_in_check(self, king_coords: Coords) -> bool:
        """
        Function to see if after making move king is exposed. Check all sliding squares
        outward from king to see if sliding piece is present and check if knights can attack king
        """
        king = self.board.get_piece_at(king_coords)

        # Checking knight moves
        for n_d in KNIGHT_DIRECTIONS:
            possible_knight_rank = king_coords.rank + n_d.rank_offset
            possible_knight_file = king_coords.file + n_d.file_offset
            if not (0 <= possible_knight_rank <= 7 and 0 <= possible_knight_file <= 7):
                continue
            possible_knight_coords = Coords(possible_knight_rank, possible_knight_file)

            curr_tile = self.board.get_piece_at(possible_knight_coords)
            
            if curr_tile.color == king.color:
                continue

            if curr_tile.type != "knight":
                continue

            return True
        
        # Checking sliding moves
        for r_d in ROOK_DIRECTIONS:
            possible_rook_rank = king_coords.rank + r_d.rank_offset
            possible_rook_file = king_coords.file + r_d.file_offset

            while (0 <= possible_rook_rank <= 7 and 0 <= possible_rook_file <= 7):
                possible_rook_coords = Coords(possible_rook_rank, possible_rook_file)
                curr_tile = self.board.get_piece_at(possible_rook_coords)

                if curr_tile.color is None:
                    possible_rook_rank += r_d.rank_offset
                    possible_rook_file += r_d.file_offset
                    continue

                elif curr_tile.color == king.color:
                    break

                elif curr_tile.type not in ["rook", "queen"]:
                    break
                
                return True
        
        for b_d in BISHOP_DIRECTIONS:
            possible_bishop_rank = king_coords.rank + b_d.rank_offset
            possible_bishop_file = king_coords.file + b_d.file_offset

            while (0 <= possible_bishop_rank <= 7 and 0 <= possible_bishop_file <= 7):
                possible_bishop_coords = Coords(possible_bishop_rank, possible_bishop_file)
                curr_tile = self.board.get_piece_at(possible_bishop_coords)

                if curr_tile.color is None:
                    possible_bishop_rank += b_d.rank_offset
                    possible_bishop_file += b_d.file_offset
                    continue

                elif curr_tile.color == king.color:
                    break

                elif curr_tile.type not in ["bishop", "queen"]:
                    break
                
                return True

        # Checking pawn diagonals
        possible_pawn_rank = king_coords.rank - 1 if king.color == 'w' else king_coords.rank + 1
        if (0 <= possible_pawn_rank <= 7):
            for p_d in PAWN_CAPTURE_DIRECTIONS:
                possible_pawn_file = king_coords.file + p_d
                if not (0 <= possible_pawn_file <= 7):
                    continue

                possible_pawn_coords = Coords(possible_pawn_rank, possible_pawn_file)
                curr_tile = self.board.get_piece_at(possible_pawn_coords)

                if curr_tile.color != king.color and curr_tile.type == "pawn":
                    return True

        # Checking king squares
        for k_d in KING_DIRECTIONS:
            possible_king_rank = king_coords.rank + k_d.rank_offset
            possible_king_file = king_coords.file + k_d.file_offset

            if not (0 <= possible_king_rank <= 7 and 0 <= possible_king_file <= 7):
                continue
            
            possible_king_coords = Coords(possible_king_rank, possible_king_file)
            curr_tile = self.board.get_piece_at(possible_king_coords)

            if curr_tile.color != king.color and curr_tile.type == "king":
                return True
            
        return False
from get_moves import MoveGenerator
from constants import *
from board import Board

board = Board()
move_generator = MoveGenerator(board)

queen_moves = move_generator._get_stepping_moves(old_coords=Coord(7, 4), piece_type='k')
board.make_move(queen_moves[0])
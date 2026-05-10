from get_moves import MoveGenerator
from constants import *
from board import Board

board = Board()
move_generator = MoveGenerator(board)
old_coord = Coord(6, 4)
new_coord = Coord(4, 4)

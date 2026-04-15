class Board:
    """
    Class for handling the chess board. Lowercase pieces are black pieces
    while uppercase pieces are white ones
    """
    def __init__(self):
        grid = [["r", "n", "b", "k", "q", "b", "n", "r"],
                ["p", "p", "p", "p", "p", "p", "p", "p"],
                [None, None, None, None, None, None, None, None],
                [None, None, None, None, None, None, None, None],
                [None, None, None, None, None, None, None, None]
                [None, None, None, None, None, None, None, None],
                ["P", "P", "P", "P", "P", "P", "P", "P"],
                ["R", "N", "B", "K", "Q", "B", "N", "R"]]

        # White Kingside, White Queenside, Black Kingside, Black Queenside
        can_castle = [True, True, True, True]
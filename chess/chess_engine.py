"""
This class responsible for storing all the information about the current state of a chess game. It also will be
responsible for determining the valid moves at the current state. It will also log all the moves.
"""

LEFT_SIDE_OF_BOARD = 0
RIGHT_SIDE_OF_BOARD = 7


class GameState:
    def __init__(self):
        # board 8x8 2d list, each element has 2 char
        # the first char represent the color, the second represent the type
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
        ]
        self.white_to_move = True
        self.move_log = []
        self.en_passant_possible = ()
        self.move_functions = {'P': self.get_pawn_moves, 'R': self.get_rook_moves, 'N': self.get_knight_moves,
                               'B': self.get_bishop_moves, 'Q': self.get_queen_moves, 'K': self.get_king_moves}

    def make_move(self, move):
        self.board[move.start_row][move.start_column] = "--"
        self.board[move.end_row][move.end_column] = move.piece_moved

        # Pawn Promotion
        if move.is_pawn_promotion:
            self.board[move.end_row][move.end_column] = move.piece_moved[0] + 'Q'  # Always promote to Queen

        # En Passant Capture
        if move.is_en_passant_move:
            self.board[move.start_row][move.end_column] = "--"  # Captures the pawn on the adjacent row

        # Update en_passant_possible
        if move.piece_moved[1] == 'P' and abs(move.start_row - move.end_row) == 2:
            # Pawn moved two squares, set the square behind it as possible
            self.en_passant_possible = ((move.start_row + move.end_row) // 2, move.start_column)
        else:
            self.en_passant_possible = ()

        self.move_log.append(move)  # history
        self.white_to_move = not self.white_to_move  # switch

    def undo_move(self):
        if len(self.move_log) != 0:
            move = self.move_log.pop()

            # 1. Restore the piece that moved to its start square
            self.board[move.start_row][move.start_column] = move.piece_moved

            # 2. Restore the piece that was captured (or '--' for a regular move) to the end square
            self.board[move.end_row][move.end_column] = move.piece_captured

            # 3. Handle the En Passant exception
            if move.is_en_passant_move:
                self.board[move.end_row][move.end_column] = "--"  # Make the landing square empty
                # Put the captured pawn back on its correct adjacent square
                self.board[move.start_row][move.end_column] = move.piece_captured

            # Undo a two-square advance (since this resets the en_passant_possible state for the *next* move)
            if move.piece_moved[1] == 'P' and abs(move.start_row - move.end_row) == 2:
                self.en_passant_possible = ()

            self.white_to_move = not self.white_to_move

    # moves considering checks
    def get_valid_moves(self):
        # Save current en_passant_possible to restore it later
        temp_en_passant_possible = self.en_passant_possible  # Create a temporary copy

        # Returns all moves for now
        moves = self.get_all_possible_moves()

        self.en_passant_possible = temp_en_passant_possible  # Restore the value
        return moves

    def get_all_possible_moves(self):
        moves = []
        for row in range(len(self.board)):
            for column in range(len(self.board[row])):
                turn = self.board[row][column][0]
                if (turn == 'w' and self.white_to_move) or (turn == 'b' and not self.white_to_move):
                    piece = self.board[row][column][1]
                    self.move_functions[piece](row, column, moves)
        return moves

    def get_pawn_moves(self, row, column, moves):
        # white pawn moves only on top, decrement rows
        if self.white_to_move:
            if self.board[row - 1][column] == '--': # nothing in front of the piece
                moves.append(Move((row, column), (row - 1, column), self.board))
                if row == 6 and self.board[row - 2][column] == '--': # first move
                    moves.append(Move((row, column), (row - 2, column), self.board))
            if column - 1 >= LEFT_SIDE_OF_BOARD:  # to the left
                if self.board[row - 1][column - 1][0] == 'b':  # enemy piece to capture
                    moves.append(Move((row, column), (row - 1, column - 1), self.board))
                elif (row - 1, column - 1) == self.en_passant_possible:  # En Passant capture
                    moves.append(Move((row, column), (row - 1, column - 1), self.board, is_en_passant_move=True))  # Pass flag
            if column + 1 <= RIGHT_SIDE_OF_BOARD:  # to the right
                if self.board[row - 1][column + 1][0] == 'b':
                    moves.append(Move((row, column), (row - 1, column + 1), self.board))
                elif (row - 1, column + 1) == self.en_passant_possible:  # En Passant capture
                    moves.append(Move((row, column), (row - 1, column + 1), self.board, is_en_passant_move=True))  # Pass flag
        else:
            if self.board[row + 1][column] == '--':
                moves.append(Move((row, column), (row + 1, column), self.board))
                if row == 1 and self.board[row + 2][column] == '--': # only for first move
                    moves.append(Move((row, column), (row + 2, column), self.board))
            if column - 1 >= LEFT_SIDE_OF_BOARD:  # to the left
                if self.board[row + 1][column - 1][0] == 'w':  # enemy piece to capture
                    moves.append(Move((row, column), (row + 1, column - 1), self.board))
                elif (row + 1, column - 1) == self.en_passant_possible:  # En Passant capture
                    moves.append(Move((row, column), (row + 1, column - 1), self.board, is_en_passant_move=True))  # Pass flag
            if column + 1 <= RIGHT_SIDE_OF_BOARD:  # to the right
                if self.board[row + 1][column + 1][0] == 'w':
                    moves.append(Move((row, column), (row + 1, column + 1), self.board))
                elif (row + 1, column + 1) == self.en_passant_possible:  # En Passant capture
                    moves.append(Move((row, column), (row + 1, column + 1), self.board, is_en_passant_move=True))  # Pass flag

    def get_rook_moves(self, row, column, moves):
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1)) # up, left, down, right possible directions for rook
        enemy_color = 'b' if self.white_to_move else 'w'
        for direction in directions:
            for i in range(1, 8):
                end_row = row + i * direction[0]
                end_column = column + i * direction[1]
                if LEFT_SIDE_OF_BOARD <= end_row <= RIGHT_SIDE_OF_BOARD and LEFT_SIDE_OF_BOARD <= end_column <= RIGHT_SIDE_OF_BOARD:
                    end_piece = self.board[end_row][end_column]
                    if end_piece == '--':
                        moves.append(Move((row, column), (end_row, end_column), self.board))
                    elif end_piece[0] == enemy_color:
                        moves.append(Move((row, column), (end_row, end_column), self.board))
                        break
                    else:
                        break
                else:
                    break

    def get_knight_moves(self, row, column, moves):
        knight_moves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        ally_color = 'w' if self.white_to_move else 'b'
        for move in knight_moves:
            end_row = row + move[0]
            end_column = column + move[1]
            if LEFT_SIDE_OF_BOARD <= end_row <= RIGHT_SIDE_OF_BOARD and LEFT_SIDE_OF_BOARD <= end_column <= RIGHT_SIDE_OF_BOARD:
                end_piece = self.board[end_row][end_column]
                if end_piece[0] != ally_color: # only enemy or empty square
                    moves.append(Move((row, column), (end_row, end_column), self.board))

    def get_bishop_moves(self, row, column, moves):
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1)) # diagonal
        enemy_color = 'b' if self.white_to_move else 'w'
        for direction in directions:
            for i in range(1, 8): # bishop can move max 7 squares
                end_row = row + i * direction[0]
                end_column = column + i * direction[1]
                if LEFT_SIDE_OF_BOARD <= end_row <= RIGHT_SIDE_OF_BOARD and LEFT_SIDE_OF_BOARD <= end_column <= RIGHT_SIDE_OF_BOARD:
                    end_piece = self.board[end_row][end_column]
                    if end_piece == '--':
                        moves.append(Move((row, column), (end_row, end_column), self.board))
                    elif end_piece[0] == enemy_color:
                        moves.append(Move((row, column), (end_row, end_column), self.board))
                        break
                    else:
                        break
                else:
                    break

    def get_queen_moves(self, row, column, moves):
        pass

    def get_king_moves(self, row, column, moves):
        pass


class Move:
    # X
    ranks_to_rows = {"1": 7, "2": 6, "3": 5, "4": 4,
                     "5": 3, "6": 2, "7": 1, "8": 0}
    rows_to_ranks = {v: k for k, v in ranks_to_rows.items()}
    # Y
    files_to_columns = {"a": 0, "b": 1, "c": 2, "d": 3,
                        "e": 4, "f": 5, "g": 6, "h": 7}
    columns_to_files = {v: k for k, v in files_to_columns.items()}

    def __init__(self, start_square, end_square, board, is_en_passant_move=False):
        self.start_row = start_square[0]
        self.start_column = start_square[1]
        self.end_row = end_square[0]
        self.end_column = end_square[1]
        self.piece_moved = board[self.start_row][self.start_column]
        self.piece_captured = board[self.end_row][self.end_column]

        # Determine if it's a pawn promotion move
        self.is_pawn_promotion = (self.piece_moved == 'wP' and self.end_row == 0) or \
                                 (self.piece_moved == 'bP' and self.end_row == 7)

        # En Passant logic: manually set captured piece if EP is true
        self.is_en_passant_move = is_en_passant_move
        if self.is_en_passant_move:
            self.piece_captured = 'wP' if self.piece_moved[0] == 'b' else 'bP'
        else:
            self.piece_captured = board[self.end_row][self.end_column]

        self.move_id = self.start_row * 1000 + self.start_column * 100 + self.end_row * 10 + self.end_column
        # print(self.move_id)

    # override equals
    def __eq__(self, other):
        if isinstance(other, Move):
            return self.move_id == other.move_id
        return False

    def get_chess_notation(self):
        return self.get_rank_file(self.start_row, self.start_column) + self.get_rank_file(self.end_row, self.end_column)

    def get_rank_file(self, row, column):
        return self.columns_to_files[column] + self.rows_to_ranks[row]

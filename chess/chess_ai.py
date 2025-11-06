import random


PIECE_SCORE = {"K": 0, "Q": 900, "R": 500, "B": 330, "N": 320, "P": 100, "--": 0}
CHECKMATE = 10000000  # A very large number
STALEMATE = 0
SEARCH_DEPTH = 3  # You can adjust this for search depth

next_move = None

# Pawns are usually valued more in the center and closer to promotion
PAWN_SCORES = [
    [0, 0, 0, 0, 0, 0, 0, 0],
    [50, 50, 50, 50, 50, 50, 50, 50],
    [10, 10, 20, 30, 30, 20, 10, 10],
    [5, 5, 10, 25, 25, 10, 5, 5],
    [0, 0, 0, 20, 20, 0, 0, 0],
    [5, -5, -10, 0, 0, -10, -5, 5],
    [5, 10, 10, -20, -20, 10, 10, 5],
    [0, 0, 0, 0, 0, 0, 0, 0]
]

# Knights are best in the center and poor on the edges
KNIGHT_SCORES = [
    [-50, -40, -30, -30, -30, -30, -40, -50],
    [-40, -20, 0, 0, 0, 0, -20, -40],
    [-30, 0, 10, 15, 15, 10, 0, -30],
    [-30, 5, 15, 20, 20, 15, 5, -30],
    [-30, 0, 15, 20, 20, 15, 0, -30],
    [-30, 5, 10, 15, 15, 10, 5, -30],
    [-40, -20, 0, 5, 5, 0, -20, -40],
    [-50, -40, -30, -30, -30, -30, -40, -50]
]

# Bishops are generally better along diagonals, especially when the center is open
BISHOP_SCORES = [
    [-20, -10, -10, -10, -10, -10, -10, -20],
    [-10, 0, 0, 0, 0, 0, 0, -10],
    [-10, 0, 5, 10, 10, 5, 0, -10],
    [-10, 5, 5, 10, 10, 5, 5, -10],
    [-10, 0, 10, 10, 10, 10, 0, -10],
    [-10, 10, 10, 10, 10, 10, 10, -10],
    [-10, 5, 0, 0, 0, 0, 5, -10],
    [-20, -10, -10, -10, -10, -10, -10, -20]
]

# Rooks prefer open files and are strong on the back rank late game
ROOK_SCORES = [
    [0, 0, 0, 5, 5, 0, 0, 0],
    [-5, 0, 0, 0, 0, 0, 0, -5],
    [-5, 0, 0, 0, 0, 0, 0, -5],
    [-5, 0, 0, 0, 0, 0, 0, -5],
    [-5, 0, 0, 0, 0, 0, 0, -5],
    [-5, 0, 0, 0, 0, 0, 0, -5],
    [5, 10, 10, 10, 10, 10, 10, 5], # Seventh rank is valuable
    [0, 0, 0, 0, 0, 0, 0, 0]
]

# Queens are centralized but generally have less positional value than minor pieces
QUEEN_SCORES = [
    [-20, -10, -10, -5, -5, -10, -10, -20],
    [-10, 0, 0, 0, 0, 0, 0, -10],
    [-10, 0, 5, 5, 5, 5, 0, -10],
    [-5, 0, 5, 5, 5, 5, 0, -5],
    [0, 0, 5, 5, 5, 5, 0, -5],
    [-10, 5, 5, 5, 5, 5, 0, -10],
    [-10, 0, 5, 0, 0, 0, 0, -10],
    [-20, -10, -10, -5, -5, -10, -10, -20]
]

# Kings should be safe early game and centralized late game (requires advanced evaluation)
# This table prioritizes safety (Tuck the King in the corner)
KING_SCORES = [
    [-30, -40, -40, -50, -50, -40, -40, -30],
    [-30, -40, -40, -50, -50, -40, -40, -30],
    [-30, -40, -40, -50, -50, -40, -40, -30],
    [-30, -40, -40, -50, -50, -40, -40, -30],
    [-20, -30, -30, -40, -40, -30, -30, -20],
    [-10, -20, -20, -20, -20, -20, -20, -10],
    [20, 20, 0, 0, 0, 0, 20, 20],
    [20, 30, 10, 0, 0, 10, 30, 20]
]

# Mapping piece types to their scores
piece_to_score = {
    'P': PAWN_SCORES,
    'N': KNIGHT_SCORES,
    'B': BISHOP_SCORES,
    'R': ROOK_SCORES,
    'Q': QUEEN_SCORES,
    'K': KING_SCORES,
}



def score_board(gs):
    """
    Positive score is good for white, negative is good for black.
    This function only calculates the material advantage.
    """
    if gs.checkmate:
        # Checkmate value must be returned from the perspective of the current player
        return CHECKMATE if not gs.white_to_move else -CHECKMATE
    if gs.stalemate:
        return STALEMATE

    score = 0
    for row in range(8):
        for col in range(8):
            piece = gs.board[row][col]
            if piece != '--':
                # Base material score
                score += PIECE_SCORE[piece[1]] if piece[0] == 'w' else -PIECE_SCORE[piece[1]]

                # Positional score
                if piece[1] == 'N':
                    # If white, use the table directly
                    if piece[0] == 'w':
                        score += KNIGHT_SCORES[row][col]
                    # If black, flip the table vertically (row 7 becomes row 0)
                    elif piece[0] == 'b':
                        score -= KNIGHT_SCORES[7 - row][col]
    return score


def find_best_move(gs, valid_moves):
    """
    Top-level function to start the search and return the best move.
    """
    global next_move
    next_move = None

    # Initiate the Minimax search with initial alpha/beta boundaries
    find_minimax_move(gs, valid_moves, SEARCH_DEPTH, -CHECKMATE, CHECKMATE, gs.white_to_move)
    return next_move


def find_minimax_move(gs, valid_moves, depth, alpha, beta, white_to_move):
    """
    The recursive minimax implementation with Alpha-Beta Pruning (Part 13).
    The function always returns the score from the perspective of the maximizing player (White).
    """
    global next_move

    # Base case: When depth is 0 or game is over
    if depth == 0 or gs.checkmate or gs.stalemate:
        # The score_board already returns the material score from White's perspective (positive=good for white)
        return score_board(gs)

    if white_to_move:  # Maximizing player (White)
        max_score = -CHECKMATE
        for move in valid_moves:
            gs.make_move(move)
            next_moves = gs.get_valid_moves()

            # Recursive call: The next turn is Black's (minimizing)
            score = find_minimax_move(gs, next_moves, depth - 1, alpha, beta, False)
            gs.undo_move()

            if score > max_score:
                max_score = score
                if depth == SEARCH_DEPTH:  # Only update the global move at the top search level
                    next_move = move

            # Alpha Pruning
            alpha = max(alpha, max_score)
            if beta <= alpha:
                break
        return max_score

    else:  # Minimizing player (Black)
        min_score = CHECKMATE
        for move in valid_moves:
            gs.make_move(move)
            next_moves = gs.get_valid_moves()

            # Recursive call: The next turn is White's (maximizing)
            score = find_minimax_move(gs, next_moves, depth - 1, alpha, beta, True)
            gs.undo_move()

            if score < min_score:
                min_score = score
                if depth == SEARCH_DEPTH:  # Only update the global move at the top search level
                    next_move = move

            # Beta Pruning
            beta = min(beta, min_score)
            if beta <= alpha:
                break
        return min_score

def find_random_move(valid_moves):
    """
    Picks a random valid move from the list.
    """
    return random.choice(valid_moves)
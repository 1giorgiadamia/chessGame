"""
This class responsible for handling user input and displaying the current game state.
"""
import pygame as p
from chess import chess_engine
from chess import chess_ai

WIDTH = HEIGHT = 512
DIMENSION = 8  # 8x8 board
SQUARE_SIZE = WIDTH // DIMENSION
MAX_FPS = 15  # for animation
IMAGES = {}


# Init a global dict for images for storing them, it will be call one time
def init_images():
    pieces = ["wR", "wN", "wB", "wQ", "wK", "wP", "bR", "bN", "bB", "bQ", "bK", "bP"]
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("chess/images/" + piece + ".png"), (SQUARE_SIZE, SQUARE_SIZE))


# The driver that handle user input and updating display
def chess_game():
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("White"))
    game_state = chess_engine.GameState()
    valid_moves = game_state.get_valid_moves()
    move_made = False
    init_images()
    running = True

    player_one = True  # White player is human
    player_two = False  # Black player is AI

    square_selected = ()  # tracking the last click of the user (row, column)
    player_clicks = []  # tracking player clicks, two tuples [(start_row, start_column), (end_row, end_column)]

    while running:
        human_turn = (game_state.white_to_move and player_one) or \
                     (not game_state.white_to_move and player_two)

        for event in p.event.get():
            if event.type == p.QUIT:
                running = False
            elif event.type == p.MOUSEBUTTONDOWN:
                if human_turn:
                    location = p.mouse.get_pos()  # (x, y) location of the mouse
                    column = location[0] // SQUARE_SIZE
                    row = location[1] // SQUARE_SIZE
                    if square_selected == (row, column):
                        # deselecting
                        square_selected = ()
                        player_clicks = []
                    else:
                        square_selected = (row, column)
                        player_clicks.append(square_selected)  # append for 1st and 2nd clicks
                    if len(player_clicks) == 2:  # after 2nd click
                        move = chess_engine.Move(player_clicks[0], player_clicks[1], game_state.board)
                        print(move.get_chess_notation())
                        for valid_move in valid_moves:
                            if move == valid_move:
                                game_state.make_move(valid_move)  # Use the move from valid_moves, which has the flag set
                                move_made = True
                                break
                        # reset user clicks
                        square_selected = ()
                        player_clicks = []
            elif event.type == p.KEYDOWN:
                # undo when the 'z' is pressed
                if event.key == p.K_z:
                    game_state.undo_move()
                    move_made = True
            if not human_turn and not game_state.checkmate and not game_state.stalemate:
                ai_move = chess_ai.find_best_move(game_state, valid_moves)

                if ai_move is None:
                    # If no move is found, it means the game is technically over, it's a safety check
                    ai_move = chess_ai.find_random_move(valid_moves)
                    print("AI could not find an optimal move. Makes a random move.")
                game_state.make_move(ai_move)
                move_made = True

        if move_made:
            valid_moves = game_state.get_valid_moves()
            move_made = False

        draw_game_state(screen, game_state)
        clock.tick(MAX_FPS)
        p.display.flip()


# Responsible for all display on a current game state
def draw_game_state(screen, game_state):
    draw_board(screen)  # draw the squares
    draw_pieces(screen, game_state.board)  # draw the pieces on top of the board


# Top left square is always white
def draw_board(screen):
    colors = [p.Color("bisque"), p.Color("chocolate")]
    for row in range(DIMENSION):
        for column in range(DIMENSION):
            color = colors[((row + column) % 2)]
            p.draw.rect(screen, color, p.Rect(column * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))


def draw_pieces(screen, board):
    for row in range(DIMENSION):
        for column in range(DIMENSION):
            piece = board[row][column]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(column * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

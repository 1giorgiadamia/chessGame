"""
This class responsible for handling user input and displaying the current game state.
"""
import pygame as p
from chess import chess_engine

WIDTH = HEIGHT = 512
DIMENSION = 8  # 8x8 board
SQUARE_SIZE = WIDTH // DIMENSION
MAX_FPS = 15  # for amination
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
    init_images()
    running = True
    square_selected = () # tracking the last click of the user (row, column)
    player_clicks = [] # tracking player clicks, two tuples [(start_row, start_column), (end_row, end_column)]
    while running:
        for event in p.event.get():
            if event.type == p.QUIT:
                running = False
            elif event.type == p.MOUSEBUTTONDOWN:
                location = p.mouse.get_pos() # (x, y) location of the mouse
                column = location[0] // SQUARE_SIZE
                row = location[1] // SQUARE_SIZE
                if square_selected == (row, column):
                    # deselecting
                    square_selected = ()
                    player_clicks = []
                else:
                    square_selected = (row, column)
                    player_clicks.append(square_selected) # append for 1st and 2nd clicks
                if len(player_clicks) == 2: # after 2nd click
                    move = chess_engine.Move(player_clicks[0], player_clicks[1], game_state.board)
                    print(move.get_chess_notation())
                    game_state.make_move(move)
                    # reset user clicks
                    square_selected = ()
                    player_clicks = []

        draw_game_state(screen, game_state)
        clock.tick(MAX_FPS)
        p.display.flip()


# Responsible for all display on a current game state
def draw_game_state(screen, game_state):
    draw_board(screen)  # draw the squares
    draw_pieces(screen, game_state.board)  # draw the pieces on top of the board


# Top left square is always white
def draw_board(screen):
    colors = [p.Color("White"), p.Color("Grey")]
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

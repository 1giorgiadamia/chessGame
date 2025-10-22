"""
This class responsible for handling user input and displaying the current game state.
"""
import pygame
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
    while running:
        for event in p.event.get():
            if event.type == p.QUIT:
                running = False
        draw_game_state(screen, game_state)
        clock.tick(MAX_FPS)
        pygame.display.flip()


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

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
    animate = False
    game_over = False

    while running:
        human_turn = (game_state.white_to_move and player_one) or \
                     (not game_state.white_to_move and player_two)

        for event in p.event.get():
            if event.type == p.QUIT:
                running = False
            elif event.type == p.MOUSEBUTTONDOWN:
                if human_turn and not game_over:
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
                                animate = True
                                # reset user clicks
                                square_selected = ()
                                player_clicks = []
                        if not move_made:
                            player_clicks = [square_selected]
            elif event.type == p.KEYDOWN:
                # undo when the 'z' is pressed
                if event.key == p.K_z:
                    game_state.undo_move()
                    move_made = True
                    animate = False
                if event.key == p.K_r: # reset when 'r' pressed
                    game_state = chess_engine.GameState()
                    valid_moves = game_state.get_valid_moves()
                    square_selected = ()
                    player_clicks = []
                    move_made = False
                    animate = False
        if not human_turn and not game_state.checkmate and not game_state.stalemate:
            ai_move = chess_ai.find_best_move(game_state, valid_moves)

            if ai_move is None:
                # If no move is found, it means the game is technically over, it's a safety check
                ai_move = chess_ai.find_random_move(valid_moves)
                print("AI could not find an optimal move. Makes a random move.")
            game_state.make_move(ai_move)
            move_made = True

        if move_made:
            if animate:
                animate_move(game_state.move_log[-1], screen, game_state.board, clock)
            valid_moves = game_state.get_valid_moves()
            move_made = False
            animate = False

        draw_game_state(screen, game_state, valid_moves, square_selected)
        if game_state.checkmate:
            game_over = True
            if game_state.white_to_move:
                draw_text(screen, 'Black win')
            else:
                draw_text(screen, 'White win')
        elif game_state.stalemate:
            game_over = True
            draw_text(screen, 'Stalemate')
        clock.tick(MAX_FPS)
        p.display.flip()

def highlight_squares(screen, game_state, valid_moves, square_selected):
    if square_selected != (): # at least 1 click
        row, column = square_selected
        if game_state.board[row][column][0] == ('w' if game_state.white_to_move else 'b'): # the square can be selected
            square = p.Surface((SQUARE_SIZE, SQUARE_SIZE))
            square.set_alpha(100)
            # selected square
            square.fill(p.Color("blue"))
            screen.blit(square, (column * SQUARE_SIZE, row * SQUARE_SIZE))
            # valid moves of piece
            square.fill(p.Color("green"))
            for move in valid_moves:
                if move.start_row == row and move.start_column == column:
                    screen.blit(square, (move.end_column * SQUARE_SIZE, move.end_row * SQUARE_SIZE))


# Responsible for all display on a current game state
def draw_game_state(screen, game_state, valid_moves, square_selected):
    draw_board(screen)  # draw the squares
    highlight_squares(screen, game_state, valid_moves, square_selected)
    draw_pieces(screen, game_state.board)  # draw the pieces on top of the board


# Top left square is always white
def draw_board(screen):
    global colors
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

def animate_move(move, screen, board, clock):
    global colors
    draw_row = move.end_row - move.start_row
    draw_column = move.end_column - move.start_column
    frames_per_square = 10 # frames to move one square
    frame_count = (abs(draw_row) + abs(draw_column)) * frames_per_square
    for frame in range(frame_count + 1):
        r, c = (move.start_row + draw_row * frame / frame_count, move.start_column + draw_column * frame / frame_count)
        draw_board(screen)
        draw_pieces(screen, board)
        color = colors[(move.end_row + move.end_column) % 2]
        end_square = p.Rect(move.end_column * SQUARE_SIZE, move.end_row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
        p.draw.rect(screen, color, end_square)
        if move.piece_captured != '--':
            screen.blit(IMAGES[move.piece_captured], end_square)
        screen.blit(IMAGES[move.piece_moved], p.Rect(c*SQUARE_SIZE, r*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
        p.display.flip()
        clock.tick(60)

def draw_text(screen, text):
    font = p.font.SysFont("Helvitca", 32, True, False)
    text_object = font.render(text, 0, p.Color('Gray'))
    text_location = p.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH/2 - text_object.get_width()/2, HEIGHT/2 - text_object.get_height()/2)
    screen.blit(text_object, text_location)
    text_object = font.render(text, 0, p.Color('Black'))
    screen.blit(text_object, text_location.move(2, 2))
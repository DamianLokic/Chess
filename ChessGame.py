import pygame
import GameState
import EnemyAI

# Ustawienia okna gry
BOARD_WIDTH = 800
BOARD_HEIGHT = 800
move_log_panel_width = 300
move_log_panel_height = 800
Dimensions = 8
pygame.display.set_caption("Szachy")
Max_FPS = 60
Images = {}

# Kolory
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_SQUARE = (240, 217, 181)
DARK_SQUARE = (181, 136, 99)

# Rozmiar pól na planszy
SQUARE_SIZE = BOARD_WIDTH // 8


def load_pieces():
    pieces = {"wp", "wR", "wN", "wB", "wQ", "wK", "bp", "bR", "bN", "bB", "bQ", "bK"}
    for piece in pieces:
        Images[piece] = pygame.transform.scale(pygame.image.load('Szachy/' + piece + '.png'),
                                               (SQUARE_SIZE, SQUARE_SIZE))


def main():
    pygame.init()
    screen = pygame.display.set_mode((BOARD_WIDTH + move_log_panel_width, BOARD_HEIGHT))
    clock = pygame.time.Clock()
    gs = GameState.GameState()
    valid_moves = gs.move_validation()
    load_pieces()
    moveLogFont = pygame.font.SysFont('Helvetica', 20, False, False)
    animate = False
    move_made = False
    running = True
    game_over = False
    player_one = True
    playerTwo = True
    selected_square = ()
    player_clicks = []
    while running:
        human_turn = (gs.white_to_move and player_one) or (not gs.white_to_move and playerTwo)
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False

            elif e.type == pygame.MOUSEBUTTONDOWN:
                if not game_over and human_turn:
                    pos = pygame.mouse.get_pos()
                    col = pos[0] // SQUARE_SIZE
                    row = pos[1] // SQUARE_SIZE
                    if selected_square == (row, col) or col >= 8:
                        selected_square = ()
                        player_clicks = []
                    else:
                        selected_square = (row, col)
                        player_clicks.append(selected_square)
                    if len(player_clicks) == 2:
                        move = GameState.Move(player_clicks[0], player_clicks[1], gs.board)
                        for i in range(len(valid_moves)):
                            if move == valid_moves[i]:
                                gs.make_move(valid_moves[i])
                                move_made = True
                                animate = True
                                selected_square = ()
                                player_clicks = []
                        if not move_made:
                            player_clicks = [selected_square]

            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_z:
                    gs.undo_move()
                    move_made = True
                    animate = False
                    game_over = False
                if e.key == pygame.K_r:
                    gs = GameState.GameState()
                    valid_moves = gs.move_validation()
                    selected_square = ()
                    player_clicks = []
                    move_made = False
                    animate = False
                    game_over = False

        if not game_over and not human_turn:
            AI = EnemyAI.find_best_move(gs, valid_moves)
            if AI is None:
                AI = EnemyAI.find_random_move(valid_moves)
            gs.make_move(AI)
            move_made = True
            animate = True

        if move_made:
            if animate:
                animation(gs.move_log[-1], screen, gs.board, clock)
            valid_moves = gs.move_validation()
            move_made = False
            animate = False

        draw_Game_State(screen, gs, valid_moves, selected_square, moveLogFont)

        if gs.checkmate:
            game_over = True
            if gs.white_to_move:
                endgame_text(screen, 'Black wins by Checkmate')
            else:
                endgame_text(screen, 'White wins by Checkmate')
        elif gs.stalemate:
            game_over = True
            endgame_text(screen, 'Stalemate')
        clock.tick(Max_FPS)
        pygame.display.flip()


def highlight(screen, gs, valid_moves, selected_square):
    if selected_square != ():
        r, c = selected_square
        if gs.board[r][c][0] == ('w' if gs.white_to_move else 'b'):
            s = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE))
            s.set_alpha(100)
            s.fill(pygame.Color('green'))
            screen.blit(s, (c * SQUARE_SIZE, r * SQUARE_SIZE))
            s.fill(pygame.Color('blue'))
            for move in valid_moves:
                if move.start_row == r and move.start_col == c:
                    screen.blit(s, (SQUARE_SIZE * move.end_col, SQUARE_SIZE * move.end_row))
                    pygame.draw.circle(screen, pygame.Color('white'),
                                       (SQUARE_SIZE * move.end_col + SQUARE_SIZE // 2,
                                        SQUARE_SIZE * move.end_row + SQUARE_SIZE // 2),
                                       SQUARE_SIZE // 8)


def draw_Game_State(screen, gs, valid_moves, selected_square, moveLogFont):
    draw_board(screen)
    highlight(screen, gs, valid_moves, selected_square)
    draw_pieces(screen, gs.board)
    draw_move_log(screen, gs, moveLogFont)


def draw_board(screen):
    global colors
    colors = [pygame.Color("white"), pygame.Color("gray")]
    for row in range(Dimensions):
        for col in range(Dimensions):
            color = colors[((row + col) % 2)]
            pygame.draw.rect(screen, color,
                             pygame.Rect(col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))


def draw_pieces(screen, board):
    for row in range(Dimensions):
        for col in range(Dimensions):
            piece = board[row][col]
            if piece != '--':
                screen.blit(Images[piece],
                            pygame.Rect(col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))


def draw_move_log(screen, gs, font):
    move_log_rect = pygame.Rect(BOARD_WIDTH, 0, move_log_panel_width, move_log_panel_height)
    pygame.draw.rect(screen, pygame.Color('gray'), move_log_rect)
    moveLog = gs.move_log
    moveTexts = []
    for i in range(0, len(moveLog), 2):
        moveString = str(i//2 + 1) + ". " + moveLog[i].chess_notation() + " "
        if i + 1 < len(moveLog):
            moveString += moveLog[i+1].chess_notation()
        moveTexts.append(moveString)
    movesPerRow = 3
    padding = 5
    lineSpacing = 2
    textY = padding
    for t in range(0, len(moveTexts), movesPerRow):
        text = ""
        for j in range(movesPerRow):
            if j + t < len(moveTexts):
                text += moveTexts[t+j] + ' '
        textObject = font.render(text, True, pygame.Color('White'))
        textLocation = move_log_rect.move(padding, textY)
        screen.blit(textObject, textLocation)
        textY += textObject.get_height() + lineSpacing


def endgame_text(screen, text):
    font = pygame.font.SysFont('Helvetica', 50, True, False)
    object = font.render(text, False, pygame.Color('Black'))
    textLocation = pygame.Rect(0, 0, BOARD_WIDTH, BOARD_HEIGHT).move(BOARD_WIDTH / 2 - object.get_width() / 2,
                                                                     BOARD_HEIGHT / 2 - object.get_height() / 2)
    screen.blit(object, textLocation)
    object = font.render(text, False, pygame.Color('Red'))
    screen.blit(object, textLocation.move(2, 2))


def animation(move, screen, board, clock):
    global colors
    dR = move.end_row - move.start_row
    dC = move.end_col - move.start_col
    fps = 10
    frame_count = (abs(dR) + abs(dC)) * fps
    for frame in range(frame_count + 1):
        r, c = (move.start_row + dR * frame / frame_count, move.start_col + dC * frame / frame_count)
        draw_board(screen)
        draw_pieces(screen, board)
        color = colors[(move.end_row + move.end_col) % 2]
        end_sqr = pygame.Rect(move.end_col * SQUARE_SIZE, move.end_row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
        pygame.draw.rect(screen, color, end_sqr)
        if move.piece_captured != '--':
            if move.isEnpassantMove:
                enpassant_row = move.end_row + 1 if move.piece_captured[0] == 'b' else move.end_row - 1
                end_sqr = pygame.Rect(move.end_col * SQUARE_SIZE, enpassant_row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
            screen.blit(Images[move.piece_captured], end_sqr)
        if move.piece_moved != '--':
            screen.blit(Images[move.piece_moved],
                        pygame.Rect(c * SQUARE_SIZE, r * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
        pygame.display.flip()
        clock.tick(60)


if __name__ == '__main__':
    main()

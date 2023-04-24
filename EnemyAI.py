import random

piecescore = {'K': 0, 'Q': 100, 'N': 25, 'R': 50, 'B': 25, 'p': 5}
CHECKMATE = 2000
STALEMATE = 0
DEPTH = 2
global next_move

knight_score = [[1, 1, 1, 1, 1, 1, 1, 1],
                [1, 2, 2, 2, 2, 2, 2, 1],
                [1, 2, 4, 4, 4, 4, 2, 1],
                [1, 3, 4, 6, 6, 4, 3, 1],
                [1, 3, 4, 6, 6, 4, 3, 1],
                [1, 2, 4, 4, 4, 4, 2, 1],
                [1, 2, 2, 2, 2, 2, 2, 1],
                [1, 1, 1, 1, 1, 1, 1, 1]]

white_pawn_score = [[9, 9, 9, 9, 9, 9, 9, 9],
                    [4, 4, 4, 4, 4, 4, 4, 4],
                    [4, 3, 2, 2, 2, 2, 3, 4],
                    [1, 2, 2, 2, 2, 2, 2, 1],
                    [1, 2, 3, 3, 3, 3, 2, 1],
                    [1, 2, 3, 3, 3, 3, 2, 1],
                    [1, 2, 2, 2, 2, 2, 2, 1],
                    [0, 0, 0, 0, 0, 0, 0, 0]]

black_pawn_score = [[0, 0, 0, 0, 0, 0, 0, 0],
                    [1, 2, 2, 2, 2, 2, 2, 1],
                    [1, 2, 3, 3, 3, 3, 2, 1],
                    [1, 2, 3, 3, 3, 3, 2, 1],
                    [1, 2, 2, 2, 2, 2, 2, 1],
                    [4, 3, 2, 2, 2, 2, 3, 4],
                    [4, 4, 4, 4, 4, 4, 4, 4],
                    [9, 9, 9, 9, 9, 9, 9, 9]]

bishop_score = [[1, 1, 1, 1, 1, 1, 1, 1],
                [1, 2, 2, 2, 2, 2, 2, 1],
                [1, 2, 3, 3, 3, 3, 2, 1],
                [1, 2, 3, 4, 4, 3, 2, 1],
                [1, 2, 3, 4, 4, 3, 2, 1],
                [1, 2, 3, 3, 3, 3, 2, 1],
                [1, 2, 2, 2, 2, 2, 2, 1],
                [1, 1, 1, 1, 1, 1, 1, 1]]

rook_score = [[5, 4, 4, 4, 4, 4, 4, 5],
              [6, 6, 6, 6, 6, 6, 6, 6],
              [2, 2, 3, 3, 3, 3, 2, 2],
              [2, 2, 3, 4, 4, 3, 2, 2],
              [2, 2, 3, 4, 4, 3, 2, 2],
              [2, 2, 3, 3, 3, 3, 2, 2],
              [6, 6, 6, 6, 6, 6, 6, 6],
              [5, 4, 4, 4, 4, 4, 4, 5]]

queen_score = [[1, 1, 2, 2, 2, 1, 1, 1],
               [1, 2, 2, 2, 2, 2, 2, 1],
               [1, 2, 4, 3, 3, 4, 2, 1],
               [1, 2, 3, 5, 5, 3, 2, 1],
               [1, 2, 3, 5, 5, 3, 2, 1],
               [1, 2, 4, 3, 3, 4, 2, 1],
               [1, 2, 2, 2, 2, 2, 2, 1],
               [1, 1, 2, 2, 2, 1, 1, 1]]

king_score = [[5, 10, 1, 1, 1, 1, 10, 5],
              [1, 1, 1, 1, 1, 1, 1, 1],
              [1, 1, 0, 0, 0, 0, 1, 1],
              [1, 1, 0, 0, 0, 0, 1, 1],
              [1, 1, 0, 0, 0, 0, 1, 1],
              [1, 1, 0, 0, 0, 0, 1, 1],
              [1, 1, 1, 1, 1, 1, 1, 1],
              [5, 10, 1, 1, 1, 1, 10, 5]]

piece_position_score = {'K': king_score, 'Q': queen_score, 'N': knight_score, 'R': rook_score, 'B': bishop_score, 'wp': white_pawn_score, 'bp': black_pawn_score}


def find_random_move(valid_moves):
    return valid_moves[random.randint(0, len(valid_moves) - 1)]


def find_move(gs, valid_moves):
    turnMultiplayer = 1 if gs.white_to_move else -1
    enemy_min_max_score = CHECKMATE
    best_move = None
    random.shuffle(valid_moves)
    for player_move in valid_moves:
        gs.make_move(player_move)
        enemy_move = gs.move_validation()
        if gs.stalemate:
            enemy_max_score = STALEMATE
        elif gs.checkmate:
            enemy_max_score = -CHECKMATE
        else:
            enemy_max_score = -CHECKMATE
        for move in enemy_move:
            gs.make_move(move)
            gs.move_validation()
            if gs.checkmate:
                score = CHECKMATE
            elif gs.stalemate:
                score = STALEMATE
            else:
                score = -turnMultiplayer * scoreBoard(gs.board)
            if score > enemy_max_score:
                enemy_max_score = score
            gs.undo_move()
        if enemy_max_score < enemy_min_max_score:
            enemy_min_max_score = enemy_max_score
            best_move = player_move
        gs.undo_move()
    return best_move


def find_best_move(gs, valid_moves):
    global next_move
    next_move = None
    random.shuffle(valid_moves)
    alpha_beta(gs, valid_moves, DEPTH, -CHECKMATE, CHECKMATE, 1 if gs.white_to_move else -1)
    return next_move


def min_max(gs, validMoves, depth, white_to_move):
    global next_move
    if depth == 0:
        return scoreBoard(gs.board)

    if white_to_move:
        max_score = -CHECKMATE
        for move in validMoves:
            gs.make_move(move)
            nextMoves = gs.move_validation
            score = min_max(gs, nextMoves, depth - 1, False)
            if score > max_score:
                max_score = score
                if depth == DEPTH:
                    next_move = move
            gs.undo_move()
        return max_score

    else:
        min_score = CHECKMATE
        for move in validMoves:
            gs.make_move(move)
            nextMoves = gs.move_validation
            score = min_max(gs, nextMoves, depth - 1, True)
            if score < min_score:
                min_score = score
                if depth == DEPTH:
                    next_move = move
            gs.undo_move()
        return min_score


def nega_max(gs, validMoves, depth, turnMultiplayer):
    global next_move
    if depth == 0:
        return turnMultiplayer * scoreBoard(gs)

    max_score = - CHECKMATE
    for move in validMoves:
        gs.make_move(move)
        nextMoves = gs.move_validation()
        score = -nega_max(gs, nextMoves, depth - 1, -turnMultiplayer)
        if score > max_score:
            max_score = score
            if depth == DEPTH:
                next_move = move
        gs.undo_move()
    return max_score


def alpha_beta(gs, validMoves, depth, alpha, beta, turnMultiplayer):
    global next_move
    if depth == 0:
        return turnMultiplayer * scoreBoard(gs)

    max_score = - CHECKMATE
    for move in validMoves:
        gs.make_move(move)
        nextMoves = gs.move_validation()
        score = -alpha_beta(gs, nextMoves, depth - 1, -beta, -alpha, -turnMultiplayer)
        if score > max_score:
            max_score = score
            if depth == DEPTH:
                next_move = move
        gs.undo_move()
        if max_score > alpha:
            alpha = max_score
        if alpha >= beta:
            break
    return max_score


def scoreBoard(gs):
    if gs.checkmate:
        if gs.white_to_move:
            return -CHECKMATE
        else:
            return CHECKMATE
    elif gs.stalemate:
        return STALEMATE

    score = 0
    for row in range(len(gs.board)):
        for col in range(len(gs.board[row])):
            square = gs.board[row][col]
            if square != '--':
                position_score = 0
                if square[1] == 'p':
                    position_score = piece_position_score[square][row][col]
                else:
                    position_score = piece_position_score[square[1]][row][col]
                if square[0] == 'w':
                    score += piecescore[square[1]] + position_score
                elif square[0] == 'b':
                    score -= piecescore[square[1]] + position_score

    return score

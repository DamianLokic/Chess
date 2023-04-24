class GameState:
    def __init__(self):
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"],
        ]
        self.move_functions = {'p': self.pawn_moves, 'N': self.knight_moves, 'B': self.bishop_moves,
                               'Q': self.queen_moves, 'K': self.king_moves, 'R': self.rook_moves}
        self.white_to_move = True
        self.move_log = []
        self.white_king_pos = (7, 4)
        self.black_king_pos = (0, 4)
        self.checkmate = False
        self.stalemate = False
        self.enpassantPossible = ()
        self.enpassantPossibleLog = [self.enpassantPossible]
        self.currentCastlingRights = CastlingRights(True, True, True, True)
        self.CastleRightsLog = [CastlingRights(self.currentCastlingRights.wks, self.currentCastlingRights.bks,
                                               self.currentCastlingRights.wqs, self.currentCastlingRights.bqs)]

    def make_move(self, move):
        self.board[move.start_row][move.start_col] = "--"
        self.board[move.end_row][move.end_col] = move.piece_moved
        self.move_log.append(move)
        self.white_to_move = not self.white_to_move

        if move.piece_moved == 'wK':
            self.white_king_pos = (move.end_row, move.end_col)
        elif move.piece_moved == 'bK':
            self.black_king_pos = (move.end_row, move.end_col)

        if move.promotion:
            self.board[move.end_row][move.end_col] = move.piece_moved[0] + 'Q'

        if move.isEnpassantMove:
            self.board[move.start_row][move.end_col] = '--'

        if move.piece_moved[1] == 'p' and abs(move.start_row - move.end_row) == 2:
            self.enpassantPossible = ((move.start_row + move.end_row) // 2, move.start_col)
        else:
            self.enpassantPossible = ()
        self.enpassantPossibleLog.append(self.enpassantPossible)

        if move.isCastleMove:
            if move.end_col - move.start_col == 2:
                self.board[move.end_row][move.end_col - 1] = self.board[move.end_row][move.end_col + 1]
                self.board[move.end_row][move.end_col + 1] = '--'
            else:
                self.board[move.end_row][move.end_col + 1] = self.board[move.end_row][move.end_col - 2]
                self.board[move.end_row][move.end_col - 2] = '--'

        self.updateCastleRights(move)
        self.CastleRightsLog.append(CastlingRights(self.currentCastlingRights.wks, self.currentCastlingRights.bks,
                                                   self.currentCastlingRights.wqs, self.currentCastlingRights.bqs))

    def undo_move(self):
        if len(self.move_log) != 0:
            move = self.move_log.pop()
            self.board[move.start_row][move.start_col] = move.piece_moved
            self.board[move.end_row][move.end_col] = move.piece_captured
            self.white_to_move = not self.white_to_move
            # king position
            if move.piece_moved == 'wK':
                self.white_king_pos = (move.start_row, move.start_col)
            elif move.piece_moved == 'bK':
                self.black_king_pos = (move.start_row, move.start_col)
            # enpassant
            if move.isEnpassantMove:
                self.board[move.end_row][move.end_col] = '--'
                self.board[move.start_row][move.end_col] = move.piece_captured

            self.enpassantPossibleLog.pop()
            self.enpassantPossible = self.enpassantPossibleLog[-1]

            self.CastleRightsLog.pop()
            self.currentCastlingRights = self.CastleRightsLog[-1]

            if move.isCastleMove:
                if move.end_col - move.start_col == 2:
                    self.board[move.end_row][move.end_col + 1] = self.board[move.end_row][move.end_col - 1]
                    self.board[move.end_row][move.end_col - 1] = '--'
                else:
                    self.board[move.end_row][move.end_col - 2] = self.board[move.end_row][move.end_col + 1]
                    self.board[move.end_row][move.end_col + 1] = '--'

            self.checkmate = False
            self.stalemate = False

    def move_validation(self):
        temp_enpassant_possible = self.enpassantPossible
        temp_Castle_Rights = CastlingRights(self.currentCastlingRights.wks, self.currentCastlingRights.bks,
                                            self.currentCastlingRights.wqs, self.currentCastlingRights.bqs)
        moves = self.possible_moves()

        if self.white_to_move:
            self.getCastleMoves(self.white_king_pos[0], self.white_king_pos[1], moves)
        else:
            self.getCastleMoves(self.black_king_pos[0], self.black_king_pos[1], moves)

        for i in range(len(moves) - 1, -1, -1):
            self.make_move(moves[i])
            self.white_to_move = not self.white_to_move
            if self.is_check():
                moves.remove(moves[i])
            self.white_to_move = not self.white_to_move
            self.undo_move()
        if len(moves) == 0:
            if self.is_check():
                self.checkmate = True
            else:
                self.stalemate = True

        self.enpassantPossible = temp_enpassant_possible
        self.currentCastlingRights = temp_Castle_Rights
        return moves

    def is_check(self):
        if self.white_to_move:
            return self.under_attack(self.white_king_pos[0], self.white_king_pos[1])
        else:
            return self.under_attack(self.black_king_pos[0], self.black_king_pos[1])

    def under_attack(self, r, c):
        self.white_to_move = not self.white_to_move
        opponent_moves = self.possible_moves()
        self.white_to_move = not self.white_to_move
        for move in opponent_moves:
            if move.end_row == r and move.end_col == c:
                return True
        return False

    def possible_moves(self):
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                turn = self.board[r][c][0]
                if (turn == 'w' and self.white_to_move) or (turn == 'b' and not self.white_to_move):
                    piece = self.board[r][c][1]
                    self.move_functions[piece](r, c, moves)

        return moves

    def pawn_moves(self, r, c, moves):
        if self.white_to_move:
            if self.board[r - 1][c] == "--":
                moves.append(Move((r, c), (r - 1, c), self.board))
                if r == 6 and self.board[r - 2][c] == "--":
                    moves.append(Move((r, c), (r - 2, c), self.board))
            if c - 1 >= 0:
                if self.board[r - 1][c - 1][0] == 'b':
                    moves.append(Move((r, c), (r - 1, c - 1), self.board))
                elif (r - 1, c - 1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r - 1, c - 1), self.board, isEnpassantMove=True))
            if c + 1 <= 7:
                if self.board[r - 1][c + 1][0] == 'b':
                    moves.append(Move((r, c), (r - 1, c + 1), self.board))
                elif (r - 1, c + 1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r - 1, c + 1), self.board, isEnpassantMove=True))
        else:
            if self.board[r + 1][c] == "--":
                moves.append(Move((r, c), (r + 1, c), self.board))
                if r == 1 and self.board[r + 2][c] == "--":
                    moves.append(Move((r, c), (r + 2, c), self.board))
            if c - 1 >= 0:
                if self.board[r + 1][c - 1][0] == 'w':
                    moves.append(Move((r, c), (r + 1, c - 1), self.board))
                elif (r + 1, c - 1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r + 1, c - 1), self.board, isEnpassantMove=True))
            if c + 1 <= 7:
                if self.board[r + 1][c + 1][0] == 'w':
                    moves.append(Move((r, c), (r + 1, c + 1), self.board))
                elif (r + 1, c + 1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r + 1, c + 1), self.board, isEnpassantMove=True))

    def rook_moves(self, r, c, moves):
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))
        enemycolor = 'b' if self.white_to_move else 'w'
        for d in directions:
            for i in range(1, 8):
                end_row = r + d[0] * i
                end_col = c + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    end_piece = self.board[end_row][end_col]
                    if end_piece == '--':
                        moves.append(Move((r, c), (end_row, end_col), self.board))
                    elif end_piece[0] == enemycolor:
                        moves.append(Move((r, c), (end_row, end_col), self.board))
                        break
                    else:
                        break
                else:
                    break

    def queen_moves(self, r, c, moves):
        self.rook_moves(r, c, moves)
        self.bishop_moves(r, c, moves)

    def knight_moves(self, r, c, moves):
        knightmoves = ((-2, -1), (-2, 1), (-1, 2), (-1, -2), (1, 2), (1, -2), (2, -1), (2, 1))
        allycolor = 'w' if self.white_to_move else 'b'
        for move in knightmoves:
            end_row = r + move[0]
            end_col = c + move[1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] != allycolor:
                    moves.append(Move((r, c), (end_row, end_col), self.board))

    def bishop_moves(self, r, c, moves):
        directions = ((-1, 1), (-1, -1), (1, 1), (1, -1))
        enemycolor = 'b' if self.white_to_move else 'w'
        for d in directions:
            for i in range(1, 8):
                end_row = r + d[0] * i
                end_col = c + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    end_piece = self.board[end_row][end_col]
                    if end_piece == '--':
                        moves.append(Move((r, c), (end_row, end_col), self.board))
                    elif end_piece[0] == enemycolor:
                        moves.append(Move((r, c), (end_row, end_col), self.board))
                        break
                    else:
                        break
                else:
                    break

    def king_moves(self, r, c, moves):
        kingmoves = ((-1, -1), (-1, 1), (-1, 0), (1, -1), (1, 1), (1, 0), (0, -1), (0, 1))
        allycolor = 'w' if self.white_to_move else 'b'
        for i in range(8):
            end_row = r + kingmoves[i][0]
            end_col = c + kingmoves[i][1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] != allycolor:
                    moves.append(Move((r, c), (end_row, end_col), self.board))

    def updateCastleRights(self, move):
        if move.piece_moved == 'wK':
            self.currentCastlingRights.wks = False
            self.currentCastlingRights.wqs = False
        if move.piece_moved == 'bK':
            self.currentCastlingRights.bks = False
            self.currentCastlingRights.bqs = False
        if move.piece_moved == 'wR':
            if move.start_row == 7:
                if move.start_col == 0:
                    self.currentCastlingRights.wqs = False
                elif move.start_col == 7:
                    self.currentCastlingRights.wks = False
        if move.piece_moved == 'bR':
            if move.start_row == 0:
                if move.start_col == 0:
                    self.currentCastlingRights.bqs = False
                elif move.start_col == 7:
                    self.currentCastlingRights.bks = False
        if move.piece_captured == 'wR':
            if move.end_row == 7:
                if move.end_col == 0:
                    self.currentCastlingRights.wqs = False
                elif move.end_col == 7:
                    self.currentCastlingRights.wks = False
        if move.piece_captured == 'bR':
            if move.end_row == 0:
                if move.end_col == 0:
                    self.currentCastlingRights.bqs = False
                elif move.end_col == 7:
                    self.currentCastlingRights.bks = False

    def getCastleMoves(self, r, c, moves):
        if (self.white_to_move and self.currentCastlingRights.wks) or (
                not self.white_to_move and self.currentCastlingRights.bks):
            self.getKingSideCastle(r, c, moves)
        if (self.white_to_move and self.currentCastlingRights.wqs) or (
                not self.white_to_move and self.currentCastlingRights.bqs):
            self.getQueenSideCastle(r, c, moves)

    def getKingSideCastle(self, r, c, moves):
        if self.board[r][c + 1] == '--' and self.board[r][c + 2] == '--':
            if not self.under_attack(r, c + 1) and not self.under_attack(r, c + 2):
                moves.append(Move((r, c), (r, c + 2), self.board, isCastleMove=True))

    def getQueenSideCastle(self, r, c, moves):
        if self.board[r][c - 1] == '--' and self.board[r][c - 2] == '--' and self.board[r][c - 3] == '--':
            if not self.under_attack(r, c - 1) and not self.under_attack(r, c - 2) and not self.under_attack(r, c - 3):
                moves.append(Move((r, c), (r, c - 2), self.board, isCastleMove=True))


class CastlingRights:
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs


class Move:
    rank_to_row = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    row_to_rank = {s: z for z, s in rank_to_row.items()}
    files_to_cols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    cols_to_files = {s: z for z, s in files_to_cols.items()}

    def __init__(self, start, end, board, isEnpassantMove=False, isCastleMove=False):
        self.start_row = start[0]
        self.start_col = start[1]
        self.end_row = end[0]
        self.end_col = end[1]
        self.piece_moved = board[self.start_row][self.start_col]
        self.piece_captured = board[self.end_row][self.end_col]
        self.promotion = (self.piece_moved == 'wp' and self.end_row == 0) or (
                self.piece_moved == 'bp' and self.end_row == 7)
        self.isEnpassantMove = isEnpassantMove
        if self.isEnpassantMove:
            self.piece_captured = 'wp' if self.piece_moved == 'bp' else 'bp'

        self.isCastleMove = isCastleMove
        self.move_ID = self.start_row * 1000 + self.start_col * 100 + self.end_row * 10 + self.end_col

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.move_ID == other.move_ID
        return False

    def get_rank_to_file(self, r, c):
        return self.cols_to_files[c] + self.row_to_rank[r]

    def chess_notation(self):
        return self.get_rank_to_file(self.start_row, self.start_col) + self.get_rank_to_file(self.end_row, self.end_col)

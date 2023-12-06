from util import *
import math

class ClassicalBoard:
    def __init__(self, alive, bv) -> None:
        self.__bv = bv
        self.alive = alive
        self.overlap = False
        self.board = [[None for _i in range(BOARD_SIZE)] for _j in range(BOARD_SIZE)]
        for piece in Piece:
            if not self.alive[piece.value]: continue
            file, rank = self.get_pos(piece)
            if self.board[file][rank] is not None:
                self.overlap = True
            self.board[file][rank] = piece
        pass

    # combines boards
    def merge(self, other):
        assert not self.overlap
        assert self.alive == other.alive
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                if other.board[i][j] is not None:
                    assert self.board[i][j] is None or \
                        self.board[i][j] == other.board[i][j]
                    self.board[i][j] = other.board[i][j]

    def get_pos(self, piece):
        if not self.alive[piece.value]: return None
        else: return Position((self.__bv >>
            (piece.value * 6)) & ((1 << BITS_PER_PIECE) - 1))

    def get_piece(self, pos):
        assert not self.overlap
        return self.board[pos[0]][pos[1]]


class MovementValidator:

    def __init__(self, cboard, piece) -> None:
        self.board = cboard
        self.piece = piece

    def __check_axis(self, diff_x, diff_y):
        return (diff_x and not diff_y) or (not diff_x and diff_y)

    def __check_diag(self, diff_x, diff_y):
        return abs(diff_x) == abs(diff_y)

    def __check_knight(self, diff_x, diff_y):
        return (abs(diff_x) == 2 and abs(diff_y) == 1) or (abs(diff_x) == 1 and abs(diff_y) == 2)

    def __check_queen(self, diff_x, diff_y):
        return self.__check_axis(diff_x, diff_y) or self.__check_diag(diff_x, diff_y)

    def __check_king(self, diff_x, diff_y):
        if abs(diff_x) + abs(diff_y) <= 2:
            return self.__check_diag(diff_x, diff_y) or self.__check_row_col(diff_x, diff_y)

    def __check_pawn(self, diff_x, diff_y):
        old_x, old_y = self.board.get_pos(self.piece)
        is_attacking = self.board.get_piece(
            Position(old_x + diff_x, old_y + diff_y)) is not None

        okay = False
        dir = 1 if self.piece.get_color() == Color.WHITE.value else -1
        okay |= is_attacking and (diff_y == dir) and (abs(diff_x) == 1)
        okay |= self.board.get_pos(self.piece)[1] == (1 if dir == 1 else 6) \
            and diff_y == 2*dir and not diff_x
        okay |= not diff_x and diff_y == dir
        return okay

    def __diff(self, new_pos):
        diff_x, diff_y = new_pos
        old_x, old_y = self.board.get_pos(self.piece)
        diff_x -= old_x
        diff_y -= old_y
        return diff_x, diff_y

    def __collides(self, new_pos):
        diff_x, diff_y = self.__diff(new_pos)
        pos = self.board.get_pos(self.piece)

        if self.piece.get_type() == PieceType.KNIGHT:
            return False

        for _i in range(1, max(abs(diff_x), abs(diff_y))):
            if diff_x != 0: pos[0] += int(math.copysign(1, diff_x))
            if diff_y != 0: pos[1] += int(math.copysign(1, diff_y))
            if self.board.get_piece(pos) is not None: return True
        return False

    def __check_new_pos(self, new_pos):
        pt = self.piece.get_type()
        diff_x, diff_y = self.__diff(new_pos)

        if diff_x == diff_y == 0: return False
        if pt == PieceType.ROOK: return self.__check_axis(diff_x, diff_y)
        elif pt == PieceType.KNIGHT: return self.__check_knight(diff_x, diff_y)
        elif pt == PieceType.BISHOP: return self.__check_diag(diff_x, diff_y)
        elif pt == PieceType.QUEEN: return self.__check_queen(diff_x, diff_y)
        elif pt == PieceType.KING: return self.__check_king(diff_x, diff_y)
        elif pt == PieceType.PAWN: return self.__check_pawn(diff_x, diff_y)
        else: return False # Invalid piece

    def set_piece(self, piece):
        self.piece = piece

    def check(self, new_pos):
        return self.__check_new_pos(new_pos) and not self.__collides(new_pos)

    def get_eaten(self, new_pos):
        return self.board.get_piece(new_pos)



def print_board(board):
    print("  \u250C\u2500\u2500\u2500", end="")
    for i in range(7): print("\u252C\u2500\u2500\u2500", end="")
    print("\u2510")
    for i in range(BOARD_SIZE):
        print(BOARD_SIZE - i, "\u2502", end="")
        for j in range(BOARD_SIZE):
            piece = (board[j][7-i])
            if piece != None:
                piece_code = piece.get_type().value + (piece.get_color() << 4)
                print(" " + pieceType.get(piece_code) + " \u2502", end = "")
            else: print("   \u2502", end = "")
        print("")
        if(i == BOARD_SIZE - 1):
            print("  \u2514\u2500\u2500\u2500", end="")
            for i in range(BOARD_SIZE - 1): print("\u2534\u2500\u2500\u2500", end="")
            print("\u2518")
        else:
            print("  \u251C\u2500\u2500\u2500", end="")
            for i in range(BOARD_SIZE - 1): print("\u253C\u2500\u2500\u2500", end="")
            print("\u2524")
    print("    A   B   C   D   E   F   G   H")

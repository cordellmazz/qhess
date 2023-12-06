from math import pi, sqrt, e
from util import *

class ParseError(Exception):
    def __init__(self, index) -> None:
        super().__init__()
        self.index = index

def has(func):
    try:
        return func()
    except (ParseError, IndexError, ValueError):
        return False

def read_whitespace(input, index):
    while index < len(input) and input[index].isspace():
        index += 1
    return index

def read_str(input, index, string):
    index = read_whitespace(input, index)
    if input[index:index + len(string)] == string:
        return index + len(string)
    else: raise ParseError(index)

def read_piece(input, index, color=None) -> int:
    index = read_whitespace(input, index)

    if color is None:
        if input[index] == 'w': color = Color.WHITE
        elif input[index] == 'b': color = Color.BLACK
        else: raise ParseError(index)
        index += 1

    if input[index] == 'p':
        val = int(input[index + 1])
        if val == 0 or val > 8: raise ParseError(index)
        val -= 1
        return index + 2, Piece(color.value + PieceType.PAWN.value + val)
    elif input[index] == 'k':
        return index + 1, Piece(color.value + PieceType.KING.value)
    elif input[index] == 'q':
        return index + 1, Piece(color.value + PieceType.QUEEN.value)
    else:
        val = int(input[index + 1])
        if val == 0 or val > 2: raise ParseError(index)
        val -= 1
        piece_type = None
        if input[index] == 'r': piece_type = PieceType.ROOK
        elif input[index] == 'b': piece_type = PieceType.BISHOP
        elif input[index] == 'n': piece_type = PieceType.KNIGHT
        if piece_type is None: raise ParseError(index)
        return index + 2, Piece(color.value + piece_type.value + val)

def read_pos(input, index):
    index = read_whitespace(input, index)
    pos_str = input[index:index + 2]
    if not ('a' <= pos_str[0] and pos_str[0] <= 'h'):
        raise ParseError(index)
    if not ('1' <= pos_str[1] and pos_str[1] <= '8'):
        raise ParseError(index + 1)
    return index + 2, Position(pos_str)

def read_cond(input, index):
    index = read_whitespace(input, index)
    index, piece = read_piece(input, index)
    index = read_str(input, index, 'at')
    index, pos = read_pos(input, index)
    return index, (piece, pos)
    
def read_complex(input, index):
    index = read_whitespace(input, index)
    index = read_str(input, index, '(')
    tilde = input.find('~', index)
    if tilde < 0: raise ParseError(index)
    end = input.find(')', tilde)
    if end < 0: raise ParseError(tilde)

    mag2 = float(input[index:tilde])
    angle = float(input[tilde + 1:end])

    return end + 1, sqrt(mag2) * (e ** (1j * pi * angle))


# Parses input for the if syntax
def read_if(input, index):
    index = read_whitespace(input, index)
    index = read_str(input, index, 'if')

    index, cond = read_cond(input, index)

    index = read_str(input, index, '{')
    index, first = read_move(input, index)
    index = read_str(input, index, '}')

    index = read_str(input, index, 'else')
    index = read_str(input, index, '{')
    index, second = read_move(input, index)
    index = read_str(input, index, '}')

    return index, (cond, first, second)

def read_dict(input, index, inner, delim):
    index = read_whitespace(input, index)
    result = list()

    first = True
    while first or has(lambda: read_str(input, index, delim)):
        if first: first = False
        else: index = read_str(input, index, delim)
        index, item = inner(input, index)
        result.append(item)

    return index, dict(result)

def read_col_elem(input, index):
    index = read_whitespace(input, index)
    index, pos = read_pos(input, index)
    index, coeff = read_complex(input, index)
    return index, (pos, coeff)

def read_col(input, index):
    index = read_whitespace(input, index)
    index, pos = read_pos(input, index)
    index = read_str(input, index, ':')
    index, result = read_dict(input, index, read_col_elem, '+')
    return index, (pos, result)

def read_map(input, index):
    index = read_whitespace(input, index)
    return read_dict(input, index, read_col, ',')

def read_move(input, index):
    index = read_whitespace(input, index)

    move = None
    if has(lambda: read_str(input, index, 'if')):
        index, move = read_if(input, index)
    else: index, move = read_map(input, index)
    return index, move

def read_turn(input, index, color):
    index = read_whitespace(input, index)

    index, piece = read_piece(input, index, color)
    index = read_str(input, index, ':')
    index, move = read_move(input, index)
    return index, piece, move

def parse(input, color):
    index, piece, move = read_turn(input, 0, color)
    index = read_whitespace(input, index)
    if index != len(input): raise ParseError(index)
    return piece, move

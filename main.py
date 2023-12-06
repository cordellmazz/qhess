from classical import print_board, ClassicalBoard
from quantum import quantum_check, quantum_move
from simulator import Qubits
from parse import parse, ParseError
from util import *

import os
import sys
import math
import cmath

# chess stuff
STARTING_POS = dict()
for color in range(2):
    for type in PieceType:
        if type == PieceType.PAWN:
            for index in range(8):
                piece = Piece((color << 4) + (type.value | index))
                STARTING_POS[piece] = Position(index, 1 if color == 0 else 6)
        else:
            for index in range(2):
                piece = Piece((color << 4) + (type.value | index))
                file = (type.value // 2) if index == 0 else 7 - (type.value // 2)
                rank = 0 if color == 0 else 7
                STARTING_POS[piece] = Position(file, rank)


INITIAL_STATE = 0
for piece in Piece:
    INITIAL_STATE += piece.at_pos(STARTING_POS[piece])

# handles all of the high level content and function of the game
class QuantumChess:
    def __init__(self) -> None:
        self.state = Qubits(INITIAL_STATE)
        self.alive = [True] * NUM_PIECES
        self.move = Color.WHITE # white to move

    # flattens all quantum boards into one classical representation of the board
    def flatten(self):
        board = None
        for bv in self.state.statedict:
            if board is None: board = ClassicalBoard(self.alive, bv)
            else: board.merge(ClassicalBoard(self.alive, bv))
        return board.board

    def get_board(self, index):
        bv = sorted(self.state.statedict)[index] # very slow but who cares
        return ClassicalBoard(self.alive, bv).board, self.state.statedict[bv]

    # Parses user input from <piece_rank> <piece_file> <new_rank> <new_file> to a piece object and board location (piece, rank, file)
    def start_game(self):
        current_board = None
        current_message = ''
        while self.alive[Piece.WHITE_KING.value] and self.alive[Piece.BLACK_KING.value]:
            # os.system('cls' if os.name == 'nt' else 'clear')
            if current_board is not None:
                board, coeff = self.get_board(current_board)
                radius, theta = cmath.polar(coeff)
                print('Board {:2} of {:2}, (r^2, theta) = ({:4.3}, {:4.3}pi)'.format(
                    current_board + 1, len(self.state.statedict),
                    radius ** 2, theta / math.pi))
                print_board(board)
            else:
                print('Flattened board ({} board total)'.format(len(self.state.statedict)))
                print_board(self.flatten())

            print()
            print(current_message)

            print('Enter command:', end=' ')
            sys.stdout.flush()
            command = input()
            if command.startswith('board'):
                try:
                    bn_str = command[len('board'):].strip()
                    if bn_str == 'flat': current_board = None
                    else: current_board = int(bn_str) - 1
                except ValueError:
                    current_message = 'Invalid board!'
            else:
                command = command.lower()
                try:
                    piece, move = parse(command, self.move)
                except (ParseError, IndexError, ValueError) :
                    current_message = 'Invalid move!'
                    continue

                check, measure_list = quantum_check(self, piece, move)
                if not check:
                    current_message = 'Invalid move!'
                    continue
                quantum_move(self, piece, move)
                self.state.measure((index for mp in measure_list \
                    for index in mp.get_indices()))
                for bv in self.state.statedict:
                    cboard = ClassicalBoard(self.alive, bv)
                    for mp in measure_list:
                        if cboard.get_pos(mp) is not None and \
                            cboard.get_pos(piece) == cboard.get_pos(mp) \
                            and piece != mp: self.alive[mp.value] = False
                self.move = Color.BLACK if self.move == Color.WHITE else Color.WHITE
                current_board = None
                current_message = ''
   
QuantumChess().start_game()

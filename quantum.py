from classical import ClassicalBoard, MovementValidator
from scipy import sparse
from simulator import THRESHOLD
from util import *

def numeric_map(pos_map):
    return {
        source.value: {
            target.value: pos_map[source][target] \
                for target in pos_map[source]
        } for source in pos_map
    }

# verifies that the user inputted movement is actually a unitary function
def check_unitary(numeric_map):
    matrix = sparse.identity(BOARD_SIZE ** 2, dtype=complex, format='dok')
    for source in numeric_map: # source = col, target = row
        matrix[source, source] = 0
    for source in numeric_map:
        for target in numeric_map[source]:
            matrix[target, source] = numeric_map[source][target]
    matrix = matrix.conjtransp().dot(matrix)
    matrix -= sparse.identity(BOARD_SIZE ** 2, dtype=complex)

    sum = 0
    rows, cols = matrix.nonzero()
    for r, c in zip(list(rows), list(cols)):
        sum += abs(matrix[r, c]) ** 2
    return sum < THRESHOLD

# seuqentially moves through cboards and attempts to move the piece
def quantum_move(qboard, piece, move, aux_n = 0):
    if isinstance(move, dict):
        qboard.state.mcmu((1 << aux_n) - 1, range(TOTAL_QUBITS, TOTAL_QUBITS + aux_n),
            numeric_map(move), piece.get_indices())
    else:
        condition, move_true, move_false = move
        control_piece, control_position = condition
        controls = control_piece.get_indices()
        qboard.state.mcx(control_position.value, controls, TOTAL_QUBITS + aux_n)
        quantum_move(qboard, piece, move_true, aux_n + 1)
        qboard.state.x(TOTAL_QUBITS + aux_n)
        quantum_move(qboard, piece, move_false, aux_n + 1)
        qboard.state.x(TOTAL_QUBITS + aux_n)
        qboard.state.mcx(control_position.value, controls, TOTAL_QUBITS + aux_n)

def find_move(cboard, move):
    if isinstance(move, dict):
        return move
    else:
        condition, move_true, move_false = move
        piece, position = condition
        if cboard.get_piece(position) == piece:
            return find_move(cboard, move_true)
        else:
            return find_move(cboard, move_false)

# sequentially runs through your move in an attempt to search for collisions
def quantum_check(qboard, piece, move):
    measure_list = []
    for bv in qboard.state.statedict:
        cboard = ClassicalBoard(qboard.alive, bv)
        validator = MovementValidator(cboard, piece)
        current_move = find_move(cboard, move)

        if not check_unitary(numeric_map(current_move)): return False, None
        if cboard.get_pos(piece) not in current_move: return False, None

        targets = current_move[cboard.get_pos(piece)]
        for target in targets:
            if not validator.check(target): return False, None
            eaten = validator.get_eaten(target)
            if eaten is not None:
                measure_list.append(eaten)
    if len(measure_list): measure_list.append(piece)
    return True, measure_list

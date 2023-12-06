from math import sqrt
import random
from collections import defaultdict
from util import THRESHOLD

def bit(num, i):
    return int((num & (1 << i)) != 0)

# simulator from last semester
class Qubits:
    def __init__(self, val):
        self.statedict = defaultdict(complex)
        self.statedict[val] = complex(1)

    def x(self, target):
        new = defaultdict(complex)
        for bv in self.statedict:
            new[bv ^ (1 << target)] += self.statedict[bv]
        self.statedict = new
        self.clean()

    # multi controlled not gate
    def mcx(self, pattern, controls, target):
        new = defaultdict(complex)
        for bv in self.statedict:
            for i in range(len(controls)):
                if bit(bv, controls[i]) != bit(pattern, i):
                    new[bv] += self.statedict[bv]
                    break
            else:
                new[bv ^ (1 << target)] += self.statedict[bv]
        self.statedict = new
        self.clean()

    # multi controlled multi unitary gate that takes in a pattern, list of controls, permutation, and targets
    def mcmu(self, pattern, controls, perm, targets):
        new = defaultdict(complex)
        bitmask = sum((1 << target for target in targets))
        def tb(val_t):
            val_b = 0
            for i in range(len(targets)):
                if bit(val_t, i) == 1:
                    val_b += (1 << targets[i])
            return val_b

        perm = {tb(from_t): {tb(to_t): to_coeff \
                for to_t, to_coeff in to.items()} \
            for from_t, to in perm.items()}

        for bv in self.statedict:
            for i in range(len(controls)):
                if bit(bv, controls[i]) != bit(pattern, i):
                    new[bv] += self.statedict[bv]
                    break
            else:
                cleared = bv & ~bitmask
                val_t = bv & bitmask
                if val_t not in perm: continue
                for to_b in perm[val_t]:
                    result_b = cleared + to_b
                    new[result_b] += self.statedict[bv] * \
                        perm[val_t][to_b]
        self.statedict = new
        self.clean()

    # collapses state and returns output
    def measure(self, indices):
        for index in indices:
            p1 = 0
            for bv in self.statedict:
                if bit(bv, index) == 1:
                    p1 += abs(self.statedict[bv]) ** 2
            is_one = random.uniform(0, 1) <= p1
            for bv in self.statedict:
                if bit(bv, index) != int(is_one):
                    self.statedict[bv] = 0
            self.normalize()
            self.clean()

    # does what it says
    def normalize(self):
        mag = 0
        for bv in self.statedict:
            mag += abs(self.statedict[bv]) ** 2
        mag = sqrt(mag)
        for bv in self.statedict:
            self.statedict[bv] /= mag

    # cleans up the statevectors and removes noise added from real value math
    def clean(self):
        self.statedict = defaultdict(complex, filter(
            lambda x: abs(x[1]) >= THRESHOLD,
            self.statedict.items()))
        self.normalize()

import os
from time import sleep
from algorithm import PuzzleSolver, PuzzleState, StepSequence, StepSequenceCursor


def cls():
    os.system('cls' if os.name=='nt' else 'clear')

class PuzzleUI:

    def init(self):
        shuffle_sequence = StepSequence()
        shuffle_sequence.fillRandom(10)
        puzzle = PuzzleState()
        shuffle_sequence.apply(puzzle)
        cls()
        print(shuffle_sequence.to_str())
        print(puzzle.to_str())

        solver = PuzzleSolver(puzzle)
        solver.solve_adaptive()

    def play(self):
        while self.cursor.has_next():
            cls()
            print(self.cursor.to_str())
            sleep(1)
            self.cursor.next()

        cls()
        print(self.cursor.to_str())
        sleep(1)

PuzzleUI().init()
    
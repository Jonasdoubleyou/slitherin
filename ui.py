import os
from time import sleep
from algorithm import StepSequence, StepSequenceCursor


def cls():
    os.system('cls' if os.name=='nt' else 'clear')

class PuzzleUI:

    def init(self):
        shuffle_sequence = StepSequence()
        shuffle_sequence.fillRandom(10)
        self.cursor = StepSequenceCursor(shuffle_sequence)
        self.play()

        solve_sequence = shuffle_sequence.invert()
        self.cursor = StepSequenceCursor(solve_sequence, self.cursor.currentState())
        self.play()


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
    
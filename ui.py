import os
from time import sleep
from algorithm import StepSequence, StepSequenceCursor


def cls():
    os.system('cls' if os.name=='nt' else 'clear')

class PuzzleUI:

    def init(self):
        sequence = StepSequence()
        sequence.fillRandom(10)
        self.cursor = StepSequenceCursor(sequence)

        self.play()

    def play(self):
        while self.cursor.has_next():
            cls()
            print(self.cursor.to_str())
            sleep(1)
            self.cursor.next()

        cls()
        print(self.cursor.to_str())
        sleep(1000)

PuzzleUI().init()
    
import os
from algorithm import PuzzleState
from ui import PuzzleUI
from time import time_ns, sleep

# Standalone runtime, to run the program somewhere else

# Interface to a regular python environment
class UIController:
    def cls(self):
        os.system('cls' if os.name=='nt' else 'clear')

    def print(self, row: str):
        print(row)

    def time_ms(self):
        return time_ns() // 1_000_000
    
    def sleep(self, duration):
        sleep(duration)

    def wait_for_enter(self):
        input("go?")

    def select(self, title, values):
        self.print(title)
        for (idx, value) in enumerate(values):
            self.print(" " + str(idx) + " - " + value)
        selection = input(" > ")
        return values[int(selection)]
    
    def do_move(self, step, state: PuzzleState):
        sleep(0.7)

PuzzleUI(UIController()).init()

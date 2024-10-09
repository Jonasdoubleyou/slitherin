import os
from time import sleep, time_ns
from algorithm import PuzzleSolver, PuzzleState, StepSequence, StepSequenceCursor, FREE_FIELD


def cls():
    os.system('cls' if os.name=='nt' else 'clear')

class PuzzleUI:

    def init(self):
        while True:
            cls()
            print("Game Mode:")
            type = self.select(["random", "template", "scan"])
            if type == "random":
                self.init_random()
            elif type == "template":
                self.init_template()
            elif type == "scan":
                print("Scan not yet supported")
                continue

            cls()
            print(self.puzzle.to_str())
            self.wait_for_enter()

            start_time = time_ns()
            self.solve()
            self.play()
            duration = (time_ns() - start_time) // 1_000_000 // 1000

            sleep(5)

            cls()
            print("I WON")
            print("in " + str(duration) + "s")
            print()
            print("Want to play again?")
            self.wait_for_enter()

    def init_random(self):
        shuffle_sequence = StepSequence()
        shuffle_sequence.fillRandom(15)
        self.puzzle = PuzzleState()
        shuffle_sequence.apply(self.puzzle)

    def init_template(self):
        cls()
        print("Difficulty:")
        template = self.select(["easy", "medium", "hard"])
        if template == "easy":
            self.puzzle = PuzzleState((1, 2, 3, 4, FREE_FIELD, 5, 7, 8, 6))
        elif template == "medium":
            self.puzzle = PuzzleState((1, 2, 3, 4, FREE_FIELD, 5, 7, 8, 6))
        else:
            self.puzzle = PuzzleState((1, 2, 3, 4, FREE_FIELD, 5, 7, 8, 6))


    def solve(self):
        cls()
        print("Solving Puzzle")
        solver = PuzzleSolver(self.puzzle)
        solver.solve_adaptive()
        if solver.solution == None:
            raise Exception("Failed to solve puzzle")
        
        self.cursor = StepSequenceCursor(solver.solution, self.puzzle)

        cls()
        print("Solved Puzzle")

    def play(self):
        while self.cursor.has_next():
            cls()
            print(self.cursor.to_str(hide_sequence=True))
            sleep(0.7)
            self.cursor.next()

        if self.cursor.currentState().fields != PuzzleState().fields:
            raise Exception("Failed to solve puzzle, did not arrive at target state")

        cls()
        print(self.cursor.to_str(hide_sequence=True))

    def wait_for_enter(self):
        input("go?")

    def select(self, values):
        for (idx, value) in enumerate(values):
            print(" " + str(idx) + " - " + value)
        selection = input(" > ")
        return values[int(selection)]
        


PuzzleUI().init()
    
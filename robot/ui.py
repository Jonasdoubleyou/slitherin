from algorithm import PuzzleSolver, PuzzleState, StepSequence, StepSequenceCursor, FREE_FIELD

class PuzzleUI:
    def __init__(self, ctrl):
        self.ctrl = ctrl

    def init(self):
        while True:
            try:
                self.ctrl.cls()
                type = self.ctrl.select("Game Mode", ["random", "template", "exit"])
                if type == "random":
                    self.init_random()
                elif type == "template":
                    self.init_template()
                else:
                    return

                self.ctrl.cls()
                self.ctrl.print(self.puzzle.to_str())
                self.ctrl.wait_for_enter()

                start_time = self.ctrl.time_ms()
                self.solve()
                self.play()
                duration = (self.ctrl.time_ms() - start_time) // 1000

                self.ctrl.sleep(5)

                self.ctrl.cls()
                self.ctrl.print("I WON")
                self.ctrl.print("in " + str(duration) + "s")
                self.ctrl.print("")
                self.ctrl.print("Want to play again?")
                self.ctrl.wait_for_enter()
            except:
                pass

    def init_random(self):
        shuffle_sequence = StepSequence()
        # Only do at most 9 moves - so that the depth search finds something
        # without taking too long
        shuffle_sequence.fillRandom(9)
        self.puzzle = PuzzleState()
        self.cursor = StepSequenceCursor(shuffle_sequence)
        self.play()
        self.puzzle = self.cursor.currentState()

    def init_template(self):
        self.ctrl.cls()
        template = self.ctrl.select("Difficulty", ["easy", "medium", "hard"])
        if template == "easy":
            self.puzzle = PuzzleState((1, 2, 3, 4, FREE_FIELD, 6, 7, 8, 5))
        elif template == "medium":
            self.puzzle = PuzzleState((1, 2, 3, 4, FREE_FIELD, 5, 7, 8, 6))
        else:
            self.puzzle = PuzzleState((1, 2, 3, 4, FREE_FIELD, 5, 7, 8, 6))

    def solve(self):
        self.ctrl.cls()
        self.ctrl.print("Solving Puzzle")
        solver = PuzzleSolver(self.puzzle)
        
        # "the 8 Puzzle always can be solved in no more than 31 single-tile moves or 24 multi-tile moves"
        # ~ https://en.wikipedia.org/wiki/15_puzzle
        for max_depth in (5, 10, 15, 24):
            self.ctrl.print("+ depth " + str(max_depth))
            start_time = self.ctrl.time_ms()
            solver.solve(max_depth)
            duration = self.ctrl.time_ms() - start_time
            self.ctrl.print("        " + str(duration) + "ms")

            if solver.solution != None:
                break

        if solver.solution == None:
            self.ctrl.cls()
            self.ctrl.print("Unsolvable Puzzle")
            self.wait_for_input()

            raise Exception("Failed to solve puzzle")
        
        self.cursor = StepSequenceCursor(solver.solution, self.puzzle)

        self.ctrl.cls()
        self.ctrl.print("Solved Puzzle")

    def play(self):
        try:
            while self.cursor.has_next():
                self.ctrl.cls()
                self.ctrl.print(self.cursor.to_str(hide_sequence=True))

                self.ctrl.do_move(self.cursor.currentStep(), self.cursor.currentState())

                self.cursor.next()

            # if self.cursor.currentState().fields != PuzzleState().fields:
            #     raise Exception("Failed to solve puzzle, did not arrive at target state")
        finally:
            self.ctrl.finish()

        self.ctrl.cls()
        self.ctrl.print(self.cursor.to_str(hide_sequence=True))

    
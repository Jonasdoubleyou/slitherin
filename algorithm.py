from enum import Enum
import random
from typing import List

# ------- Step --------
# The direction into which tiles move by lifting the field on one side
class StepDirection(Enum):
    UP = 0
    LEFT = 1
    DOWN = 2
    RIGHT = 3

    def inverse(self):
        return StepDirection(((self.value + 2) %4))
    
    def is_x(self):
        return (self.value % 2) == 1 # left, right
    
    def is_y(self):
        return (self.value % 2) == 0 # up, down
    
    # opposite direction of the axis
    def is_opposite(self):
        return self.value >= 2 # down, right
    
    # The number of fields in the direction
    def size(self):
        return SIZE_X if self.is_x() else SIZE_Y

    # position + stride returns the next position on the field in the direction
    def stride(self):
        return (1 if self.is_x() else SIZE_X) * (1 if self.is_opposite() else -1)
    
    def char(self):
        if self == StepDirection.DOWN:
            return "v"
        if self == StepDirection.UP:
            return "^"
        if self == StepDirection.RIGHT:
            return ">"
        if self == StepDirection.LEFT:
            return "<"
        
    # ---- Position Utilities -----
    def offset_in_dir(self, pos: int):
        pos_in_axis = int(pos / SIZE_X) if self.is_y() else (pos % SIZE_X)
        return (self.size() - 1) - pos_in_axis if self.is_opposite() else pos_in_axis
    
    def is_at_border(self, pos: int):
        return self.offset_in_dir(pos) == self.size() - 1
    
    @staticmethod
    def random():
        return StepDirection(random.randint(1, 4))
    

# A step that modifies the puzzle state, to arrive at a new puzzle state
class Step:
    # direction - the direction of the step
    # move_count - the number of tiles that should move
    def __init__(self, direction: StepDirection, move_count: int):
        assert(move_count > 0)
        self.direction = direction
        self.move_count = move_count

    # returns the Step that when applied after or before this state,
    # arrives back at the original puzzle state
    # e.g. the opposite of moving two to the left is moving two to the right
    def inverse(self):
        return Step(self.direction.inverse(), self.move_count)
    
    def to_str(self):
        return self.direction.char() + str(self.move_count)

# ----- PuzzleState -----
# The state of the puzzle at a certain point in time

# The dimensions of the puzzle
SIZE_X = 3
SIZE_Y = 3

def to_x(pos: int):
    return pos % SIZE_X

def to_y(pos: int):
    return int(pos / SIZE_X)

def to_xy(pos: int):
    return (to_x(pos), to_y(pos))

def to_pos(x: int, y: int):
    return y * SIZE_X + x

FREE_FIELD = 0
TARGET_FIELDS = (1, 2, 3, 4, 5, 6, 7, 8, 0)

class PuzzleState:
    # fields - The fields as a SIZE_Y x SIZE_X array
    def __init__(self, fields = TARGET_FIELDS):
        self.fields = list(fields)
        # the position of the free field
        self.free_pos = fields.index(FREE_FIELD)

    # Applies a Step to the Puzzle State
    def apply(self, step: Step):
        start_free_pos = self.free_pos

        try:
            assert(self.fields[self.free_pos] == FREE_FIELD)
            assert(step.move_count > 0)

            stride = step.direction.stride()

            count = 0
            while not step.direction.is_at_border(self.free_pos) and count < step.move_count:
                prev_pos = self.free_pos - stride
                self.fields[self.free_pos] = self.fields[prev_pos]
                self.free_pos = prev_pos
                count += 1
            
            self.fields[self.free_pos] = FREE_FIELD
        except Exception:
            print("Failed to apply step:")
            print("field at time of exception:\n" + self.to_str())
            print("step: " + step.to_str())
            print("free pos: " + str(self.free_pos))
            print("start free pos: " + str(start_free_pos))
            print("stride: " + str(stride))
            print("prev_pos: " + str(prev_pos))
            raise

    def to_str(self, step: Step = None) -> str:
        line_length = SIZE_X * 5
        result = bytearray(((" " * (line_length - 1)) + "\n") * (SIZE_Y * 3), "utf-8")
        
        # turns coordinates into fields into string positions
        def to_str(pos: int):
            x = to_x(pos)
            y = to_y(pos)
            return x * 5 + 1 + (y * 3 + 1) * line_length

        # Fill with fields
        for y in range(0, SIZE_Y):
            for x in range(0, SIZE_X):
                field = self.fields[x + SIZE_X * y]
                if field != FREE_FIELD:
                    result[to_str(to_pos(x, y))] = field + 48 # "0" at 48 in ASCII
        
        # Add movement
        if step != None:
            marker_offset = (line_length if step.direction.is_y() else 1) * (1 if step.direction.is_opposite() else -1)
            pos = self.free_pos
            result[to_str(pos) + marker_offset] = ord('x')
        
            count = 0
            while not step.direction.is_at_border(pos) and count < step.move_count:
                pos -= step.direction.stride()
                result[to_str(pos) + marker_offset] = ord(step.direction.char())
                count += 1

        return result.decode("utf-8")

    # Returns a random step that can be done at the current state
    def randomStep(self, prevStep: Step = None):
        if prevStep == None:
            direction = StepDirection.random()
        else:
            opposite = random.randint(0, 1) == 1
            if prevStep.direction.is_x():
                direction = StepDirection.DOWN if opposite else StepDirection.UP
            else:
                direction = StepDirection.RIGHT if opposite else StepDirection.LEFT

        pos_in_direction = to_x(self.free_pos) if direction.is_x() else to_y(self.free_pos)
        fields_in_direction = (SIZE_X - 1) if direction.is_x() else (SIZE_Y - 1)
        max_moves = (fields_in_direction - pos_in_direction) if not direction.is_opposite() else pos_in_direction
        if max_moves == 0: # useless Step that does nothing
            return self.randomStep(prevStep)
        moves = random.randint(1, max_moves)
        return Step(direction, moves)
    
class StepSequence:
    steps: List[Step] = list()

    def fillRandom(self, length: int, puzzle: PuzzleState = PuzzleState()):
        current_state = PuzzleState(puzzle.fields)
        current_step = None
        for i in range(0, length):
            current_step = current_state.randomStep(current_step)
            self.steps.append(current_step)
            current_state.apply(current_step)

    def to_str(self):
        result = ""
        for step in self.steps:
            result += " " + step.to_str()
        return result


class StepSequenceCursor:
    index = 0
    def __init__(self, sequence: StepSequence, puzzle: PuzzleState = PuzzleState()):
        self.sequence = sequence
        self.puzzle = PuzzleState(puzzle.fields)

    def has_next(self):
        return self.index < len(self.sequence.steps)

    def currentState(self):
        return self.puzzle
    
    def currentStep(self):
        return self.sequence.steps[ self.index ]

    def next(self):
        self.puzzle.apply(self.currentStep())
        self.index += 1

    def to_str(self):
        result = self.sequence.to_str() + "\n"
        if self.has_next():
            result += (" " * (1 + self.index * 3)) + "^"
        result += "\n\n"
        result += self.puzzle.to_str(self.currentStep() if self.has_next() else None)
        return result


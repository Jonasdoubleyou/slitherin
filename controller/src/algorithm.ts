
// Direction into which tiles move by lifting the field on one side
class StepDirection {
    static UP = new StepDirection(0);
    static LEFT = new StepDirection(1);
    static DOWN = new StepDirection(2);
    static RIGHT = new StepDirection(3);

    value: number;

    constructor(value: number) {
        this.value = value;
    }

    equals(other: StepDirection): boolean {
        return this.value === other.value;
    }

    inverse(): StepDirection {
        return new StepDirection((this.value + 2) % 4);
    }

    isX(): boolean {
        return (this.value % 2) === 1; // left, right
    }

    isY(): boolean {
        return (this.value % 2) === 0; // up, down
    }

    isOpposite(): boolean {
        return this.value >= 2; // down, right
    }

    size(): number {
        return this.isX() ? SIZE_X : SIZE_Y;
    }

    stride(): number {
        return (this.isX() ? 1 : SIZE_X) * (this.isOpposite() ? 1 : -1);
    }

    char(): string {
        if (this.equals(StepDirection.DOWN)) return "v";
        if (this.equals(StepDirection.UP)) return "^";
        if (this.equals(StepDirection.RIGHT)) return ">";
        if (this.equals(StepDirection.LEFT)) return "<";
        throw new Error("Unknown direction");
    }

    // ---- Position Utilities -----
    offsetInDir(pos: number): number {
        const posInAxis = this.isY() ? Math.floor(pos / SIZE_X) : (pos % SIZE_X);
        return this.isOpposite() ? (this.size() - 1) - posInAxis : posInAxis;
    }

    maxMoves(pos: number): number {
        return (this.size() - 1) - this.offsetInDir(pos);
    }

    isAtBorder(pos: number): boolean {
        return this.offsetInDir(pos) === this.size() - 1;
    }

    static random(): StepDirection {
        const randomValue = Math.floor(Math.random() * 4);
        return new StepDirection(randomValue);
    }
}

// A step that modifies the puzzle state to arrive at a new puzzle state
class Step {
    direction: StepDirection;
    moveCount: number;

    constructor(direction: StepDirection, moveCount: number) {
        if (moveCount <= 0) {
            throw new Error("Move count must be greater than 0");
        }
        this.direction = direction;
        this.moveCount = moveCount;
    }

    // Returns the Step that, when applied after or before this state,
    // arrives back at the original puzzle state.
    // e.g., the opposite of moving two to the left is moving two to the right.
    inverse(): Step {
        return new Step(this.direction.inverse(), this.moveCount);
    }

    toString(): string {
        return this.direction.char() + this.moveCount.toString();
    }
}

// Puzzle dimensions
const SIZE_X = 3;
const SIZE_Y = 3;

function toX(pos: number): number {
    return pos % SIZE_X;
}

function toY(pos: number): number {
    return Math.floor(pos / SIZE_X);
}

function toXY(pos: number): [number, number] {
    return [toX(pos), toY(pos)];
}

function toPos(x: number, y: number): number {
    return y * SIZE_X + x;
}

const FREE_FIELD = 0;
const TARGET_FIELDS = [1, 2, 3, 4, 5, 6, 7, 8, 0];

export class PuzzleState {
    fields: number[];
    freePos: number;

    constructor(fields: number[] = TARGET_FIELDS) {
        this.fields = [...fields];
        this.freePos = this.fields.indexOf(FREE_FIELD);
    }

    // Applies a Step to the PuzzleState
    apply(step: Step): void {
        const startFreePos = this.freePos;

        try {
            if (this.fields[this.freePos] !== FREE_FIELD) {
                throw new Error("The free field is not at the expected position.");
            }
            if (step.moveCount <= 0) {
                throw new Error("Move count must be greater than 0.");
            }

            const stride = step.direction.stride();
            let count = 0;

            while (!step.direction.isAtBorder(this.freePos) && count < step.moveCount) {
                const prevPos = this.freePos - stride;
                this.fields[this.freePos] = this.fields[prevPos];
                this.freePos = prevPos;
                count++;
            }

            this.fields[this.freePos] = FREE_FIELD;
        } catch (error) {
            console.error("Failed to apply step:");
            console.error("Field at time of exception:\n" + this.toString());
            console.error("Step: " + step.toString());
            console.error("Free position: " + this.freePos);
            console.error("Start free position: " + startFreePos);
            throw error;
        }
    }

    toString(step: Step | null = null): string {
        const lineLength = SIZE_X * 4;
        const result = [..." ".repeat((lineLength - 1) * (SIZE_Y * 2 + 1))];

        const toStr = (pos: number): number => {
            const x = toX(pos);
            const y = toY(pos);
            return x * 4 + 1 + (y * 2 + 1) * lineLength;
        };

        // Fill fields
        for (let y = 0; y < SIZE_Y; y++) {
            for (let x = 0; x < SIZE_X; x++) {
                const field = this.fields[x + SIZE_X * y];
                if (field !== FREE_FIELD) {
                    result[toStr(toPos(x, y))] = "" + field;
                }
            }
        }

        // Add movement
        if (step) {
            const markerOffset =
                (step.direction.isY() ? lineLength : 1) * (step.direction.isOpposite() ? 1 : -1);
            let pos = this.freePos;
            result[toStr(pos) + markerOffset] = "x";

            let count = 0;
            while (!step.direction.isAtBorder(pos) && count < step.moveCount) {
                pos -= step.direction.stride();
                result[toStr(pos) + markerOffset] = step.direction.char();
                count++;
            }
        }

        return result.join("");
    }

    randomStep(prevStep: Step | null = null): Step {
        let direction: StepDirection;

        if (prevStep === null) {
            direction = StepDirection.random();
        } else {
            const opposite = Math.random() < 0.5;
            direction = prevStep.direction.isX()
                ? opposite
                    ? StepDirection.DOWN
                    : StepDirection.UP
                : opposite
                ? StepDirection.RIGHT
                : StepDirection.LEFT;
        }

        const maxMoves = direction.maxMoves(this.freePos);
        if (maxMoves === 0) {
            return this.randomStep(prevStep);
        }

        const moves = maxMoves === 1 ? 1 : Math.floor(Math.random() * maxMoves) + 1;
        return new Step(direction, moves);
    }

    possibleSteps(prevStep: Step | null = null): Step[] {
        let possibleDirections: StepDirection[];

        if (prevStep === null) {
            possibleDirections = [
                StepDirection.UP,
                StepDirection.DOWN,
                StepDirection.LEFT,
                StepDirection.RIGHT,
            ];
        } else {
            possibleDirections = prevStep.direction.isX()
                ? [StepDirection.DOWN, StepDirection.UP]
                : [StepDirection.RIGHT, StepDirection.LEFT];
        }

        const possibleSteps: Step[] = [];
        for (const direction of possibleDirections) {
            const maxMoves = direction.maxMoves(this.freePos);
            for (let moveCount = 1; moveCount <= maxMoves; moveCount++) {
                possibleSteps.push(new Step(direction, moveCount));
            }
        }
        return possibleSteps;
    }
}


export class StepSequence {
    steps: Step[];

    constructor(steps: Step[] = []) {
        this.steps = steps;
    }

    fillRandom(length: number, puzzle: PuzzleState = new PuzzleState()): void {
        const currentState = new PuzzleState(puzzle.fields);
        let currentStep: Step | null = null;

        for (let i = 0; i < length; i++) {
            currentStep = currentState.randomStep(currentStep);
            this.steps.push(currentStep);
            currentState.apply(currentStep);
        }
    }

    invert(): StepSequence {
        const invertedSteps = this.steps.slice().reverse().map(step => step.inverse());
        return new StepSequence(invertedSteps);
    }

    apply(puzzle: PuzzleState): void {
        for (const step of this.steps) {
            puzzle.apply(step);
        }
    }

    toString(): string {
        return this.steps.map(step => " " + step.toString()).join("");
    }
}

export class StepSequenceCursor {
    sequence: StepSequence;
    puzzle: PuzzleState;
    index: number = 0;

    constructor(sequence: StepSequence, puzzle: PuzzleState = new PuzzleState()) {
        this.sequence = sequence;
        this.puzzle = new PuzzleState(puzzle.fields);
    }

    hasNext(): boolean {
        return this.index < this.sequence.steps.length;
    }

    currentState(): PuzzleState {
        return this.puzzle;
    }

    currentStep(): Step {
        return this.sequence.steps[this.index];
    }

    next(): void {
        this.puzzle.apply(this.currentStep());
        this.index++;
    }

    toString(hideSequence: boolean = false): string {
        let result = "";

        if (!hideSequence) {
            result = this.sequence.toString() + "\n";
            if (this.hasNext()) {
                result += " ".repeat(1 + this.index * 3) + "^";
            }
            result += "\n\n";
        }

        result += this.puzzle.toString(this.hasNext() ? this.currentStep() : null);
        return result;
    }
}

export class PuzzleSolver {
    puzzle: PuzzleState;
    target: PuzzleState;
    solution: StepSequence | null = null;

    constructor(puzzle: PuzzleState, target: PuzzleState = new PuzzleState()) {
        this.puzzle = puzzle;
        this.target = target;
    }

    solveAdaptive(): void {
        for (const maxDepth of [5, 10, 15, 20, 24]) {
            this.solve(maxDepth);
            if (this.solution !== null) {
                return;
            }
        }
    }

    solve(maxDepth: number): void {
        if (this.puzzle.fields.every((f, i) => this.target.fields[i] === f)) {
            this.solution = new StepSequence([]);
            return;
        }

        let bestSolution: Step[] | null = null;
        const currentPath: Step[] = [];
        const state = new PuzzleState(this.puzzle.fields);
        let stepCount = 0;

        const recurse = (depth: number): boolean => {
            if (depth > maxDepth) {
                return false;
            }

            for (const step of state.possibleSteps(currentPath[currentPath.length - 1] || null)) {
                stepCount++;

                state.apply(step);
                currentPath.push(step);

                if (state.fields.every((f, i) => this.target.fields[i] === f)) {
                    bestSolution = [...currentPath];
                    maxDepth = depth;

                    state.apply(step.inverse());
                    currentPath.pop();
                    return false; // Continue to find better solution
                }

                const found = recurse(depth + 1);
                if (found) {
                    return true;
                }

                state.apply(step.inverse());
                currentPath.pop();
            }

            return false;
        };

        recurse(0);

        if (bestSolution) {
            this.solution = new StepSequence(bestSolution);
        }
    }
}

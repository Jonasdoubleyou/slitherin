from unittest import TestCase, main
from algorithm import StepDirection, Step, PuzzleState, StepSequence, SIZE_X

class TestStepDirection(TestCase):
    def test_inverse(self):
        self.assertEqual(StepDirection.DOWN.inverse(), StepDirection.UP)
        self.assertEqual(StepDirection.UP.inverse(), StepDirection.DOWN)
        self.assertEqual(StepDirection.LEFT.inverse(), StepDirection.RIGHT)
        self.assertEqual(StepDirection.RIGHT.inverse(), StepDirection.LEFT)

    def test_isXY(self):
        self.assertTrue(StepDirection.LEFT.is_x())
        self.assertTrue(StepDirection.RIGHT.is_x())
        self.assertFalse(StepDirection.UP.is_x())
        self.assertFalse(StepDirection.DOWN.is_x())

        self.assertFalse(StepDirection.LEFT.is_y())
        self.assertFalse(StepDirection.RIGHT.is_y())
        self.assertTrue(StepDirection.UP.is_y())
        self.assertTrue(StepDirection.DOWN.is_y())

        self.assertFalse(StepDirection.LEFT.is_opposite())
        self.assertTrue(StepDirection.RIGHT.is_opposite())
        self.assertFalse(StepDirection.UP.is_opposite())
        self.assertTrue(StepDirection.DOWN.is_opposite())

    def test_stride(self):
        self.assertEqual(StepDirection.UP.stride(), -SIZE_X)
        self.assertEqual(StepDirection.DOWN.stride(), SIZE_X)
        self.assertEqual(StepDirection.LEFT.stride(), -1)
        self.assertEqual(StepDirection.RIGHT.stride(), 1)

    def test_offset(self):
        self.assertEqual(StepDirection.UP.offset_in_dir(0), 0) 
        self.assertEqual(StepDirection.UP.offset_in_dir(1), 0)
        self.assertEqual(StepDirection.UP.offset_in_dir(2), 0)
        self.assertEqual(StepDirection.UP.offset_in_dir(3), 1)
        self.assertEqual(StepDirection.UP.offset_in_dir(6), 2)
        self.assertEqual(StepDirection.UP.offset_in_dir(8), 2)

        self.assertEqual(StepDirection.DOWN.offset_in_dir(8), 0)
        self.assertEqual(StepDirection.DOWN.offset_in_dir(0), 2)

        self.assertEqual(StepDirection.RIGHT.offset_in_dir(0), 2) 
        self.assertEqual(StepDirection.RIGHT.offset_in_dir(1), 1)
        self.assertEqual(StepDirection.RIGHT.offset_in_dir(2), 0)
        self.assertEqual(StepDirection.RIGHT.offset_in_dir(3), 2)
        self.assertEqual(StepDirection.RIGHT.offset_in_dir(6), 2)
        self.assertEqual(StepDirection.RIGHT.offset_in_dir(8), 0)

        self.assertEqual(StepDirection.LEFT.offset_in_dir(8), 2)
        self.assertEqual(StepDirection.LEFT.offset_in_dir(2), 2)
        self.assertEqual(StepDirection.LEFT.offset_in_dir(0), 0)
        
    def test_at_border(self):
        self.assertFalse(StepDirection.UP.is_at_border(0))
        self.assertFalse(StepDirection.UP.is_at_border(3))
        self.assertTrue(StepDirection.UP.is_at_border(6))
        self.assertTrue(StepDirection.UP.is_at_border(7))
        self.assertTrue(StepDirection.UP.is_at_border(8))

        self.assertTrue(StepDirection.DOWN.is_at_border(0))
        self.assertFalse(StepDirection.DOWN.is_at_border(3))

        self.assertFalse(StepDirection.LEFT.is_at_border(0))
        self.assertFalse(StepDirection.LEFT.is_at_border(1))
        self.assertTrue(StepDirection.LEFT.is_at_border(2))
        self.assertTrue(StepDirection.LEFT.is_at_border(5))
        self.assertTrue(StepDirection.LEFT.is_at_border(8))

        self.assertTrue(StepDirection.RIGHT.is_at_border(0))
        self.assertFalse(StepDirection.RIGHT.is_at_border(8))

class PuzzleStateTest(TestCase):
    def eq(self, a: PuzzleState, b: PuzzleState):
        self.assertListEqual(a.fields, b.fields)
        self.assertEqual(a.free_pos, b.free_pos)

    def test_apply(self):
        state = PuzzleState(
            (1, 2, 3,
             4, 5, 6,
             7, 8, 0))

        state.apply(Step(StepDirection.DOWN, 1))
        self.eq(state, PuzzleState(
            (1, 2, 3,
             4, 5, 0,
             7, 8, 6)))
        
        state.apply(Step(StepDirection.UP, 1))
        self.eq(state, PuzzleState(
            (1, 2, 3,
             4, 5, 6,
             7, 8, 0)))
        
        state.apply(Step(StepDirection.DOWN, 2))
        self.eq(state, PuzzleState(
            (1, 2, 0,
             4, 5, 3,
             7, 8, 6)))
        
        state.apply(Step(StepDirection.UP, 1))
        self.eq(state, PuzzleState(
            (1, 2, 3,
             4, 5, 0,
             7, 8, 6)))
        
        state.apply(Step(StepDirection.RIGHT, 2))
        self.eq(state, PuzzleState(
            (1, 2, 3,
             0, 4, 5,
             7, 8, 6)))
        
        state.apply(Step(StepDirection.UP, 1))
        self.eq(state, PuzzleState(
            (1, 2, 3,
             7, 4, 5,
             0, 8, 6)))
        
        state.apply(Step(StepDirection.LEFT, 1))
        self.eq(state, PuzzleState(
            (1, 2, 3,
             7, 4, 5,
             8, 0, 6)))

class StepSequenceTest(TestCase):
    def eq(self, a: PuzzleState, b: PuzzleState, msg: str):
        self.assertListEqual(a.fields, b.fields, msg)
        self.assertEqual(a.free_pos, b.free_pos, msg)

    def test_random(self):
        for i in range(0, 1000):
            sequence = StepSequence(list())
            sequence.fillRandom(5)
            
            puzzle = PuzzleState()
            sequence.apply(puzzle)
            sequence.invert().apply(puzzle)
            self.eq(puzzle, PuzzleState(), sequence.to_str())
main()
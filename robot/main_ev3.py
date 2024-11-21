#!/usr/bin/env pybricks-micropython

# Main entrypoint to run the program on a LEGO EV3
# This program requires LEGO EV3 MicroPython v2.0 or higher.
# Click "Open user guide" on the EV3 extension tab for more information.

from pybricks.hubs import EV3Brick
from pybricks.ev3devices import (Motor, TouchSensor, ColorSensor,
                                 InfraredSensor, UltrasonicSensor, GyroSensor)
from pybricks.parameters import Port, Stop, Direction, Button, Color
from pybricks.tools import wait, StopWatch, DataLog
from pybricks.robotics import DriveBase
from pybricks.media.ev3dev import SoundFile, ImageFile, Font
from pybricks.messaging import BluetoothMailboxServer, TextMailbox

import json

from ui import PuzzleUI
from algorithm import PuzzleState, Step, StepDirection

# ------- Configuration --------------------
# The angle the motor turns in each direction
TILT_X = 220
TILT_Y = 380
# The speed in angle/s of the motor
SPEED_X = 280
SPEED_Y = 700
# When turning back to the center position, the motor "overshoots" by this angle,
# to account for slack in the gears
OVERSHOOT_X = 40
OVERSHOOT_Y = 50

# The speed by which the lifter moves
SPEED_LIFTER = 1200
# The angle by which the lifter moves up or down
OFFSET_LIFTER = 370
# The time in seconds by which the robot waits for tiles to slide
WAIT_FOR_SLIDE = 0.3

# Interface for the EV3 environment
# This connects the abstract UI + algorithms to the EV3
class UIController:
    ev3 = EV3Brick()
    clock = StopWatch()
    rowIdx = 0

    def __init__(self):
        small_font = Font(size=15, bold=True, monospace=True)
        self.ev3.screen.set_font(small_font)

        self.axis_x = Motor(Port.A)
        self.axis_x.reset_angle(0)
        self.axis_y = Motor(Port.B)
        self.axis_y.reset_angle(0)
        self.lifter = Motor(Port.C)
        self.lifter.reset_angle(0)
        self.lock_even = None

    def init(self):
        # self.connect_bluetooth()
        # return

        while True:
            selection = self.select("Sliding Puzzle", ["Start", "Calibrate Axis", "Calibrate Lifter", "Connect"])
            if selection == "Calibrate Axis":
                self.calibrate_axis()
            if selection == "Calibrate Lifter":
                self.calibrate_lifter()
            elif selection == "Start":
                PuzzleUI(self).init()
            elif selection == "Connect":
                self.connect()

    # ---- Calibration -------------------------------------

    def calibrate_lifter(self):
        self.cls()
        self.print("   ^   ")
        self.print(" LIFT  ")
        self.print("   v   ")
        self.print("")
        self.print("Move till all tiles are")
        self.print("at the same height")

        while True:
            btn = self.wait_for_button()
            if btn == Button.DOWN:
                self.lifter.run_angle(SPEED_LIFTER, 60)
            elif btn == Button.UP:
                self.lifter.run_angle(SPEED_LIFTER, -60)
            elif btn == Button.CENTER:
                self.lifter.reset_angle(0)
                self.lock_even = False
                self.lock(True)
                self.lock(False)
                self.lock(True)
                self.lock(False)
                self.lock(True)
                self.lock(False)
                return

    def calibrate_axis(self):
        self.cls()
        self.print("   ^   ")
        self.print("<     >")
        self.print("   v   ")
        self.print("")
        self.print("Move till the axis are")
        self.print("at 0 degree")

        while True:
            btn = self.wait_for_button()
            if btn == Button.DOWN:
                self.do_tilt_y(10)
            elif btn == Button.UP:
                self.do_tilt_y(-10)
            elif btn == Button.LEFT:
                self.do_tilt_x(-10)
            elif btn == Button.RIGHT:
                self.do_tilt_x(10)
            elif btn == Button.CENTER:
                break

        self.axis_x.reset_angle(0)
        self.axis_y.reset_angle(0)

        self.do_tilt_x(TILT_X)
        self.sleep(1)
        self.reset_tilt()
        self.do_tilt_x(-TILT_X)
        self.sleep(1)
        self.reset_tilt()
        self.do_tilt_y(TILT_Y)
        self.sleep(1)
        self.reset_tilt()
        self.do_tilt_y(-TILT_Y)
        self.sleep(1)
        self.reset_tilt()

    # ---- Interface to UI -------------------------------------

    def cls(self):
        self.ev3.screen.clear()

    def print(self, text: str):
        self.ev3.screen.print(text.rstrip())

    def time_ms(self):
        return self.clock.time()
    
    def sleep(self, duration):
        wait(duration * 1000)

    def wait_for_enter(self):
        self.print("Go?")
        while self.wait_for_button() != Button.CENTER:
            wait(10)

    def select(self, title, values):
        selectedIdx = 0
        while True:
            self.cls()
            self.print(title)
            for (idx, value) in enumerate(values):
                self.print((" + " if idx == selectedIdx else "    ") + value)

            btn = self.wait_for_button()
            if btn == Button.UP:
                if selectedIdx >= 1:
                    selectedIdx -= 1
            elif btn == Button.DOWN:
                if selectedIdx <= len(values) - 1:
                    selectedIdx += 1
            elif btn == Button.CENTER:
                return values[selectedIdx]

    def is_button_pressed(self):
        return any(self.ev3.buttons.pressed())

    def wait_for_button(self):
        while len(self.ev3.buttons.pressed()) != 1:
            wait(10)
        btn = self.ev3.buttons.pressed()[0]
        while self.is_button_pressed():
            wait(10)
        return btn

    # ------- Interface to Algorithm --------------------------

    def do_move(self, step: Step, state: PuzzleState):
        # Check for interrupt by user and stop
        if self.is_button_pressed():
            self.cls()
            while self.is_button_pressed():
                wait(10)
            selection = self.select("Stopped", ["Resume", "Finish"])
            if selection == "Finish":
                raise Exception("Abort")
            self.cls()

        # If the target is an even position, lock it.
        # This inversely unlocks all tiles moving to
        target_even = (state.free_pos % 2) == 0
        # Lock-Unlock to bring all tiles into proper position
        self.lock(not target_even)
        self.lock(target_even)

        if step.direction == StepDirection.UP:
            self.do_tilt_y(-TILT_Y)
        elif step.direction == StepDirection.DOWN:
            self.do_tilt_y(TILT_Y)
        elif step.direction == StepDirection.LEFT:
            self.do_tilt_x(-TILT_X)
        elif step.direction == StepDirection.RIGHT:
            self.do_tilt_x(TILT_X)
        
        if step.move_count == 1:
            self.sleep(WAIT_FOR_SLIDE)

        for i in range(1, step.move_count):
            self.lock(not self.lock_even)
            self.sleep(WAIT_FOR_SLIDE)

        if step.direction.is_x():
            self.reset_tilt_x()
        if step.direction.is_y():
            self.reset_tilt_y()
           
    def finish(self):
        self.reset_tilt()
        self.unlock()

    # ------- Axis Controller -------------------------------

    def print_move(self, move: str):
        self.ev3.screen.draw_text(100, 30, move)

    def do_tilt_x(self, degree):
        self.print_move("RIGHT" if degree > 0 else "LEFT")
        self.axis_x.run_angle(SPEED_X, -degree)
    
    def do_tilt_y(self, degree):
        self.print_move("DOWN" if degree > 0 else "UP")
        self.axis_y.run_angle(SPEED_Y, degree)

    def reset_tilt(self):
        self.reset_tilt_x()
        self.reset_tilt_y()

    def reset_tilt_x(self):
        x_correction = -OVERSHOOT_X if self.axis_x.angle() > 0 else OVERSHOOT_X
        self.axis_x.run_target(SPEED_X, x_correction)
        self.axis_x.run_target(SPEED_X, 0)

    def reset_tilt_y(self):
        y_correction = -OVERSHOOT_Y if self.axis_y.angle() > 0 else OVERSHOOT_Y
        self.axis_y.run_target(SPEED_Y, y_correction)
        self.axis_y.run_target(SPEED_Y, 0)
    
    # -------- Lifter Controller --------------------------------

    def lock(self, even):
        if even == self.lock_even:
            return

        if even:
            self.lifter.run_target(SPEED_LIFTER, -OFFSET_LIFTER)
        else:
            self.lifter.run_target(SPEED_LIFTER, OFFSET_LIFTER)
        
        self.lock_even = even

    def unlock(self):
        self.lifter.run_target(SPEED_LIFTER, 0)

    # ----------- Server Connection -----------------------

    # Communicate with the http server via files

    def write_status(self):
        status = { "status": "waiting for command" }
        with open("./status.json", "w") as f:
            f.write(json.dumps(status))

    def read_command(self):
        with open("./command.json", "r") as f:
            return json.loads(f.read())
        
    def reset_command(self):
        with open("./command.json", "w") as f:
            f.write('{ "command": "wait" }')

    def connect(self):
        self.write_status()
        self.reset_command()


        while not self.is_button_pressed():
            self.cls()
            self.print("Waiting for commands")

            command = self.read_command()
            cmd = command["command"]
            if cmd == "solve":
                self.reset_command()
                self.connect_solve(command["pattern"])
            elif cmd == "wait":
                pass
            else:
                raise Exception("Unknown command: " + cmd)
            self.sleep(1)
    
    def connect_solve(self, pattern):
        print("Solving" + str(pattern))

        ui = PuzzleUI(self)
        ui.puzzle = PuzzleState(pattern)
        try:
            ui.run()
        finally:
            pass
        

UIController().init()



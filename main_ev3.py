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

from ui import PuzzleUI
from algorithm import Step, StepDirection

TILT_X = 60
SPEED_X = 60
TILT_Y = 130
SPEED_Y = 60

SPEED_LIFTER = 240
OFFSET_LIFTER = 2 * 240

# Interface to the EV3 environment
class UIController:
    ev3 = EV3Brick()
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
        self.lock_middle = False

    def init(self):
        while True:
            selection = self.select("Sliding Puzzle", ["Start", "Axis", "Lifter"])
            if selection == "Axis":
                self.calibrate_axis()
            if selection == "Lifter":
                self.calibrate_lifter()
            elif selection == "Start":
                self.axis_x.reset_angle(0)
                self.axis_y.reset_angle(0)

                PuzzleUI(self).init()

    def calibrate_lifter(self):
        self.cls()
        self.print("   ^   ")
        self.print(" LIFT  ")
        self.print("   v   ")

        while True:
            btn = self.wait_for_button()
            if btn == Button.DOWN:
                self.lifter.run_angle(SPEED_LIFTER, 60)
            elif btn == Button.UP:
                self.lifter.run_angle(SPEED_LIFTER, -60)
            elif btn == Button.CENTER:
                return

    def calibrate_axis(self):
        self.cls()
        self.print("   ^   ")
        self.print("<     >")
        self.print("   v   ")

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
                return
        

    def wait_for_button(self):
        while len(self.ev3.buttons.pressed()) != 1:
            wait(10)
        btn = self.ev3.buttons.pressed()[0]
        while any(self.ev3.buttons.pressed()):
            wait(10)
        return btn

    # ---- Interface ----
    def cls(self):
        self.ev3.screen.clear()

    def print(self, text: str):
        self.ev3.screen.print(text.rstrip())

    def time_ms(self):
        return 0 # TODO
    
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
    
    def print_move(self, move: str):
        self.ev3.screen.draw_text(100, 30, move)

    def do_tilt_x(self, degree):
        self.print_move("RIGHT" if degree > 0 else "LEFT")
        self.axis_x.run_angle(SPEED_X, -degree)
    
    def do_tilt_y(self, degree):
        self.print_move("DOWN" if degree > 0 else "UP")
        self.axis_y.run_angle(SPEED_Y, -degree)


    def reset_tilt(self):
        self.axis_x.run_target(SPEED_X, 0)
        self.axis_y.run_target(SPEED_Y, 0)
    
    def lock(self, middle):
        if middle == self.lock_middle:
            return

        if middle:
            self.lifter.run_angle(SPEED_LIFTER, -OFFSET_LIFTER)
        else:
            self.lifter.run_angle(SPEED_LIFTER, OFFSET_LIFTER)
        
        self.lock_middle = middle

    def do_move(self, step: Step):
        if step.direction == StepDirection.UP:
            self.do_tilt_y(-TILT_Y)
        elif step.direction == StepDirection.DOWN:
            self.do_tilt_y(TILT_Y)
        elif step.direction == StepDirection.LEFT:
            self.do_tilt_x(-TILT_X)
        elif step.direction == StepDirection.RIGHT:
            self.do_tilt_x(TILT_X)
        
        self.lock(not self.lock_middle)

        self.sleep(1)

        self.reset_tilt()
           


UIController().init()



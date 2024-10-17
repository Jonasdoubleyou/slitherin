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

# Interface to the EV3 environment
class UIController:
    ev3 = EV3Brick()
    rowIdx = 0

    def __init__(self):
        small_font = Font(size=15, bold=True, monospace=True)
        self.ev3.screen.set_font(small_font)

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
        self.rowIdx = 0

    def print(self, text: str):
        for row in text.rstrip().split("\n"):
            self.ev3.screen.draw_text(5, 5 + 15 * self.rowIdx, row)
            self.rowIdx += 1
            if self.rowIdx > 9:
                self.rowIdx = 0
                self.cls()

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


PuzzleUI(UIController()).init()



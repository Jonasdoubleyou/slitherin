# Sliding Puzzle Solver for LEGO Mindstorms

Solves a 3x3 sliding puzzle using LEGO Mindstorms. 

# The Robot

The `/robot` folder contains a micro-python program to control a LEGO Mindstorms EV3. To run it on an EV3, install the "LEGO MINDSTORMS EV3 MicroPython" extension in VS Code, open `main_ev3.py` and "Run on EV3" from the Debugger tab. Alternatively to develop the algorithm, `main_standalone.py` can also be used to run it from a terminal program. Run `test.py` to run some small unit tests.

## Installation

TODO

```
sudo cp http_runner.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl start http_runner
sudo systemctl enable http_runner
```

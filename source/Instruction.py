# Project: Reti Debugger
# Author: Robin Sonner
# License: MIT (view License.txt)
# inspired by the lectures "Technische Informatik" and "Betriebssysteme" at Albert-Ludwig Universität, Freiburg

from dataclasses import dataclass


@dataclass
class Instruction:
    line_number: int  # Number of the line
    line_raw: str  # Unprocessed line
    command: str  # Name of the Method
    arguments: tuple  # Values of the Arguments to be given to the method

# Project: Reti Debugger
# Author: Robin Sonner
# License: MIT (view License.txt)
# inspired by the lectures "Technische Informatik" and "Betriebssysteme" at Albert-Ludwig Universität, Freiburg

from StartGUI import StartGUI
from Assembler import Assembler
from Debugger import Debugger
from DebuggerGUI import DebuggerGUI
from Instruction import Instruction
import tkinter as tk


class GUIController:
    """Class manages the transition from the StartGUI to the DebuggerGUI"""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.start_gui = None
        self.debugger_gui = None

    def open_start_gui(self) -> None:
        """Opens the StartGUI"""
        # remove everything that DebuggerGUI placed inside the Root Window
        for widget in self.root.winfo_children():
            widget.destroy()
        self.start_gui = StartGUI(self)

    def open_debugger_gui(
        self,
        memory: dict[int, int],
        instructions: list[Instruction],
        debug: bool,
        raw_text: list[str],
    ) -> None:
        """Opens the DebuggerGUI

        Args:
            memory (dict[int, int]): Represents the memory of the Assembler
            instructions (list[instruction]): parsed program file
            debug (bool): User Option to show more/less debug messages
            raw_text (list[str]): Content of the program file. Every string in the list stores one line of text.
        """
        # remove everything that StartGUI placed inside the Root Window
        for widget in self.root.winfo_children():
            widget.destroy()

        # prepare the backend
        assembler = Assembler(s=memory)
        assembler.max_pc = len(instructions)
        debugger = Debugger(assembler, debug, instructions, raw_text)

        # prepare the frontend
        self.debugger_gui = DebuggerGUI(self, debugger)

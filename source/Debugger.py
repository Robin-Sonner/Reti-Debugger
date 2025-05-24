# Project: Reti Debugger
# Author: Robin Sonner
# License: MIT (view License.txt)
# inspired by the lectures "Technische Informatik" and "Betriebssysteme" at Albert-Ludwig Universität, Freiburg

from dataclasses import dataclass
from Assembler import (
    Assembler,
    REGISTERS,
    TERMINATE,
)
from Instruction import Instruction
import tkinter as tk
from tkinter.messagebox import showerror
from copy import deepcopy
from TkinterHelper import Text

RESET = "\nI will reset this field to a valid value."


@dataclass
class Debugger:
    assembler: Assembler
    debug: bool
    instructions: list[Instruction]
    raw_text: list[str]
    previous_line: int | None = None
    do_auto_step_fast: bool = False
    do_auto_step_slow: bool = False
    finished: bool = False
    assembler_backup_stack = []

    def compute(self, instruction: Instruction, text: Text) -> Text:
        """applies the given instruction to the Assembler

        Args:
            instruction (Instruction): instruction to be computed
            text (Text): text field to enter status messages

        Returns:
            Text: modified text field
        """
        command = getattr(self.assembler, instruction.command)
        increment_pc = command(*instruction.arguments)
        if increment_pc:
            self.assembler.pc += 1
        text = self.assembler_message(text)
        memory = ", ".join(
            f"{key}: {value}" for key, value in sorted(self.assembler.s.items())
        )
        if memory == "":
            memory = "{}"
        text.append(
            f"\nCurrent State of the Machine is:"
            f"\nregister_states = {', '.join(f"{reg}={getattr(self.assembler, attr)}" for reg, attr in REGISTERS.items())}"
            f"\nMemory= {memory}\n",
        )

        if instruction.line_raw in TERMINATE:
            text.append(
                f"\nTerminate Instruction '{instruction.line_raw}' encountered on line {instruction.line_number}. I will now terminate the Script.\n",
            )
            self.finished = True

        if self.assembler.pc >= len(self.instructions):
            message = (
                f"\npc={self.assembler.pc}, len={len(self.instructions)}, last={self.instructions[self.assembler.pc - 1].line_raw}\n"
                f"I reached End-Of-File before reaching a '{TERMINATE}' instruction.\n"
                f"To allow me to properly shutdown add '{TERMINATE}' as the last instruction that will be called.\n"
            )
            text.append(message)
            showerror("Assembler Error", message)
            self.finished = True

        return text

    def assembler_message(self, text: Text) -> Text:
        """Appends messages from the Assembler in the text field

        Args:
            text (Text): status text field to hold the messages

        Returns:
            Text: modified text field
        """
        if self.assembler.message != "":
            text.insert(tk.END, f"\n{self.assembler.message}")
            self.assembler.message = ""
        if self.debug and self.assembler.debug_message != "":
            text.insert(tk.END, f"\n{self.assembler.debug_message}")
            self.assembler.debug_message = ""
        return text

    def next(self, text: Text) -> tuple[int, Text]:
        """Computes the next Instruction

        Args:
            text (Text): text field to enter an error message, if needed

        Returns:
            tuple[int, Text]: wait time for the next instruction, modified text field
        """
        if not self.finished:
            self.assembler_backup_stack.append(deepcopy(self.assembler))
            try:
                text = self.compute(self.instructions[self.assembler.pc], text)
            except Exception as e:
                self.assembler = self.assembler_backup_stack.pop()
                instruction = self.instructions[self.assembler.pc]
                message = (
                    f"\nEncountered the following error:\n{str(e)}\n"
                    f"This was caught at the following instruction: '{instruction.line_raw}' at line {instruction.line_number}\n"
                    f"I will revert the assembler to the last stable state.\n"
                )
                showerror("Assembler Error", message)
                text.append(message)

        if self.do_auto_step_fast:
            return (50, text)
        elif self.do_auto_step_slow:
            return (1000, text)
        else:
            return (-1, text)

    def previous(self, text: Text) -> Text:
        """Reverts the Assembler to a previous state

        Args:
            text (Text): text field to enter status messages

        Returns:
            Text: modified text field
        """
        if not self.assembler_backup_stack:
            text.append("\nNo steps to revert.\n")
            return text

        self.assembler = self.assembler_backup_stack.pop()
        self.finished = (
            False  # At least one instruction remains (the one that was reverted)
        )
        memory = ", ".join(
            f"{key}: {value}" for key, value in sorted(self.assembler.s.items())
        )
        if memory == "":
            memory = "{}"
        text.append(
            f"\nReverted to the previous step.\n"
            f"Current State of the Machine is:"
            f"\nregister_states = {', '.join(f"{reg}={getattr(self.assembler, attr)}" for reg, attr in REGISTERS.items())}"
            f"\nMemory= {memory}\n\n",
        )
        return text

    def start(self, status_text: Text, raw_text: Text) -> tuple[Text, Text]:
        """Fills the text fields with the first status message / the raw program text

        Args:
            status_text (Text): text field to hold status messages
            raw_text (Text): text field to hold the raw program code

        Returns:
            tuple[Text, Text]: modified text fields (status_text, raw_text)
        """
        status_text.append('Assembler loaded. Press the "Next Step" Button.\n')

        for line in self.raw_text:
            raw_text.insert(tk.END, line)

        raw_text = self.show_line(raw_text)
        return (status_text, raw_text)

    def show_line(self, raw_text: Text) -> Text:
        """Shows which line of raw_text has the instruction that will be computed next

        Args:
            raw_text (Text): text field that has the raw program as content

        Returns:
            Text: modified text field
        """
        if self.finished:
            return raw_text
        current_line = self.instructions[self.assembler.pc].line_number
        raw_text.highlight_line(current_line, self.previous_line)
        self.previous_line = current_line
        return raw_text

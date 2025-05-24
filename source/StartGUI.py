# Project: Reti Debugger
# Author: Robin Sonner
# License: MIT (view License.txt)
# inspired by the lectures "Technische Informatik" and "Betriebssysteme" at Albert-Ludwig Universität, Freiburg

import tkinter as tk
from Assembler import *
from tkinter import filedialog
import tkinter.messagebox as messagebox
from Parser import create_memory, InstructionParser
from TkinterHelper import create_labeled_checkbox, Text, FONT, ToolTip
from dataclasses import dataclass, field
from Instruction import Instruction
from typing import Callable


class StartGUI:
    """Responsible for the Graphical User Interface that opens at the start of the application."""

    def __init__(self, controller) -> None:
        """Init for GUI class"""
        self.root: tk.Tk = controller.root
        self.controller = controller
        self.backend = Start()

        self.root.title(ASSEMBLER_NAME)
        self.root.geometry("1000x500")
        self.setup()

    def setup(self) -> None:
        """Builds the GUI"""
        self.startFrame = tk.Frame(master=self.root)
        self.startFrame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.setup_file_frame()
        self.setup_option_frame()
        self.setup_control_frame()

    def setup_file_frame(self) -> None:
        """setup the file frame which holds everything needed for program and memory selection"""
        self.fileFrame = tk.Frame(master=self.startFrame)
        self.programFrame = tk.Frame(master=self.fileFrame)
        self.memoryFrame = tk.Frame(master=self.fileFrame)
        self.fileFrame.pack(side=tk.TOP, fill=tk.X, expand=False)
        self.programFrame.pack(side=tk.TOP, fill=tk.X, expand=True, pady=5)
        self.memoryFrame.pack(side=tk.TOP, fill=tk.X, expand=True, pady=5)

        self.programLabel = tk.Label(
            master=self.programFrame,
            font=FONT,
            justify="left",
            anchor="w",
            text="Please select a file",
            background="gray70",
        )
        self.memoryLabel = tk.Label(
            master=self.memoryFrame,
            font=FONT,
            justify="left",
            anchor="w",
            text="Please select a file. If no file is selected all memory will be initialized with 0",
            background="gray70",
        )
        self.programButton = tk.Button(
            master=self.programFrame,
            font=FONT,
            text="Select Program to run       ",
            command=lambda: self.select_program(),
        )
        self.memoryButton = tk.Button(
            master=self.memoryFrame,
            font=FONT,
            text="Select Memory File (.json)",
            command=lambda: self.select_memory(),
        )
        self.programLabel.pack(side=tk.LEFT, fill=tk.X, expand=True, anchor="w")
        self.programButton.pack(side=tk.RIGHT, padx=10)
        self.programButton_tooltip = ToolTip(
            widget=self.programButton,
            text="Select a program to be executed. I expect a .txt file",
        )
        self.memoryLabel.pack(side=tk.LEFT, fill=tk.X, expand=True, anchor="w")
        self.memoryButton.pack(side=tk.RIGHT, padx=10)
        self.memoryButton_tooltip = ToolTip(
            widget=self.memoryButton,
            text="Optionally set the Reti memory. I expect a .json file",
        )

    def setup_option_frame(self) -> None:
        """Setup a frame with all needed checkboxes"""
        self.optionsFrame = tk.Frame(master=self.startFrame)
        self.optionsFrame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.semicolonVar = tk.BooleanVar()
        self.caseSensitivityVar = tk.BooleanVar(value=True)
        self.debugVar = tk.BooleanVar(value=True)

        create_labeled_checkbox(
            self.optionsFrame,
            "I will check if every instruction ends with a semicolon:   ",
            self.semicolonVar,
        )
        create_labeled_checkbox(
            self.optionsFrame,
            "I will be case sensitive while checking your instructions:",
            self.caseSensitivityVar,
        )
        create_labeled_checkbox(
            self.optionsFrame,
            "I will provide additional detailed debug messages:        ",
            self.debugVar,
        )

    def setup_control_frame(self) -> None:
        """Setup the control frame with all needed buttons and a text field for output messages"""
        self.controlFrame = tk.Frame(master=self.startFrame)
        self.controlFrame.pack(side=tk.TOP, fill=tk.X, expand=False)

        self.analyzeButton = tk.Button(
            master=self.controlFrame,
            font=FONT,
            text="Analyze program",
            command=lambda: self.analyze(),
        )
        self.executeButton = tk.Button(
            master=self.controlFrame,
            font=FONT,
            text="Execute program",
            state="disabled",
            command=lambda: self.execute(),
        )
        self.analyzeButton.pack(side=tk.LEFT, padx=5, pady=5)
        self.analyzeButton_tooltip = ToolTip(
            widget=self.analyzeButton,
            text="I need to parse your program, before running it. Click me to parse it",
        )
        self.executeButton.pack(side=tk.LEFT, padx=5, pady=5)
        self.executeButton_tooltip = ToolTip(
            widget=self.executeButton,
            text="Click me to open the Debugger Gui, in which the program will be run",
        )

        self.outputFrame = tk.Frame(master=self.startFrame)
        self.outputFrame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.output = Text(master=self.outputFrame, font=FONT)
        self.output.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def show_error(self, title: str, message: str) -> None:
        """Displays an error messagebox."""
        messagebox.showerror(title, message)
        self.executeButton.configure(state="disabled")

    def select_program(self) -> None:
        """Handles program file selection."""
        self.backend.select_program(self.programLabel, self.show_error)

    def select_memory(self) -> None:
        """Handles memory file selection."""
        self.backend.select_memory(self.memoryLabel, self.show_error)

    def analyze(self):
        """Analyzes the program and memory files."""
        self.backend.reset_errors()
        self.output.delete(1.0, tk.END)
        self.output = self.backend.load_memory(self.output, self.show_error)
        self.output = self.backend.parse_program(
            self.semicolonVar.get(),
            self.caseSensitivityVar.get(),
            self.output,
            self.show_error,
        )
        self.output, self.executeButton = self.backend.setup_execution(
            self.output, self.executeButton
        )

    def execute(self):
        """Executes the program."""
        self.controller.open_debugger_gui(
            self.backend.memory,
            self.backend.instructions,
            self.debugVar.get(),
            self.backend.raw_text,
        )


@dataclass
class Start:
    """Handles all backend tasks needed for StartGUI"""

    program_path: str = ""
    memory_path: str = ""
    memory: dict[int, int] = field(default_factory=dict)
    instructions: list[Instruction] = field(default_factory=list)
    raw_text: list[str] = field(default_factory=list)
    program_error: bool = False
    memory_error: bool = False

    def select_memory(self, label: tk.Label, error: Callable) -> tk.Label:
        """Handles memory file selection.

        Args:
            label (tk.Label): Memory Label to show the new memory path in the GUI
            error (Callable): error function to show any errors in the GUI

        Returns:
            tk.Label: updated Memory label
        """
        file_path = filedialog.askopenfilename(title="Select memory file")
        if not file_path:
            error("File Error", "No memory file selected")
            return label
        if not file_path.endswith(".json"):
            error("File Error", "Memory file needs to be a .json")
            return label
        self.memory_path = file_path
        label.configure(text=file_path)
        return label

    def select_program(self, label: tk.Label, error: Callable) -> tk.Label:
        """Handles program file selection.

        Args:
            label (tk.Label): Program Label to show the new memory path in the GUI
            error (Callable): error function to show any errors in the GUI

        Returns:
            tk.Label: updated Program label
        """
        file_path = filedialog.askopenfilename(title="Select program file")
        if not file_path:
            error("File Error", "No program file selected")
            return label
        if not file_path.endswith(".txt"):
            error("File Error", "Program file needs to be a .txt")
            return label
        self.program_path = file_path
        label.configure(text=file_path)
        return label

    def load_memory(self, output: Text, error: Callable) -> Text:
        """Loads memory from the memory file.

        Args:
            output (Text): Text field to write a status message

        Returns:
            Text: modified Text field
        """
        try:
            self.memory, message = create_memory(self.memory_path)
            output.append(message)
            return output
        except (SyntaxError, FileNotFoundError) as e:
            error("Parsing Error", str(e))
            self.memory_error = True
            return output

    def parse_program(
        self, semicolon_check: bool, case_sensitive: bool, output: Text, error: Callable
    ) -> Text:
        """Parses the program file.

        Args:
            semicolon_check (bool): Whether to check for semicolons in instructions.
            case_sensitive (bool): Whether to perform case-sensitive parsing.

        Returns:
            str: Status messages from the parsing process.
        """
        parser = InstructionParser(semicolon_check, case_sensitive)
        try:
            output.append(parser.read_instructions(self.program_path))
            output.append(parser.convert_commands())
            output.append(parser.convert_arguments())
        except (KeyError, ValueError) as e:
            error("Parsing Error", str(e))
            self.program_error = True

        self.instructions = parser.instructions
        self.raw_text = parser.raw_text
        return output

    def setup_execution(
        self, output: Text, execute: tk.Button
    ) -> tuple[Text, tk.Button]:
        """Checks if errors have occurred during parsing and depending on that enables/disables the execution button

        Args:
            output (Text): Text field to write status messages
            execute (tk.Button): Button which will be enabled/disabled

        Returns:
            tuple[Text, tk.Button]: modified Text field and button
        """
        if self.program_error or self.memory_error:
            output.append("An Error occurred\n")
            execute.configure(state="disabled")
        else:
            output.append(
                "Setup finished. You can now execute your program by pressing the 'Execute'-Button.\n"
            )
            execute.configure(state="normal")
        return (output, execute)

    def reset_errors(self):
        """Resets errors of the backend."""
        self.program_error = False
        self.memory_error = False

# Project: Reti Debugger
# Author: Robin Sonner
# License: MIT (view License.txt)
# inspired by the lectures "Technische Informatik" and "Betriebssysteme" at Albert-Ludwig Universität, Freiburg

import tkinter as tk
from Debugger import Debugger
from TkinterHelper import Entry, Text, txt_event, FONT, ToolTip
from Assembler import REGISTERS, MAX_REGISTER_SIZE, MAX_MEMORY_CELL_SIZE, ASSEMBLER_NAME
from ValidateAndUpdate import *


class DebuggerGUI:
    """Responsible for the Graphical User Interface after startup (see StartGUI) is completed.
    Backend Functionalities are in Debugger.py
    """

    def __init__(self, controller, debugger: Debugger) -> None:
        """Init for GUI class.

        Args:
            controller (GUIController): Provides the root window and manages the transition from DebuggerGUI to StartGUI
            register_list: list[str]
            debugger: Debugger
        """
        self.controller = controller
        self.root: tk.Tk = controller.root
        self.register_list = list(REGISTERS.keys())
        self.schedule_id = "none"  # placeholder
        self.register_entries: dict[str, tuple[Entry, Entry]] = dict()
        self.memory_cell_entries: dict[Entry, tuple[Entry, Entry]] = dict()
        self.debugger = debugger

        self.root.title(ASSEMBLER_NAME)
        self.root.geometry("1600x800")
        self.setup()
        self.status_text, self.raw_text = self.debugger.start(
            self.status_text, self.raw_text
        )

    def setup(self):
        """Setup All GUI Widgets"""
        self.input_window = tk.Frame(master=self.root)
        self.output_window = tk.Frame(master=self.root, bg="grey80")
        self.input_window.pack(side=tk.LEFT, fill=tk.Y, expand=False, pady=5, padx=5)
        self.output_window.pack(
            side=tk.RIGHT, fill=tk.BOTH, expand=True, pady=5, padx=5
        )

        self.setup_register()
        self.setup_memory()
        self.setup_debug_control()
        self.setup_assembler_control()
        self.setup_output()

    def setup_register(self):
        """Setup all Widgets of the Register Frame"""
        self.register_control = tk.Frame(master=self.input_window)
        self.register_control.pack(
            side=tk.TOP, fill=tk.BOTH, expand=True, pady=5, padx=5
        )

        register_legend = tk.Label(
            master=self.register_control,
            text="Register  |  Value (decimal)  |  Value (binary)",
            font=FONT,
            anchor="w",
        )
        register_legend.pack(side=tk.TOP)

        max_label_width = max(len(register) for register in self.register_list) + 1
        for _, register in enumerate(self.register_list):
            self.register_window = tk.Frame(
                master=self.register_control, pady=2, padx=2
            )
            self.register_window.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

            self.register_label = tk.Label(
                master=self.register_window,
                text=register,
                anchor="w",
                width=max_label_width,
                font=FONT,
            )
            self.register_label.pack(side=tk.LEFT)

            self.register_entry = Entry(
                master=self.register_window, width=12, font=FONT, justify="right"
            )
            self.register_entry.pack(side=tk.LEFT, expand=True)
            self.register_entry.set("0")
            self.register_entry_binary = Entry(
                master=self.register_window,
                width=MAX_REGISTER_SIZE,
                font=FONT,
                justify="right",
            )
            self.register_entry_binary.pack(side=tk.LEFT, expand=True)
            self.register_entry_binary.set("0" * MAX_REGISTER_SIZE)
            self.register_entries[register] = (
                self.register_entry,
                self.register_entry_binary,
            )

    def setup_memory(self):
        """Setup all Widgets of the memory frame"""
        self.memory_control = tk.Frame(master=self.input_window)
        self.memory_control.pack(side=tk.TOP, fill=tk.X, expand=True, pady=5, padx=5)

        memory_legend = tk.Label(
            master=self.memory_control,
            text="Trace  |  Memory Cell  |  Value (decimal)  |  Value (binary)",
            font=FONT,
            anchor="w",
        )
        memory_legend.pack(side=tk.TOP)

        for i in range(0, 7):
            self.memory_cell = tk.Frame(master=self.memory_control)
            self.memory_cell.pack(side=tk.TOP, fill=tk.X, expand=True, padx=2, pady=2)

            self.memory_cell_label = tk.Label(
                master=self.memory_cell, text=f"Trace {i + 1}:", font=FONT
            )
            self.memory_cell_label.pack(side=tk.LEFT, expand=False)

            self.memory_cell_select = Entry(
                master=self.memory_cell, width=12, font=FONT, justify="right"
            )
            self.memory_cell_select.pack(side=tk.LEFT, expand=True)
            self.memory_cell_select.set(i)

            self.memory_cell_value = Entry(
                master=self.memory_cell, width=12, font=FONT, justify="right"
            )
            self.memory_cell_value.pack(side=tk.LEFT, expand=True)
            self.memory_cell_value.set("0")

            self.memory_cell_value_binary = Entry(
                master=self.memory_cell,
                width=MAX_MEMORY_CELL_SIZE,
                font=FONT,
                justify="right",
            )
            self.memory_cell_value_binary.pack(side=tk.LEFT, expand=True)
            self.memory_cell_value_binary.set("0" * MAX_MEMORY_CELL_SIZE)

            self.memory_cell_entries[self.memory_cell_select] = (
                self.memory_cell_value,
                self.memory_cell_value_binary,
            )

    def setup_debug_control(self):
        """Setup a Frame to hold all buttons needed to control the debug functionalities"""
        self.control_debug = tk.Frame(master=self.input_window)
        self.control_debug.pack(side=tk.TOP, fill=tk.X, pady=5, padx=5)

        self.overwrite_control = tk.Frame(master=self.control_debug)
        self.overwrite_control.pack(side=tk.TOP, fill=tk.X)
        self.overwrite_with_decimal = tk.Button(
            master=self.overwrite_control,
            text="Inject custom\ndecimal values",
            font=FONT,
            command=lambda: self.validate_value_entries(),
        )
        self.overwrite_with_decimal_tooltip = ToolTip(
            widget=self.overwrite_with_decimal,
            text="Save the currently set decimal values and update the binary values",
        )
        self.overwrite_with_decimal.pack(side=tk.LEFT, expand=True, pady=5)

        self.overwrite_with_binary = tk.Button(
            master=self.overwrite_control,
            text="Inject custom\nbinary values",
            font=FONT,
            command=lambda: self.validate_binary_value_entries(),
        )
        self.overwrite_with_binary_tooltip = ToolTip(
            widget=self.overwrite_with_binary,
            text="Save the currently set binary values and update the decimal values",
        )
        self.overwrite_with_binary.pack(side=tk.LEFT, expand=True, pady=5)

        self.change_traces = tk.Button(
            master=self.overwrite_control,
            text="Change Traces\n",
            font=FONT,
            command=lambda: self.validate_select_entries(),
        )
        self.change_traces_tooltip = ToolTip(
            widget=self.change_traces,
            text="After editing the Traces, click me to view the content of the newly selected memory cells",
        )
        self.change_traces.pack(side=tk.LEFT, expand=True, pady=5)

        self.return_button = tk.Button(
            master=self.overwrite_control,
            font=FONT,
            text="Return to\nprogram/memory selection",
            command=lambda: self.controller.open_start_gui(),
        )
        self.return_button_tooltip = ToolTip(
            widget=self.return_button,
            text="Returning to the Selection window will reset the Reti and allow you to pick a new program to run",
        )
        self.return_button.pack(side=tk.LEFT, expand=True, pady=5)

    def setup_assembler_control(self):
        """Setup a Frame to hold all buttons needed for stepping through the assembler instructions"""
        self.control_assembler = tk.Frame(master=self.input_window)
        self.control_assembler.pack(side=tk.BOTTOM, fill=tk.X, pady=5, padx=5)
        self.next_step = tk.Button(
            master=self.control_assembler,
            text="  Next Step  \n",
            font=FONT,
            command=lambda: self.next(),
        )
        self.next_step_tooltip = ToolTip(
            widget=self.next_step, text="Executes the next instruction"
        )
        self.next_step.pack(side=tk.LEFT, expand=True)

        self.previous_step = tk.Button(
            master=self.control_assembler,
            text="Previous Step\n",
            font=FONT,
            command=lambda: self.previous(),
        )
        self.previous_step_tooltip = ToolTip(
            widget=self.previous_step, text="Revert the Reti to its previous state"
        )
        self.previous_step.pack(side=tk.LEFT, expand=True)

        self.auto_step_slow = tk.Button(
            master=self.control_assembler,
            text="  Auto Step  \nslow",
            font=FONT,
            command=lambda: self.call_auto_step_slow(),
        )
        self.auto_step_slow_tooltip = ToolTip(
            widget=self.auto_step_slow,
            text="Execute one Instruction per second. Stop by pressing 'Pause'",
        )
        self.auto_step_slow.pack(side=tk.LEFT, expand=True)

        self.auto_step_fast = tk.Button(
            master=self.control_assembler,
            text="  Auto Step  \nfast",
            font=FONT,
            command=lambda: self.call_auto_step_fast(),
        )
        self.auto_step_fast_tooltip = ToolTip(
            widget=self.auto_step_fast,
            text="Execute one Instruction per 50ms. Stop by pressing 'Pause'",
        )
        self.auto_step_fast.pack(side=tk.LEFT, expand=True)

        self.pause = tk.Button(
            master=self.control_assembler,
            text="    Pause    \n",
            font=FONT,
            command=lambda: self.call_pause(),
        )
        self.pause_tooltip = ToolTip(widget=self.pause, text="Stop Auto Stepping")
        self.pause.pack(side=tk.LEFT, expand=True)

    def setup_output(self):
        """Setups the output window"""
        # Configure raw_text_frame
        self.raw_text_frame = tk.Frame(master=self.output_window)
        self.raw_text_frame.grid(row=1, column=0, columnspan=2, sticky="nsew")
        self.raw_text_frame.grid_rowconfigure(0, weight=1)
        self.raw_text_frame.grid_columnconfigure(0, weight=1)

        self.raw_text_scrollbar = tk.Scrollbar(
            master=self.raw_text_frame, orient="vertical"
        )
        self.raw_text_hscrollbar = tk.Scrollbar(
            master=self.raw_text_frame, orient="horizontal"
        )

        self.raw_text = Text(
            master=self.raw_text_frame,
            font=FONT,
            height=20,
            yscrollcommand=self.raw_text_scrollbar.set,
            xscrollcommand=self.raw_text_hscrollbar.set,
            wrap="none",
        )

        self.raw_text_scrollbar.grid(row=0, column=1, sticky="ns")
        self.raw_text_hscrollbar.grid(row=1, column=0, sticky="ew")
        self.raw_text.grid(row=0, column=0, sticky="nsew")

        self.raw_text_scrollbar.config(command=self.raw_text.yview)
        self.raw_text_hscrollbar.config(command=self.raw_text.xview)
        self.raw_text.bind("<Key>", lambda e: txt_event(e))

        # Configure status_frame
        self.status_frame = tk.Frame(master=self.output_window)
        self.status_frame.grid(row=0, column=0, sticky="nsew")
        self.status_frame.grid_rowconfigure(0, weight=1)
        self.status_frame.grid_columnconfigure(0, weight=1)

        self.status_text_scrollbar = tk.Scrollbar(
            master=self.status_frame, orient="vertical"
        )
        self.status_text = Text(
            master=self.status_frame,
            yscrollcommand=self.status_text_scrollbar.set,
            font=FONT,
        )
        self.status_text_scrollbar.grid(row=0, column=1, sticky="ns")
        self.status_text.grid(row=0, column=0, sticky="nsew")

        self.status_text.bind("<Key>", lambda e: txt_event(e))
        self.status_text_scrollbar.config(command=self.status_text.yview)

        # Configure grid layout for the output_window
        self.output_window.grid_rowconfigure(0, weight=1)
        self.output_window.grid_rowconfigure(1, weight=1)
        self.output_window.grid_columnconfigure(0, weight=1)

    def next(self):
        """Triggers the next step of the assembler execution"""
        wait, self.status_text = self.debugger.next(self.status_text)
        self.raw_text = self.debugger.show_line(self.raw_text)
        self.update_entries()
        if wait < 0:
            pass
        else:
            self.schedule_id = self.root.after(wait, self.next)

    def previous(self):
        """Undo for the last step of the assembler execution"""
        self.status_text = self.debugger.previous(self.status_text)
        self.raw_text = self.debugger.show_line(self.raw_text)
        self.update_entries()

    def call_auto_step_slow(self):
        """Steps automatically through all Assembler instructions"""
        self.debugger.do_auto_step_fast = False
        self.debugger.do_auto_step_slow = True
        self.root.after_cancel(self.schedule_id)
        self.next()

    def call_auto_step_fast(self):
        """Steps automatically through all Assembler instructions"""
        self.debugger.do_auto_step_fast = True
        self.debugger.do_auto_step_slow = False
        self.root.after_cancel(self.schedule_id)
        self.next()

    def call_pause(self):
        """Disables the automatic stepping of auto_step_slow and auto_step_fast"""
        self.debugger.do_auto_step_fast = False
        self.debugger.do_auto_step_slow = False
        self.root.after_cancel(self.schedule_id)

    def update_entries(self):
        """Updates all entry fields"""
        self.register_entries = update_register_entries(
            self.register_entries, self.debugger.assembler
        )
        self.memory_cell_entries = update_memory_entries(
            self.memory_cell_entries, self.debugger.assembler
        )

    def validate_select_entries(self):
        """Validates UserInput in the select entries and updates entry fields accordingly"""
        self.memory_cell_entries = validate_select_entries(self.memory_cell_entries)
        # Update memoryentries to allow user Input to take effect
        self.memory_cell_entries = update_memory_entries(
            self.memory_cell_entries, self.debugger.assembler
        )

    def validate_value_entries(self):
        """Validate UserInput in the decimal value entries and updates entry fields accordingly"""
        self.debugger.assembler = validate_value_entries(
            self.register_entries, self.memory_cell_entries, self.debugger.assembler
        )
        # Get rid of invalid values and synchronize Binary entry fields with the new decimal entry field values
        self.update_entries()

    def validate_binary_value_entries(self):
        """Validate UserInput in the binary value entries and updates entry fields accordingly"""
        self.debugger.assembler = validate_binary_value_entries(
            self.register_entries, self.memory_cell_entries, self.debugger.assembler
        )
        # Get rid of invalid values and synchronize decimals entry fields with the new binary entry field values
        self.update_entries()

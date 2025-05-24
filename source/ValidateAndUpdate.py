# Project: Reti Debugger
# Author: Robin Sonner
# License: MIT (view License.txt)
# inspired by the lectures "Technische Informatik" and "Betriebssysteme" at Albert-Ludwig Universität, Freiburg


from Assembler import (
    Assembler,
    MAX_REGISTER_SIZE,
    REGISTERS,
    MAX_MEMORY_CELL_SIZE,
    PROGRAM_COUNTER,
    MAX_MEMORY_ADDRESS,
)
from TkinterHelper import Entry
from tkinter.messagebox import showerror


RESET = "\nI will reset this field to a valid value."


def validate_value_entries(
    register_entries: dict[str, tuple[Entry, Entry]],
    memory_cell_entries: dict[Entry, tuple[Entry, Entry]],
    assembler: Assembler,
) -> Assembler:
    """
    Validates and processes user-provided entries for registers and memory cells.
    Ensures the values fall within allowed ranges and updates the corresponding assembler attributes.

    Args:
        register_entries (dict[str, tuple[Entry, Entry]]):
             A dictionary where keys are register names and values are tuples containing entry objects.
        memory_cell_entries (dict[Entry, tuple[Entry, Entry]]):
            A dictionary where keys are memory cell selectors (Entry objects) and values are tuples of entry objects.
    Returns:
    Assembler: assembler with validated User Input
    """

    def validate_and_update(
        value_entry: Entry,
        min_value: int,
        max_value: int,
        name: str,
        error_context: str,
        update_callback,
    ) -> bool:
        """
        Helper function to validate a value and update the registers or memory cells if valid.

        Args:
            value_entry (Entry): The entry object containing the value to validate.
            min_value (int): Minimum allowed value.
            max_value (int): Maximum allowed value.
            name (str): Name of the field being validated (e.g., Register name, Memory Cell key).
            error_context (str): Context for error messages (e.g., "Register", "Memory Cell").
            update_callback (callable): Function to update the corresponding attribute or memory.

        Returns:
        bool: true if only valid values were found, else false
        """
        try:
            value = int(value_entry.get())
        except ValueError:
            showerror(
                "Input Error",
                f"The string '{value_entry.get()}' inside {error_context} '{name}' is invalid.{RESET}",
            )
            return False

        if value < min_value:
            showerror(
                "Input Error",
                f"The number '{value_entry.get()}' inside {error_context} '{name}' is lower than '{min_value}' and invalid.{RESET}",
            )
            return False

        if value > max_value:
            showerror(
                "Input Error",
                f"The number '{value_entry.get()}' inside {error_context} '{name}' is higher than '{max_value}' and invalid.{RESET}",
            )
            return False

        update_callback(value)
        return True

    # Validate register entries
    min_register_value = -(2 ** (MAX_REGISTER_SIZE - 1))
    max_register_value = 2 ** (MAX_REGISTER_SIZE - 1) - 1
    for register, entry_pair in register_entries.items():
        register_name = REGISTERS[register]

        def update_register(value):
            if register_name == PROGRAM_COUNTER[1] and not (
                0 <= value <= assembler.max_pc
            ):
                showerror(
                    "Input Error",
                    f"I only have instructions for Program Counter in [{0}, {assembler.max_pc}] and not Program Counter = {value}.{RESET}",
                )
            else:
                setattr(assembler, register_name, value)

        validate_and_update(
            entry_pair[0],
            min_register_value,
            max_register_value,
            register_name,
            "Register",
            update_register,
        )

    # Validate memory cell entries
    min_cell_value = -(2 ** (MAX_MEMORY_CELL_SIZE - 1))
    max_cell_value = 2 ** (MAX_MEMORY_CELL_SIZE - 1) - 1
    for select_entry, entry_pair in memory_cell_entries.items():
        try:
            cell_key = int(select_entry.get())
        except ValueError:
            showerror(
                "Input Error",
                f"The selector '{select_entry.get()}' for a Memory Cell is not valid.{RESET}",
            )
            continue

        def update_memory_cell(value):
            assembler.s[cell_key] = value

        validate_and_update(
            entry_pair[0],
            min_cell_value,
            max_cell_value,
            str(cell_key),
            "Memory Cell",
            update_memory_cell,
        )
    return assembler


def validate_binary_value_entries(
    register_entries: dict[str, tuple[Entry, Entry]],
    memory_cell_entries: dict[Entry, tuple[Entry, Entry]],
    assembler: Assembler,
) -> Assembler:
    """Validates and processes user-provided entries for registers and memory cells.
    Ensures the values fall within allowed ranges and updates the corresponding assembler attributes.

    Args:
        register_entries (dict[str, tuple[Entry, Entry]]):
            A dictionary where keys are register names and values are tuples containing entry objects.
        memory_cell_entries (dict[Entry, tuple[Entry, Entry]]):
            A dictionary where keys are memory cell selectors (Entry objects) and values are tuples of entry objects.
    Returns:
        Assembler: updated with validated user Input
    """

    def validate_and_convert(
        value: str, max_size: int, error_context: str
    ) -> int | None:
        """Validates a binary string and converts it to a signed integer.

        Args:
            value (str): The binary string to validate.
            max_size (int): Maximum allowed length of the binary string.
            error_context (str): Context string for error messages.

        Returns:
            int | None: The converted signed integer value if valid, None otherwise.
        """
        invalid = list(filter(lambda c: c not in "01", value))

        if invalid:
            showerror(
                "Input Error",
                f"The string '{value}' in {error_context} is not a valid binary number because it contains '{invalid}'.{RESET}",
            )
            return None

        if len(value) > max_size:
            showerror(
                "Input Error",
                f"The number '{value}' in {error_context} has too many bits (bits={len(value)}). It may only be {max_size} bits long.{RESET}",
            )
            return None

        decimal_value = int(value, 2)
        if (
            decimal_value & (1 << (len(value) - 1))
        ) != 0:  # Handle two's complement for signed integers
            decimal_value -= 1 << len(value)

        return decimal_value

    # Validate and process register entries
    for register, (_, value_entry) in register_entries.items():
        name = REGISTERS[register]
        value = value_entry.get()

        decimal_value = validate_and_convert(
            value, MAX_REGISTER_SIZE, f"Register '{name}'"
        )
        if decimal_value is None:
            continue

        if name == PROGRAM_COUNTER[1] and not (0 <= decimal_value <= assembler.max_pc):
            showerror(
                "Input Error",
                f"Program Counter must be in [{0}, {assembler.max_pc}], not {decimal_value}.{RESET}",
            )
        else:
            setattr(assembler, name, decimal_value)

    # Validate and process memory cell entries
    for select, (_, value_entry) in memory_cell_entries.items():
        key = int(select.get())
        value = value_entry.get()

        decimal_value = validate_and_convert(
            value, MAX_MEMORY_CELL_SIZE, f"Memory cell at key {key}"
        )
        if decimal_value is not None:
            assembler.s[key] = decimal_value
    return assembler


def validate_select_entries(
    memory_cell_entries: dict[Entry, tuple[Entry, Entry]]
) -> dict[Entry, tuple[Entry, Entry]]:
    """Validates the 'select' entry of the memory cell entries, which is used to determine which memory cells will have their values displayed

    Returns:
        dict[Entry, (Entry, Entry)]: memory_cell_entries with validated 'select' entries
    """
    for i, select in enumerate(memory_cell_entries.keys()):
        try:
            key = int(select.get())
        except ValueError:
            showerror(
                "Input Error",
                f"The string '{select.get()}' inside memory trace '{i}' is invalid.{RESET}",
            )
            select.set("0")
        if key < 0:
            showerror(
                "Input Error",
                f"The number '{select.get()}' inside memory trace '{i}' is negative and invalid.{RESET}",
            )
            select.set("0")
        if key > 2**MAX_MEMORY_ADDRESS:
            showerror(
                "Input Error",
                f"The number '{select.get()}' inside memory trace '{i}' is higher than MAX_MEMORY_ADDRESS={2 ** MAX_MEMORY_ADDRESS} and invalid.{RESET}",
            )
            select.set("0")
    return memory_cell_entries


def update_register_entries(
    register_entries: dict[str, tuple[Entry, Entry]], assembler: Assembler
) -> dict[str, tuple[Entry, Entry]]:
    """Updates the register entries (both decimal and binary) to reflect the  current state of the Assembler

    Returns:
        dict[str, (Entry, Entry)]: Updated the register entries
    """
    for register, entry_pair in register_entries.items():
        # Extract the internal name of the register and get the attribute
        key = REGISTERS[register]
        value = getattr(assembler, key)

        # Convert value into binary representation (as Two's complement)
        mask = (1 << MAX_REGISTER_SIZE) - 1
        value_binary = "{:0{}b}".format(value & mask, MAX_REGISTER_SIZE)

        entry_pair[0].set(str(value))
        entry_pair[1].set(str(value_binary))

    return register_entries


def update_memory_entries(
    memory_cell_entries: dict[Entry, tuple[Entry, Entry]], assembler: Assembler
) -> dict[Entry, tuple[Entry, Entry]]:
    """Updates the memory entries (both decimal and binary) to reflect the current state of the Assembler

    Returns:
        dict[Entry, tuple[Entry, Entry]]: updated memory entries
    """
    memory_cell_entries = validate_select_entries(
        memory_cell_entries
    )  # To ensure that key = int(select.get()) is valid
    for select, entry_pair in memory_cell_entries.items():
        # Extract which memory cell is selected and get the attribute
        key = int(select.get())
        value = assembler.s.get(key, 0)

        # Convert value into binary representation (as Two's complement)
        mask = (1 << MAX_MEMORY_CELL_SIZE) - 1
        value_binary = "{:0{}b}".format(value & mask, MAX_MEMORY_CELL_SIZE)

        entry_pair[0].set(str(value))
        entry_pair[1].set(str(value_binary))

    return memory_cell_entries

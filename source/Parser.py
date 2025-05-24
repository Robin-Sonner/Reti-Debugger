# Project: Reti Debugger
# Author: Robin Sonner
# License: MIT (view License.txt)
# inspired by the lectures "Technische Informatik" and "Betriebssysteme" at Albert-Ludwig Universität, Freiburg

from dataclasses import dataclass, field
from json import loads, JSONDecodeError
from Assembler import COMMANDS, REGISTERS, MAX_INTERMEDIATE_SIZE
from Instruction import Instruction


def create_memory(filepath: str) -> tuple[dict[int, int], str]:
    """
    Converts a JSON-like dictionary into a Python dictionary of type dict[int, int], that is used as memory for the Assembler.

    Arguments:
    filepath: str filepath of the json file

    Returns:
    Converted dictionary and status message: tuple[dict[int, int], str]
    """
    if filepath == "":
        return (
            {},
            "Memory path was left empty. I will initialize the memory with 0. This is not an error.\n",
        )

    try:
        with open(filepath, "r") as f:
            content = f.read()
            memory: dict[int, int] = loads(content)
            memory = {
                int(k): v for k, v in memory.items()
            }  # json.load treats keys as strings. Convert them to int
            return (memory, "Memory initialized successfully.\n")

    except JSONDecodeError:
        memory_example = """
        {
        0: 50,
        1: 3,
        30: 15,
        4: 11
        }
        """
        raise SyntaxError(
            f"Unable to decode {filepath}. File is likely not formatted correctly. See example for correct format:\n{memory_example}\n"
        )

    except FileNotFoundError:
        raise FileNotFoundError(
            f"Unable to find {filepath}. Please verify that the selected filepath exits.\n"
        )


@dataclass
class InstructionParser:
    expect_semicolon: bool = True
    case_sensitive: bool = False
    raw_text: list[str] = field(default_factory=list)
    instructions: list[Instruction] = field(default_factory=list)

    def read_instructions(self, path: str) -> str:
        """
        Builds a list of instructions that are specified in the file at <path>.
        Fills the member variables line_number, raw_line of each instruction in self.instructions

        Arguments:
        path: str filepath to the file that contains the instructions

        Returns:
        str: message
        """
        if path == "":
            raise ValueError("program file path not set.")
        with open(path, "r") as file:
            for line_number, line in enumerate(file, 1):  # Start line numbers from 1
                self.raw_text.append(line)

                # Get rid of leading/trailing white spaces, comments and empty lines
                line = line.strip()
                if line.startswith("#") or line == "":
                    continue

                # Get rid of any inline comments as well and remove any trailing white spaces that get added during inline comment removal
                line = line.split("#", 1)[0].strip()
                line = line.strip()

                if self.expect_semicolon and not line.endswith(";"):
                    raise ValueError(
                        f"There's a semicolon missing at line: '{line_number}' with content: '{line}'.\n I expect each instruction to end with a semicolon. You can deactivate this check within the GUI.\n"
                    )

                # remove the semicolon to make the output easier to work with
                line = line.rstrip(";")

                self.instructions.append(Instruction(line_number, line, "", tuple()))
        if len(self.instructions) == 0:
            raise ValueError(
                f"The file at {path} is empty. Please select a file that contains instructions.\n"
            )
        return "Instructions read successfully. Will now try to parse them.\n"

    def convert_commands(self) -> str:
        """
        Takes a list of instructions processed by read_instructions(). For every instruction fills the instruction.command member variable
        and fills instruction.arguments with the types of arguments that are required for this command

        Returns:
        str: status message
        """
        valid_commands = COMMANDS
        valid_commands_lower = {
            command.lower(): COMMANDS[command] for command in list(COMMANDS.keys())
        }
        for instruction in self.instructions:
            split = instruction.line_raw.split()
            command = split[0]
            if self.case_sensitive:
                if command not in valid_commands.keys():
                    raise KeyError(
                        f"'{command}' is not a valid command. I found this command within '{instruction.line_raw}' at line {instruction.line_number}. I am case sensitive. You can disable case sensitivity within this GUI. Here is a list of valid commands: {list(valid_commands.keys())}\n"
                    )
                parsed_command, needed_arguments = valid_commands[command]
            else:
                if command.lower() not in valid_commands_lower.keys():
                    raise KeyError(
                        f"'{command}' is not a valid command. I found this command within '{instruction.line_raw}' at line {instruction.line_number}. I am NOT case sensitive, so this is not due to a Uppercase/Lowercase Error. Here is a list of valid commands: \n{list(valid_commands.keys())}\n"
                    )
                parsed_command, needed_arguments = valid_commands_lower[command.lower()]

            instruction.command = parsed_command
            instruction.arguments = needed_arguments
        return "Parse Stage 1 of 2 completed successfully. I parsed all commands. Will now try to parse their arguments.\n"

    def convert_arguments(self) -> str:
        """
        Takes a list of instructions from convert_commands(). For every instruction fills the instruction.command member variable
        and fills instruction.arguments with the types of arguments that are required for this command

        Returns:
        str Status Message
        """
        for instruction in self.instructions:
            arguments = instruction.line_raw.split()[1:]
            needed_arguments = instruction.arguments

            if len(arguments) != len(needed_arguments):
                error = f"I expected {len(needed_arguments)} arguments but got {len(arguments)} arguments. The required arguments are: {needed_arguments}. I encountered this error in line={instruction.line_number} with content={instruction.line_raw}.\n"
                self.error = True
                return error

            parsed_arguments = list()
            for number, needed_argument in enumerate(needed_arguments):
                if needed_argument == "register":
                    parsed_argument = self.prepare_register(
                        arguments[number], instruction.line_raw, instruction.line_number
                    )
                else:
                    parsed_argument = self.prepare_integer(
                        arguments[number], instruction.line_raw, instruction.line_number
                    )
                parsed_arguments.append(parsed_argument)
            instruction.arguments = tuple(parsed_arguments)
        return "Parse Stage 2 of 2 completed successfully. I parsed all arguments.\n"

    def prepare_register(self, register: str, line_raw: str, line_number: int) -> str:
        """
        Some commands need a destination or source which can be any of the REGISTERS.
        Uses the REGISTERS dict to convert a raw register into a processed register

        arguments:
        register: str Attempts to convert this raw register into a processed register using the REGISTER dict
        line_raw: str Content of the line where instruction was found (needed for error message)
        line_number: int Line number of the instruction (needed for error message)

        returns:
        str: processed register
        """
        valid_registers = REGISTERS
        valid_registers_lower = {
            register.lower(): REGISTERS[register] for register in list(REGISTERS.keys())
        }

        if self.case_sensitive:
            if register in valid_registers.keys():
                return valid_registers[register]
            else:
                raise KeyError(
                    f"I expected one of the registers {list(REGISTERS.keys())} for the command '{line_raw.split()[0]}' but got '{register}'. Error occurred on line: {line_number}. Content of that line: '{line_raw}'. Note: I am case sensitive. You can disable case sensitivity within the GUI.\n"
                )
        else:
            register_lower = register.lower()
            if register_lower in valid_registers_lower.keys():
                return valid_registers_lower[register_lower]
            else:
                raise KeyError(
                    f"I expected one of the registers {list(REGISTERS.keys())} for the command '{line_raw.split()[0]}' but got '{register}'. Error occurred on line: {line_number}. Content of that line: '{line_raw}'. Note: I am NOT case sensitive, so this is not due to a Uppercase/Lowercase Error.\n"
                )

    def prepare_integer(
        self, integer: str, line_raw: str, line_number: int
    ) -> int | str:
        """
        Some commands need an integer. Converts the integer_string into an integer

        arguments:
        integer: str Integer to be converted to int
        line_raw: str Full Content of the line where instruction was found (needed for error message)
        line_number: int Line number of the instruction (needed for error message)

        returns:
        int converted integer
        """
        try:
            num = int(integer)
        except ValueError:
            raise ValueError(
                f"I expected an integer for the command '{line_raw.split()[0]}' but got '{integer}'. Error occurred on line: {line_number}. Content of that line: '{line_raw}'.\n"
            )

        if (
            -(2 ** (MAX_INTERMEDIATE_SIZE - 1))
            <= num
            <= 2 ** (MAX_INTERMEDIATE_SIZE - 1) - 1
        ):
            return num
        else:
            raise ValueError(
                f"I expected an integer between [{-2 ** (MAX_INTERMEDIATE_SIZE - 1)}, {2 ** (MAX_INTERMEDIATE_SIZE - 1) - 1}] but got {num}. Error occurred on line: {line_number}. Content of that line: '{line_raw}'.\n"
            )

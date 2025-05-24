# Project: Reti Debugger
# Author: Robin Sonner
# License: MIT (view License.txt)
# inspired by the lectures "Technische Informatik" and "Betriebssysteme" at Albert-Ludwig Universität, Freiburg

# Note: Should follow the specifications of "Technische Informatik" precisely (if not that's a bug, let me know).

from dataclasses import dataclass, field


# feel free to use these functions to check for Runtime Errors
def validate_register(i: int, register: str, operation: str):
    """Helper function to validate if a number falls within the register Range

    Args:
        i (int): number to be checked
        register (str): register on which the operation was performed
        operation (str): Details of the Operation
    """
    if not (-(2 ** (MAX_REGISTER_SIZE - 1)) <= i <= 2 ** (MAX_REGISTER_SIZE - 1) - 1):
        raise ValueError(
            f"Runtime Error: Register {register} out of range after {operation}."
        )


def validate_memory(i: int, operation: str):
    """Helper function to validate if a number falls within the Memory Range

    Args:
        i (int): number to be checked
        register (str): register on which the operation was performed
        operation (str): Details of the Operation
    """
    if not (0 <= i <= 2**MAX_MEMORY_ADDRESS):
        raise ValueError(
            f"Runtime Error: Memory Address {i} out of range in {operation}."
        )


# Specifies the Name of the Application
ASSEMBLER_NAME = "Reti Assembler (Technische Informatik)"

# Specifies what instruction is used to terminate the script. The Debugger will stop after executing this instructions.
TERMINATE = "JUMP 0"

# As Keys specify the Register Name as needed by the assembler specification.
# As Item specify the name of the member variable of Command Class that represents this Register
REGISTERS = {"ACC": "acc", "IN1": "in1", "IN2": "in2", "PC": "pc"}

# The Emulator needs to have a program counter which decides what instruction will be called next.
# The Program Counter has to correspond to one of the registers in REGISTERS
# The Emulator will increment the Program Counter by 1 should a function return True, else
# the Program Counter will not be incremented.
PROGRAM_COUNTER = ("PC", "pc")

# As intermediate values in commands any number with MAX_INTERMEDIATE_SIZE Bits is accepted (2er Complement, so n bit means -2^(n-1) to 2^(n-1) - 1)
MAX_INTERMEDIATE_SIZE = 22
# The Register will allow any Number with MAX_REGISTER_SIZE Bits (2er Complement, so n bit means -2^(n-1) to 2^(n-1) - 1)
MAX_REGISTER_SIZE = 32
# The Memory will allow any address from 0 to 2^(MAX_MEMORY_ADDRESS)
MAX_MEMORY_ADDRESS = 32
# The Memory will allow any Number with MAX_MEMORY_CELL_SIZE Bits (2er Complement, so n bit means -2^(n-1) to 2^(n-1) - 1)
MAX_MEMORY_CELL_SIZE = 32

# As Keys specify the command Name as needed by the assembler specification.
# As Item specify the name of the method in the command class that represents this command and the needed argument types as tuples.
# Use string "register" to specify that the Argument needs to be a key within the REGISTER Dict
# Sorry about the format. Black Autoformat is good in like 99% of all cases, but not here
COMMANDS: dict[str, tuple[str, tuple]] = {
    "LOAD": ("load", ("register", int)),  # Load from memory at index into register
    "LOADIN1": (
        "loadin1",
        ("register", int),
    ),  # Load from memory at in1 + index into register
    "LOADIN2": (
        "loadin2",
        ("register", int),
    ),  # Load from memory at in2 + index into register
    "LOADI": ("loadi", ("register", int)),  # Load immediate value into register
    "STORE": ("store", (int,)),  # Store acc into memory at index
    "STOREIN1": ("storein1", (int,)),  # Store acc into memory at in1 + index
    "STOREIN2": ("storein2", (int,)),  # Store acc into memory at in2 + index
    "MOVE": (
        "move",
        ("register", "register"),
    ),  # Move value from one register to another
    "ADD": ("add", ("register", int)),  # Add value from memory to register
    "ADDI": ("addi", ("register", int)),  # Add immediate value to register
    "SUB": ("sub", ("register", int)),  # Subtract value from memory from register
    "SUBI": ("subi", ("register", int)),  # Subtract immediate value from register
    "NOP": ("nop", ()),  # No operation, increments PC
    "OPLUSI": ("oplusi", ("register", int)),  # XOR(destination, i)
    "ANDI": ("andi", ("register", int)),  # AND(destination, i)
    "ORI": ("ori", ("register", int)),  # OR(destination, i)
    "OPLUS": ("oplus", ("register", int)),  # XOR(destination, memory[i])
    "AND": ("and_", ("register", int)),  # AND(destination, memory[i])
    "OR": ("or_", ("register", int)),  # OR(destination, memory[i])
    "JUMP": ("jump", (int,)),  # Jump by offset i
    "JUMP=": ("jump_eq", (int,)),  # Jump if acc == 0
    "JUMP!=": ("jump_ne", (int,)),  # Jump if acc != 0
    "JUMP<=": ("jump_le", (int,)),  # Jump if acc <= 0
    "JUMP>=": ("jump_ge", (int,)),  # Jump if acc >= 0
    "JUMP<": ("jump_lt", (int,)),  # Jump if acc < 0
    "JUMP>": ("jump_gt", (int,)),  # Jump if acc > 0
}


# In the following class a variable for each register needs to be declared and initialized.
# You also need to declare and define a function for each command that your Assembler will need to interpret.
# There are three extra member variables:
# 1. s: dict[int, int]. This is used as memory of the assembler. You can use it to implement store and load methods
#    Keys to positions of the dict that are not filled, will be interpreted as having the item 0 (Avoiding KeyError)
# 2. max_pc: int = 0. This will be set at runtime.
#    You may use max_pc to determine if a jump increases the Program Counter too much = Jumps to an instruction that does not exist
# 3. message: str. If you would like to print a message, then set message = "Whatever you want to print". I will print
#    your message and reset message = "" afterwards.
# 4. debug_message: str. Similar to message. I will not print and reset debug_message if debugging is turned off within the settings of the GUI
#    Note: If message and debug_message are both filled with a string and debugging is turned on, the message will be printed first, followed by the debug message
#    Note 2: After  message/debug_message a line break will be printed.
# 5. I will catch exceptions and print their error message. I will then revert the Assembler to the last stable state.
# 6. Intermediate Values are checked in the Parser. Any values that change at Runtime due to Operations like Addition and Subtraction will need to be verified
#    You can use the provided validate_register() and validate_memory() functions for that.
@dataclass
class Assembler:
    # Please do not edit these member variables
    s: dict[int, int] = field(default_factory=dict)
    max_pc: int = 0
    message: str = ""
    debug_message: str = ""
    # You may add/delete registers here
    acc: int = 0
    in1: int = 0
    in2: int = 0
    pc: int = 0

    def load(self, destination: str, i: int):
        """loads the number stored in memory[i] into the destination."""
        setattr(self, destination, self.s.get(i, 0))
        return destination != "pc"

    def loadin1(self, destination: str, i: int):
        """loads the number stored in memory[IN1 + i] into the destination."""
        setattr(self, destination, self.s.get(self.in1 + i, 0))
        validate_memory(self.in1 + i, f"LOADIN1 with i={i} and IN1={self.in1}")
        return destination != "pc"

    def loadin2(self, destination: str, i: int):
        """loads the number stored in memory[IN2 + i] into the destination."""
        setattr(self, destination, self.s.get(self.in2 + i, 0))
        validate_memory(self.in2 + i, f"LOADIN2 with i={i} and IN2={self.in2}")
        return destination != "pc"

    def loadi(self, destination: str, i: int):
        """Load value i into destination"""
        setattr(self, destination, i)
        return destination != "pc"

    def store(self, i: int):
        """stores the value of ACC in memory[i]"""
        self.s[i] = self.acc
        return True

    def storein1(self, i: int):
        """stores the value of ACC in memory[IN1 + i]"""
        self.s[self.in1 + i] = self.acc
        validate_memory(self.in1 + i, f"STOREIN1 with i={i} and IN1={self.in1}")
        return True

    def storein2(self, i: int):
        """stores the value of ACC in memory[IN2 + i]"""
        self.s[self.in2 + i] = self.acc
        validate_memory(self.in2 + i, f"STOREIN2 with i={i} and IN2={self.in2}")
        return True

    def move(self, source: str, destination: str):
        """copies the value from source to destination"""
        setattr(self, destination, getattr(self, source))
        return destination != "pc"

    def subi(self, destination: str, i: int):
        """Subtract i from destination"""
        setattr(self, destination, getattr(self, destination) - i)
        validate_register(i, destination, f"Subtraction of Intermediate Value i={i}")
        return destination != "pc"

    def addi(self, destination: str, i: int):
        """Add i to destination"""
        setattr(self, destination, getattr(self, destination) + i)
        validate_register(i, destination, f"Addition of Intermediate Value i={i}")
        return destination != "pc"

    def sub(self, destination: str, i: int):
        """Subtract value at memory[i] from destination"""
        setattr(self, destination, getattr(self, destination) - self.s.get(i, 0))
        validate_register(
            i, destination, f"Subtraction of stored Value M[{i}]={self.s.get(i, 0)}"
        )
        return destination != "pc"

    def add(self, destination: str, i: int):
        """Add value at memory[i] to destination"""
        setattr(self, destination, getattr(self, destination) + self.s.get(i, 0))
        validate_register(
            i, destination, f"Addition of stored Value M[{i}]={self.s.get(i, 0)}"
        )
        return destination != "pc"

    def oplusi(self, destination: str, i: int):
        """XOR(destination, i)"""
        setattr(self, destination, getattr(self, destination) ^ i)
        validate_register(i, destination, f"XOR with Intermediate Value i={i}")
        return destination != "pc"

    def andi(self, destination: str, i: int):
        """AND(destination, i)"""
        setattr(self, destination, getattr(self, destination) & i)
        validate_register(i, destination, f"AND with Intermediate Value i={i}")
        return destination != "pc"

    def ori(self, destination: str, i: int):
        """OR(destination, i)"""
        setattr(self, destination, getattr(self, destination) | i)
        validate_register(i, destination, f"OR with Intermediate Value i={i}")
        return destination != "pc"

    def oplus(self, destination: str, i: int):
        """XOR(destination, memory[i])"""
        setattr(self, destination, getattr(self, destination) ^ self.s.get(i, 0))
        validate_register(
            i, destination, f"XOR with stored Value M[{i}]={self.s.get(i, 0)}"
        )
        return destination != "pc"

    def and_(self, destination: str, i: int):
        """AND(destination, memory[i])"""
        setattr(self, destination, getattr(self, destination) & self.s.get(i, 0))
        validate_register(
            i, destination, f"AND with stored Value M[{i}]={self.s.get(i, 0)}"
        )
        return destination != "pc"

    def or_(self, destination: str, i: int):
        """OR(destination, memory[i])"""
        setattr(self, destination, getattr(self, destination) | self.s.get(i, 0))
        validate_register(
            i, destination, f"OR with stored Value M[{i}]={self.s.get(i, 0)}"
        )
        return destination != "pc"

    def nop(self):
        """No Operation. Will just increment PC Counter"""
        return True

    def jump_eq(self, i: int):
        """Calls self.jump[i] if self.acc=0"""
        if self.acc == 0:
            return self.jump(i)
        else:
            self.debug_message = (
                f"Jump Denied. Condition ACC == 0 not met. ACC is {self.acc}"
            )
            return True

    def jump_ne(self, i: int):
        """Calls self.jump[i] if self.acc!=0"""
        if self.acc != 0:
            return self.jump(i)
        else:
            self.debug_message = (
                f"Jump Denied. Condition ACC != 0 not met. ACC is {self.acc}"
            )
            return True

    def jump_le(self, i: int):
        """Calls self.jump[i] if self.acc<=0"""
        if self.acc <= 0:
            return self.jump(i)
        else:
            self.debug_message = (
                f"Jump Denied. Condition ACC <= 0 not met. ACC is {self.acc}"
            )
            return True

    def jump_ge(self, i: int):
        """Calls self.jump[i] if self.acc>=0"""
        if self.acc >= 0:
            return self.jump(i)
        else:
            self.debug_message = (
                f"Jump Denied. Condition ACC >= 0 not met. ACC is {self.acc}"
            )
            return True

    def jump_lt(self, i: int):
        """Calls self.jump[i] if self.acc<0"""
        if self.acc < 0:
            return self.jump(i)
        else:
            self.debug_message = (
                f"Jump Denied. Condition ACC < 0 not met. ACC is {self.acc}"
            )
            return True

    def jump_gt(self, i: int):
        """Calls self.jump[i] if self.acc>0"""
        if self.acc > 0:
            return self.jump(i)
        else:
            self.debug_message = (
                f"Jump Denied. Condition ACC > 0 not met. ACC is {self.acc}"
            )
            return True

    def jump(self, i: int):
        """Performs a jump by increasing/decreasing the program counter by the value i"""
        if self.pc + i < 0:
            raise ValueError(
                f"The Jump that you try to perform decreases the program counter too much (negative pc)."
                f"PC_new= {self.pc + i}, PC_old= {self.pc}"
            )
        elif self.pc + i > self.max_pc:
            raise ValueError(
                f"The Jump that you try to perform increases the program counter too much (I can't find"
                f" any instruction for the new PC). PC_new= {self.pc + i}, PC_old= {self.pc}"
            )
        else:
            self.pc += i
            self.debug_message = (
                f"Jump Granted. PC was PC={self.pc - i} and is now PC={self.pc}"
            )
        return False

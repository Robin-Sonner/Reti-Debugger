# Author:
Project: Reti Debugger
Author: Robin Sonner
License: MIT (view License.txt)
inspired by the lectures "Technische Informatik" and "Betriebssysteme" at Albert-Ludwig Universität, Freiburg

# Infos:
These Python scripts are used to debug Reti programs. Reti is based on Resa. Details about Resa can be found here:
Keller, J., Paul, W.J. (1995). Ein einfacher Rechner. In: Hardware Design. TEUBNER-TEXTE zur Informatik, vol 15. Vieweg+Teubner Verlag, Wiesbaden. https://doi.org/10.1007/978-3-322-93438-3_6

The Project allows (with restrictions) other assemblers to be used as well.
If you would like to to that you will need to rewrite Assembler.py to fit your Assembler.
Keep in mind that the general structure of Assembler.py must not change:
I need the constants, dicts... for Parsing and running the programs -> they need to be edited to reflect your Assembler
I need an Assembler class that has member variables for every register and member functions for every instruction -> they need to be edited to reflect your assembler

# Files
- Main.py is the entry point
- Both Assembler_TI and Assembler_BS have an AvailableInstructions.txt that contains a list of all available instructions
- Assembler_TI should follow the specifications of "Technische Informatik" precisely (if not that's a bug, let me know).
- Assembler_BS is heavily inspired by, but does NOT follow the specifications of "Betriebssysteme" precisely. Mainly the INT and RTI commands are missing (I have not implemented Interupt-Service-Routines)
- Example.txt contains an example program
- ExampleMemory.txt contains the start state of the machine's memory. It is made for Example.txt

# Start Guide:
1. to help you create a program, see available_instructions.txt and example.txt
2. Optional: You can specify initial content of the Assembler memory in a .json file like this:
	Example:
	{
	“1” : 101,
	“6” : 7,
	“23” : 98
	}
	Loads 101 in address 1, 7 in address 6, 98 in address 23 and 0 in any other address
3. Pick one of the Assembler files and overwrite the Assembler file in the Main folder with it
   You likely want to start with the smaller Assembler_TI instruction set
4. run Main.py to select your program and optionally select a memory file

# PS:
In case you like the formatting:
The Project is Auto formatted with Black: https://github.com/psf/black

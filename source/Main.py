# Project: Reti Debugger
# Author: Robin Sonner
# License: MIT (view License.txt)
# inspired by the lectures "Technische Informatik" and "Betriebssysteme" at Albert-Ludwig Universität, Freiburg

from GUIControl import GUIController
from ErrorHandler import *
import sys
import tkinter as tk

if __name__ == "__main__":
    # Initialize Error Handling
    sys.excepthook = global_exception_handler

    # Application
    root = tk.Tk()
    controller = GUIController(root)
    controller.open_start_gui()
    root.mainloop()

    # Terminate
    sys.stdout.close()
    sys.exit(0)

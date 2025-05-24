# Project: Reti Debugger
# Author: Robin Sonner
# License: MIT (view License.txt)
# inspired by the lectures "Technische Informatik" and "Betriebssysteme" at Albert-Ludwig Universität, Freiburg

from tkinter.messagebox import showerror
from sys import exit
from traceback import format_exception


def global_exception_handler(exctype, value, tb):
    """Handle otherwise unhandled exceptions"""
    err = format_exception(exctype, value, tb)
    err_msg = "".join(err)
    showerror(
        "Unknown Error",
        f"Unhandled Exception:\nI did not expect this error to occur and did not provide exception handling for it\n"
        f"If you create a bug report on github with the traceback below, I will try to help you and possible create exception handling for it (No promise though, sorry)\n"
        f"Traceback:\n\n{err_msg}\n\nThe application will now close.",
    )
    exit(1)

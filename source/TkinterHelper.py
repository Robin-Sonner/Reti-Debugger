# Project: Reti Debugger
# Author: Robin Sonner
# License: MIT (view License.txt)
# inspired by the lectures "Technische Informatik" and "Betriebssysteme" at Albert-Ludwig Universität, Freiburg

import tkinter as tk

FONT = ("Helvetica", 14)


def create_labeled_checkbox(parent: tk.Frame, text: str, variable: tk.BooleanVar):
    """Creates a checkbox, where the label is to the right

    Args:
        parent (tk.Frame): Frame in which the labeled checkbox is put
        text (str): string to put in the label
        variable (tk.BooleanVar): bool variable bound to the checkbox

    Returns:
        tk.Frame: Frame in which the label and checkbox is placed
    """
    frame = tk.Frame(parent)
    frame.pack(side=tk.TOP, fill=tk.X, pady=5, anchor="w")

    label = tk.Label(frame, font=FONT, text=text, anchor="w")
    label.pack(side=tk.LEFT, padx=5)

    checkbox = tk.Checkbutton(frame, variable=variable, font=FONT)
    checkbox.pack(side=tk.LEFT)
    return frame


def txt_event(event: tk.Event) -> str | None:
    """If bound to a tk.Text Object, allows the user to copy the content of that Text Object, but not editing it

    Args:
        event (tk.Event): event that has occurred at a text field

    Returns:
            str | None: None if event is allowed (Copy), else "break"
    """
    if (event.state == "Control_L" or event.state == 4) and event.keysym == "c":
        return
    else:
        return "break"


def highlight_line(
    text: tk.Text, current_line: int, previous_line: int | None = None
) -> tk.Text:
    """Highlights the specified line in the Text widget and removes the
    highlight from the previously highlighted line.

    Parameters:
    text (tk.Text): The text field that has a line to highlight
    current_line (int): The line number to highlight
    previous_line (int | None): The line number to remove highlighting from

    Returns:
    tk.Text: The modified text field
    """
    # Remove highlighting from the previously highlighted line
    if previous_line is not None:
        text.tag_remove("highlight", f"{previous_line}.0", f"{previous_line}.end")

    # Add highlighting to the new line
    text.tag_add("highlight", f"{current_line}.0", f"{current_line}.end")
    text.tag_config("highlight", background="yellow", font=FONT)

    # Scroll to ensure the line is visible at the top
    text.yview_moveto((current_line - 1) / int(text.index("end-1c").split(".")[0]))

    return text


class Text(tk.Text):
    """
    A subclass to tk.Text that has two additional methods:
    'highlight_line' and 'append'
    """

    def __init__(self, master, *args, **kwargs):
        tk.Text.__init__(self, master, *args, **kwargs)

    def highlight_line(self, current_line: int, previous_line: int | None = None):
        """Highlights current_line and removes the highlight from the previous_line

        Parameters:
        current_line (int): The line number to highlight
        previous_line (int | None): The line number to remove highlighting from
        """
        # Remove highlighting from the previously highlighted line
        if previous_line is not None:
            self.tag_remove("highlight", f"{previous_line}.0", f"{previous_line}.end")

        # Add highlighting to the new line
        self.tag_add("highlight", f"{current_line}.0", f"{current_line}.end")
        self.tag_config("highlight", background="yellow", font=FONT)

        # Scroll to ensure the line is visible at the top
        self.yview_moveto((current_line - 1) / int(self.index("end-1c").split(".")[0]))

    def append(self, message: str):
        """Inserts the message at the End of the Text. Then Scrolls down to the end

        Args:
            message (str): message to append to the Text
        """
        self.insert(tk.END, message)
        self.see(tk.END)


class Entry(tk.Entry):
    """
    A subclass to tk.Entry that has one additional method:
    'set(text)': replaces the previous text of the entry field with the new text
    """

    def __init__(self, master, *args, **kwargs):
        tk.Entry.__init__(self, master, *args, **kwargs)

    def set(self, text):
        """Deletes the old text from the entry field. Then insert the new text into the entry field"""
        self.delete("0", "end")
        self.insert("0", text)


# Taken from https://stackoverflow.com/questions/20399243/display-message-when-hovering-over-something-with-mouse-cursor-in-python
# Minimal changes by me to fix warning messages
class ToolTip(object):
    """
    Allows to define tooltips for buttons
    Example usage: ToolTip(widget = your_widget, text = "Hover text!")
    """

    def __init__(self, widget, text):
        self.widget = widget
        self.text = text

        def enter(_):
            self.showTooltip()

        def leave(_):
            self.hideTooltip()

        widget.bind("<Enter>", enter)
        widget.bind("<Leave>", leave)

    def showTooltip(self):
        self.tooltipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(
            True
        )  # window without border and no normal means of closing
        tw.wm_geometry(
            "+{}+{}".format(self.widget.winfo_rootx(), self.widget.winfo_rooty())
        )
        label = tk.Label(
            tw, text=self.text, background="#ffffe0", relief="solid", borderwidth=1
        ).pack()

    def hideTooltip(self):
        tw = self.tooltipwindow
        if tw:
            tw.destroy()
        self.tooltipwindow = None

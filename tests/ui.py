import pyrootutils
pyrootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)

import tkinter as tk

from loguru import logger
from sv_ttk import use_dark_theme
from string import ascii_letters
from utils.history import BidirectionalIterator

DEFAULT_PADDING = {
    "padx": 15, "pady": 15
}
TEXT_HISTORY = BidirectionalIterator()

def key_enter(event):
    if not (event.state & 0x0001): # only trigger if shift key is not also pressed (state & 0x0001 means shift is down)
        logger.info("Triggered key enter")
        submit_btn.invoke()
    return "break"

def key_arrwup(event):
    if textarea.index(tk.INSERT) == "1.0": # only trigger if cursor is already at the start of text
        logger.info("Triggered key arrow up")
        traverse_history()
    return "break"

def key_arrwdwn(event):
    if textarea.index(tk.INSERT) == textarea.index(tk.END + "-1c"): # only trigger if cursor is already at the end of text
        logger.info("Triggered key arrow down")
        traverse_history(False)
    return "break"

def key_esc(event):
    global TEXT_HISTORY
    TEXT_HISTORY.reset_iter()
    set_text()

def insert_history(text: str):
    global TEXT_HISTORY
    if text:
        if text in TEXT_HISTORY:
            TEXT_HISTORY.pop(TEXT_HISTORY.index(text))
        TEXT_HISTORY.insert(text)
        TEXT_HISTORY.reset_iter()

def traverse_history(up: bool = True):
    global TEXT_HISTORY
    # Traverse up (True) or down (False)
    if up and TEXT_HISTORY.hasnext():
        set_text(TEXT_HISTORY.next())
    elif not up and TEXT_HISTORY.hasprev():
        set_text(TEXT_HISTORY.prev())

def action_return():
    logger.info("triggered text: " + get_text(False))
    insert_history(get_text(False))
    set_text()

def get_text(process_text: bool = True):
    text = textarea.get("1.0",tk.END).strip()
    if process_text:
        VALID_PUNCTUATION = set(".!?~")
        if len(text) > 1:
            if text[-1] not in set(ascii_letters):
                if text[-1] not in VALID_PUNCTUATION:
                    text = text[:-1] + "."
            else:
                text += "."
    return text

def set_text(text: str = ""):
    textarea.delete("1.0", tk.END)
    if text: textarea.insert("1.0", text)
    textarea.mark_set("insert", tk.END + "-1c")
    logger.info(TEXT_HISTORY)

# Setting up root
root = tk.Tk()
root.title("Mouthpiece v2")
root.geometry("400x300+300+120")
use_dark_theme() # must be used after root is initalized... i think.

# Input area
textlabel = tk.ttk.Label(root, text="Enter text to inference")
textlabel.pack(**DEFAULT_PADDING)
textarea = tk.Text(root, height=1, width=40, borderwidth=5, relief=tk.FLAT, highlightthickness=0, wrap="word", bg="#424549")
textarea.pack(fill='both', expand=True, **DEFAULT_PADDING)

# Submit button
submit_btn = tk.ttk.Button(root, text="Generate Audio", command=lambda: action_return())
submit_btn.pack(**DEFAULT_PADDING)

# Model dropdown box (future feature)

# don't want to bind to just textarea, since use case for this will likely involve rapid alt-tabbing, may miss target
# binding only to root will not catch / prevent the keypress if textarea widget is focused!
root.bind('<Return>', key_enter) 
textarea.bind('<Return>', key_enter) 
root.bind("<Up>", key_arrwup)
textarea.bind("<Up>", key_arrwup)
root.bind("<Down>", key_arrwdwn)
textarea.bind("<Down>", key_arrwdwn)
root.bind("<Escape>", key_esc)
textarea.bind("<Escape>", key_esc)
root.mainloop()
import pyrootutils
pyrootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)

import threading
import tkinter as tk
import tkinter.font
import config

from os import listdir
from ctypes import windll
from pathlib import Path
from utils import pickler, audio
from utils.speech import Model
from loguru import logger
from sv_ttk import use_dark_theme
from string import ascii_letters
from utils.history import BidirectionalIterator

def key_enter(event):
    if not (event.state & 0x0001): # only trigger if shift key is not also pressed (state & 0x0001 means shift is down)
        logger.debug("Triggered key enter")
        submit_btn.invoke()
    return "break"

def key_arrwup(event):
    if textarea.index(tk.INSERT) == "1.0": # only trigger if cursor is already at the start of text
        logger.debug("Triggered key arrow up")
        traverse_history()
    return "break"

def key_arrwdwn(event):
    if textarea.index(tk.INSERT) == textarea.index(tk.END + "-1c"): # only trigger if cursor is already at the end of text
        logger.debug("Triggered key arrow down")
        traverse_history(False)
    return "break"

def key_esc(event):
    global TEXT_HISTORY
    logger.debug("Triggered key escape")
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
    print(statuslabel.cget("foreground"))
    if statuslabel.cget("foreground") == "white":
        text = get_text(False)
        processed_text = get_text()
        logger.info("Triggered text: " + processed_text)
        insert_history(text)
        set_text()
        generate_play(processed_text)
        logger.debug("Called generation daemon")

def get_text(process_text: bool = True):
    text = textarea.get("1.0",tk.END).strip()
    if process_text and text:
        VALID_PUNCTUATION = set(".!?~")
        if text[0] in set(ascii_letters):
            text = text[0].upper() + text[1:]
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

def set_status(state: int):
    if state == 1: # idle
        statuslabel.config(foreground = "white")
        statustext.set(". . .")
    elif state == 2: # loading
        statustext.set("Thinking")
        statuslabel.config(foreground = "cyan")
    elif state == 3: # playing
        statustext.set("Playing audio")
        statuslabel.config(foreground = "green")
    statuslabel.update()

def select_model(event):
    model_name = selected_model.get()
    runner = threading.Thread(target=lambda mn: load_model_preset(mn), args=(model_name,))
    runner.start()

def _callback_gore(audio_array, samplerate):
    logger.debug("Finished generating audio")
    set_status(3)
    [_ for _ in audio.mirror_audio(
        data=audio_array,
        devices=config.AUDIO_DEVICES,
        callbacks=[lambda: set_status(1) and logger.debug("Finished playing audio")],
        samplerate=samplerate
    )]

def generate_play(text: str):
    global MODEL, MODEL_POOL
    with MODEL_POOL:
        set_status(2)
        MODEL.generate_async(
            text = text,
            callback = _callback_gore
        )

def load_model_preset(name: str):
    global MODEL_PATHS, MODEL, MODEL_POOL
    with MODEL_POOL:
        set_status(2)
        del MODEL
        model_idx = MODEL_PATHS["name"].index(name)
        logger.info(f"Initializing model preset {name}")
        model_token, model_text = pickler.load_model_source(MODEL_PATHS["token"][model_idx], MODEL_PATHS["text"][model_idx])
        MODEL = Model(
            prompt_text = model_text,
            prompt_token = model_token,
            checkpoint_dir = Path(config.CHECKPOINT_DIR),
            config_name = config.MODEL_CONFIG,
            checkpoint_path = Path(config.CHECKPOINT_PATH),
            **config.MODEL_PARAMS
        )
        set_status(1)


DEFAULT_PADDING = { "padx": 15, "pady": 15 }
TEXT_HISTORY = BidirectionalIterator()
# Setting up root
root = tk.Tk()
windll.shcore.SetProcessDpiAwareness(1) # fixes blurriness
root.option_add("*Font", ("Segoe UI", 12))
root.title("Mouthpiece v2")
root.geometry("400x300+300+120")
use_dark_theme()

logger.info("Loading data")
# MODEL_BASE_PATH = (Path(config.MODELS_DIR) / config.MODEL)
# MODEL_TOKEN_PATH = MODEL_BASE_PATH.with_suffix(".npy")
# MODEL_TEXT_PATH = MODEL_BASE_PATH.with_suffix(".txt")
MODEL_PATHS = { "name": [], "token": [], "text": [] }
for filepath in Path(config.MODELS_DIR).iterdir():
    if filepath.suffix == ".npy" and filepath.stem not in MODEL_PATHS.keys():
        textpath = (filepath.parent / filepath.stem).with_suffix(".txt")
        if textpath.exists():
            MODEL_PATHS["name"].append(filepath.stem)
            MODEL_PATHS["token"].append(filepath)
            MODEL_PATHS["text"].append(textpath)
        else:
            continue
logger.debug(f"Found {len(MODEL_PATHS['name'])} model presets")
MODEL_POOL = threading.Semaphore(1)
MODEL = None

# Input area
textlabel = tk.ttk.Label(root, text="Enter text to speech")
textlabel.pack(**DEFAULT_PADDING)
textarea = tk.Text(root, height=1, width=40, borderwidth=5, relief=tk.FLAT, highlightthickness=0, wrap="word", bg="#424549")
textarea.pack(fill='both', expand=True, **DEFAULT_PADDING)

# Feedback widget
statustext = tk.StringVar()
statuslabel = tk.ttk.Label(root, textvariable=statustext)
set_status(1)
statuslabel.pack()

# Submit button
submit_btn = tk.ttk.Button(root, text="Generate Audio", command=lambda: action_return())
submit_btn.pack(**DEFAULT_PADDING)

# Model dropdown box (future feature)
options_frame = tk.ttk.Frame(root, padding="10 10 10 10", relief="groove", borderwidth=0)
options_frame.pack()
selected_model = tk.StringVar()
model_options = tk.ttk.Combobox(options_frame, textvariable=selected_model, values=MODEL_PATHS["name"], state="readonly")
model_options.set(config.MODEL)
model_options.pack(pady=10)

# don't want to bind to just textarea, since use case for this will likely involve rapid alt-tabbing, may miss target
# binding only to root will not catch / prevent the keypress if textarea widget is focused!
# definitely still crude
root.bind('<Return>', key_enter) 
textarea.bind('<Return>', key_enter) 
root.bind("<Up>", key_arrwup)
textarea.bind("<Up>", key_arrwup)
root.bind("<Down>", key_arrwdwn)
textarea.bind("<Down>", key_arrwdwn)
root.bind("<Escape>", key_esc)
textarea.bind("<Escape>", key_esc)

model_options.bind("<<ComboboxSelected>>", select_model)
threading.Thread(target=load_model_preset, args=(config.MODEL,)).start()

logger.debug("Entering TKinter mainloop")
try:
    root.mainloop()
    logger.info("Mainloop exited, stopping program")
except KeyboardInterrupt:
    logger.info("KeyboardInterrupt, stopping program")
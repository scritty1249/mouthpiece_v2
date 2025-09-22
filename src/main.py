import pyrootutils
pyrootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning) # torch distro being used has a depreceated method we don't care about.

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

class Limiter(tk.ttk.Scale):
    """ ttk.Scale sublass that limits the precision of values. """

    def __init__(self, *args, **kwargs):
        self.precision = kwargs.pop('precision')  # Remove non-std kwarg.
        self.chain = kwargs.pop('command', lambda *a: None)  # Save if present.
        super(Limiter, self).__init__(*args, command=self._value_changed, **kwargs)

    def _value_changed(self, newvalue):
        newvalue = round(float(newvalue), self.precision)
        self.winfo_toplevel().globalsetvar(self.cget('variable'), (newvalue))
        self.chain(newvalue)  # Call user specified function.

def key_enter(event):
    if not (event.state & 0x0001): # only trigger if shift key is not also pressed (state & 0x0001 means shift is down)
        logger.debug("Triggered key enter")
        submit_btn.invoke()
    return "break"

def key_arrwup(event):
    if textarea.index(tk.INSERT) == "1.0": # only trigger if cursor is already at the start of text
        logger.debug("Triggered key arrow up")
        traverse_history()

def key_arrwdwn(event):
    if textarea.index(tk.INSERT) == textarea.index(tk.END + "-1c"): # only trigger if cursor is already at the end of text
        logger.debug("Triggered key arrow down")
        traverse_history(False)

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
    if str(statuslabel.cget("foreground")) == "white" and len(get_text(False)) > 0:
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

def clamp(min_val, max_val, val):
    return min(max_val, max(min_val, val))

def select_model(event):
    global ACTIVE_NAME
    model_name = selected_model.get()
    if model_name != ACTIVE_NAME:
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
            callback = _callback_gore,
            top_p = top_p_value.get(),
            repetition_penalty = rep_pen_value.get(),
            temperature = temp_value.get()
        )

def load_model_preset(name: str):
    global MODEL_PATHS, MODEL, MODEL_POOL, ACTIVE_NAME
    with MODEL_POOL:
        set_status(2)
        del MODEL
        model_idx = MODEL_PATHS["name"].index(name)
        logger.info(f"Initializing model preset {name}")
        ACTIVE_NAME = name
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
root.geometry("400x500+300+120")
use_dark_theme()

logger.info("Loading data")
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
ACTIVE_NAME = ""

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

options_frame = tk.ttk.Frame(root, padding="10 10 10 10", relief="groove", borderwidth=0)
options_frame.pack()

# Top-P slider
top_p_label = tk.ttk.Label(options_frame, text="Top-P", justify="left", anchor=tk.W)
top_p_label.grid(row=0, column=0, sticky=tk.W, **DEFAULT_PADDING)
top_p_value = tk.DoubleVar()
top_p_value.set(0.88)
top_p_slider = Limiter(
    options_frame,
    from_= 0.7,  # Minimum value
    to = 0.95,   # Maximum value
    orient='horizontal', # Orientation: 'horizontal' or 'vertical'
    variable = top_p_value, # Link to a variable
    precision = 3
)
top_p_slider.grid(row=0, column=1, **DEFAULT_PADDING)
top_p_value_label = tk.ttk.Entry(options_frame, textvariable=top_p_value, width=3, justify="left")
top_p_value_label.grid(row=0, column=3, sticky=tk.E, **DEFAULT_PADDING)

# Temperature slider
temp_label = tk.ttk.Label(options_frame, text="Temperature", justify="left", anchor=tk.W)
temp_label.grid(row=1, column=0, sticky=tk.W, **DEFAULT_PADDING)
temp_value = tk.DoubleVar()
temp_value.set(0.84)
temp_slider = Limiter(
    options_frame,
    from_= 0.7,  # Minimum value
    to = 1,   # Maximum value
    orient='horizontal', # Orientation: 'horizontal' or 'vertical'
    variable = temp_value, # Link to a variable
    precision = 3
)
temp_slider.grid(row=1, column=1, **DEFAULT_PADDING)
temp_value_label = tk.ttk.Entry(options_frame, textvariable=temp_value, width=3, justify="left")
temp_value_label.grid(row=1, column=3, sticky=tk.E, **DEFAULT_PADDING)

# Repetition penalty slider
rep_pen_label = tk.ttk.Label(options_frame, text="Repetition Penalty", justify="left", anchor=tk.W)
rep_pen_label.grid(row=2, column=0, sticky=tk.W, **DEFAULT_PADDING)
rep_pen_value = tk.DoubleVar()
rep_pen_value.set(1.12)
rep_pen_slider = Limiter(
    options_frame,
    from_= 1,  # Minimum value
    to = 1.2,   # Maximum value
    orient='horizontal', # Orientation: 'horizontal' or 'vertical'
    variable = rep_pen_value, # Link to a variable
    precision = 3
)
rep_pen_slider.grid(row=2, column=1, **DEFAULT_PADDING)
rep_pen_value_label = tk.ttk.Entry(options_frame, textvariable=rep_pen_value, width=3, justify="left")
rep_pen_value_label.grid(row=2, column=3, sticky=tk.E, **DEFAULT_PADDING)

# Model dropdown box (future feature)
selected_model = tk.StringVar()
model_options = tk.ttk.Combobox(options_frame, textvariable=selected_model, values=MODEL_PATHS["name"], state="readonly")
model_options.set(config.MODEL)
model_options.grid(row=3, column=0, columnspan=3, **DEFAULT_PADDING)

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
# Clamping slider values
top_p_value_label.bind("<FocusOut>", lambda *args: top_p_value.set(clamp(0.7, 0.95, top_p_value.get())))
top_p_value.trace("r", lambda *args: top_p_value.set(clamp(0.7, 0.95, top_p_value.get()))) # [!] Doesn't work- value is modified AFTER preprocessed value has already been returned. Fix ASAP.

model_options.bind("<<ComboboxSelected>>", select_model)
threading.Thread(target=load_model_preset, args=(config.MODEL,)).start()

logger.debug("Entering TKinter mainloop")
try:
    root.mainloop()
    logger.info("Mainloop exited, stopping program")
except KeyboardInterrupt:
    logger.info("KeyboardInterrupt, stopping program")
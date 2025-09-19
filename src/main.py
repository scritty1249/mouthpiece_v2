import pyrootutils
pyrootutils.setup_root(__file__, indicator=".project-root", pythonpath=True, cwd=True)
from lib.fish_speech.fish_speech.models.dac.inference import generate_audio
from lib.fish_speech.fish_speech.models.text2semantic.inference import generate_tokens
from pathlib import Path
from utils import audio, pickler

import config
import tkinter as tk

# Assumes model already exists
def generate_tts(text: str):
    tokens = next(generate_tokens(  # supports loading multiple models at once, but this test only uses one
        prompt_texts = [MODEL_TEXT],
        prompt_tokens = [MODEL_TOKEN],
        text = text,
        num_samples = 1,
        checkpoint_path = Path(config.CHECKPOINT_DIR),
        **EXTRA_OPTIONS
    ))
    audio_data, samplerate = generate_audio(
        compiled_tokens = model_token, 
        checkpoint_path = config.CHECKPOINT_PATH
    )
    audio.mirror_audio(
        data = audio_data,
        devices = config.AUDIO_DEVICES,
        samplerate = samplerate
    )

def get_entry_text(*args):
    text = entry_text.get()
    if len(text) > 0:
        print("Entry text:", text)
        def runner():
            entry_button_text.set("thinking")
            root.update()
            #entry_button.update_idletasks()
            generate_tts(text)
            entry_label_text.set("TTS Input: (Speaking)")
            entry_button_text.set("Speak text")
            return
        t = threading.Thread(target=runner)
        entry_text.set("")
        t.start()

def stop_audio():
    print("Stopping playback")
    sd.stop()

def on_entry_change(*args):
    if len(entry_text.get()) > 1:
        entered = entry_text.get()[-1]

root = tk.Tk()
root.title("Mouthpiece V2 Interface")

# Entry Widget
input_label_text = tk.StringVar()
input_label_text.set("TTS Input:")
input_label = tk.Label(root, textvariable=entry_label_text)
input_label.pack()
input_field = tk.Text(root, height=15, width=40, yscrollcommand=True, xscrollcommand=False)
input_field.pack()
speak_button_text = tk.StringVar()
speak_button_text.set("Speak text")
speak_button = tk.Button(root, textvariable=entry_button_text, command=get_entry_text)
speak_button.pack()

# Stop Widget
stop_button = tk.Button(root, text="Stop audio playback", command=stop_audio)
stop_button.pack()

# Model Widget
model_name = tk.StringVar(root)
model_name.set(MODEL_LIST[5])
model_label = tk.Label(root, text="Select a model")
model_label.pack()
model_dropdown = tk.OptionMenu(root, model_name, *MODEL_LIST)
model_dropdown.pack()

root.bind('<Return>', get_entry_text)
input_field.bind('<KeyRelease>', on_entry_change) 
input_field.focus_set()
root.mainloop()
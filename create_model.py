import pyrootutils
pyrootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)

from lib.fish_speech.fish_speech.models.dac.inference import semantic_tokenizer
from pathlib import Path
from utils import pickler

from config import MODELS_DIR

# Tuples of Name, Textfile path, Waveform path
MODELS = [
    ("example", ".txt", ".wav")
]
for name, text, wav in MODELS:
    text_data = None
    with open(text, "r") as f:
        text_data = f.read()
    wav_path = Path(wav)
    token_data = semantic_tokenizer(
        input_path = wav_path
    )
    pickler.save_model_source(
        semantic_token_data = token_data,
        output_path = (Path(MODELS_DIR) / name),
        source_text = text_data
    )
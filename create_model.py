from lib.fish_speech.fish_speech.models.dac.inference import semantic_tokenizer
from pathlib import Path
from utils import pickler

from config import MODELS_DIR, CHECKPOINT_PATH
import pyrootutils
pyrootutils.setup_root(__file__, indicator=".project-root", pythonpath=True, cwd=True)

# Tuples of Name, Textfile path, Waveform path
MODELS = [
    ("example0", ".\samples\example0.txt", ".\samples\example0.wav")
]
for name, text, wav in MODELS:
    text_data = None
    print(Path(text).absolute())
    with open(text, "r") as f:
        text_data = f.read()
    wav_path = Path(wav)
    token_data = semantic_tokenizer(
        input_path = wav_path,
        checkpoint_path = CHECKPOINT_PATH
    )
    pickler.save_model_source(
        semantic_token_data = token_data,
        output_path = (Path(MODELS_DIR) / name),
        source_text = text_data
    )
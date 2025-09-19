import pyrootutils
pyrootutils.setup_root(__file__, indicator=".project-root", pythonpath=True, cwd=True)
from lib.fish_speech.fish_speech.models.dac.inference import semantic_tokenizer
from pathlib import Path
from utils import pickler

from config import MODELS_DIR, CHECKPOINT_PATH
from train_config import MODELS


# Tuples of Name, Textfile paths, Waveform paths
for name, texts, wavs in MODELS:
    text_data = ""
    for text in texts:
        with open(Path(text).resolve(), "r") as f:
            text_data += f.read().strip() + "\n"
    wav_paths = (Path(wav).resolve() for wav in wavs)
    token_data = semantic_tokenizer(
        input_paths = wav_paths,
        checkpoint_path = CHECKPOINT_PATH
    )
    pickler.save_model_source(
        semantic_token_data = token_data,
        output_path = (Path(MODELS_DIR) / name),
        source_text = text_data
    )
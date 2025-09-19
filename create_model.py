from lib.fish_speech.fish_speech.models.dac.inference import semantic_tokenizer
from pathlib import Path
from utils import pickler

from config import MODELS_DIR, CHECKPOINT_PATH
import pyrootutils
pyrootutils.setup_root(__file__, indicator=".project-root", pythonpath=True, cwd=True)

# Tuples of Name, Textfile paths, Waveform paths
MODELS = [
    (
        "sample",
        (
            "../samples/sample0.txt",
            "../samples/sample1.txt",
            "../samples/sample2.txt",
            "../samples/sample3.txt",
            "../samples/sample4.txt",
            "../samples/sample5.txt",
            "../samples/sample6.txt",
            "../samples/sample7.txt",
            "../samples/sample8.txt",
            "../samples/sample9.txt"
        ),
        (
            "../samples/sample0.wav",
            "../samples/sample1.wav",
            "../samples/sample2.wav",
            "../samples/sample3.wav",
            "../samples/sample4.wav",
            "../samples/sample5.wav",
            "../samples/sample6.wav",
            "../samples/sample7.wav",
            "../samples/sample8.wav",
            "../samples/sample9.wav"
        )
    )
]
for name, texts, wavs in MODELS:
    text_data = ""
    for text in texts:
        with open(Path(text).resolve(), "r") as f:
            text_data += f.read().strip() + "\n"
    wav_paths = (Path(wav).resolve() for wav in wavs)
    token_data = semantics_tokenizer(
        input_paths = wav_paths,
        checkpoint_path = CHECKPOINT_PATH
    )
    pickler.save_model_source(
        semantic_token_data = token_data,
        output_path = (Path(MODELS_DIR) / name),
        source_text = text_data
    )
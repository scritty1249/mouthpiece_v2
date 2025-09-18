import pyrootutils
pyrootutils.setup_root(__file__, indicator=".project-root", pythonpath=True, cwd=True)

from lib.fish_speech.fish_speech.models.dac.inference import generate_audio
from lib.fish_speech.fish_speech.models.text2semantic.inference import generate_tokens
from pathlib import Path
from utils import pickler, audio

import config

# Assumes model already exists

EXTRA_OPTIONS = {
    "top_p": 0.88,
    "repetition_penalty": 1.12,
    "temperature": 0.84
}
MODEL_BASE_PATH = (Path(config.MODELS_DIR) / config.MODEL)
MODEL_TOKEN_PATH = MODEL_BASE_PATH.with_suffix(".npy")
MODEL_TEXT_PATH = MODEL_BASE_PATH.with_suffix(".txt")

MODEL_TOKEN, MODEL_TEXT = pickler.load_model_sources([MODEL_TOKEN_PATH], [MODEL_TEXT_PATH])

try:
    while True:
        text = input("Enter text to read: ")
        tokens = generate_tokens(
            prompt_texts = [MODEL_TEXT],
            prompt_tokens = [MODEL_TOKEN],
            text = text,
            num_samples = 1,
            checkpoint_path = Path(config.CHECKPOINT_DIR),
            **EXTRA_OPTIONS
        )
        audio_array, samplerate = generate_audio(
            compiled_tokens = tokens,
            config_name = config.MODEL_CONFIG,
            checkpoint_path = Path(config.CHECKPOINT_PATH)
        )
        print("playing audio")
        runners = [r for r in audio.mirror_audio(
            audio_array,
            config.AUDIO_DEVICES
        )]
        for runner in runners:
            runner.join()
        print("finished playing audio")
except KeyboardInterrupt:
    print("KeyboardInterrupt, stopping program")
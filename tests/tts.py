import pyrootutils
pyrootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)

from lib.fish_speech.fish_speech.models.dac.inference import generate_audio
from lib.fish_speech.fish_speech.models.text2semantic.inference import generate_tokens
from pathlib import Path
from utils import pickler, audio
from loguru import logger

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

gen = pickler.load_model_sources([MODEL_TOKEN_PATH], [MODEL_TEXT_PATH])
MODEL_TOKEN, MODEL_TEXT = next(gen) # supports loading multiple models at once, but this test only uses one

try:
    while True:
        text = input("Enter text to read: ")
        tokens = next(generate_tokens(  # supports loading multiple models at once, but this test only uses one
            prompt_texts = [MODEL_TEXT],
            prompt_tokens = [MODEL_TOKEN],
            text = text,
            num_samples = 1,
            checkpoint_path = Path(config.CHECKPOINT_DIR),
            **EXTRA_OPTIONS
        ))
        audio_array, samplerate = generate_audio(
            compiled_tokens = tokens,
            config_name = config.MODEL_CONFIG,
            checkpoint_path = Path(config.CHECKPOINT_PATH)
        )
        logger.info("playing audio")
        runners = [r for r in audio.mirror_audio(
            audio_array,
            config.AUDIO_DEVICES
        )]
        for runner in runners:
            runner.join()
        logger.info("finished playing audio")
except KeyboardInterrupt:
    logger.info("KeyboardInterrupt, stopping program")
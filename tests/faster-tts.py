import pyrootutils
pyrootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)

from pathlib import Path
from utils import pickler, audio
from utils.speech import Model
from loguru import logger

import config

# Assumes model already exists

MODEL_BASE_PATH = (Path(config.MODELS_DIR) / config.MODEL)
MODEL_TOKEN_PATH = MODEL_BASE_PATH.with_suffix(".npy")
MODEL_TEXT_PATH = MODEL_BASE_PATH.with_suffix(".txt")

gen = pickler.load_model_sources([MODEL_TOKEN_PATH], [MODEL_TEXT_PATH])
MODEL_TOKEN, MODEL_TEXT = next(gen) # supports loading multiple models at once, but this test only uses one

try:
    logger.info("Initializing model")
    model = Model(
        prompt_text = MODEL_TEXT,
        prompt_token = MODEL_TOKEN,
        checkpoint_dir = Path(config.CHECKPOINT_DIR),
        config_name = config.MODEL_CONFIG,
        checkpoint_path = Path(config.CHECKPOINT_PATH),
        **EXTRA_OPTIONS
    )
    while True:
        text = input("Enter text to read:\n")
        audio_array, samplerate = model.generate(text)
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
import pyrootutils
pyrootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)

from lib.fish_speech.fish_speech.models.dac.inference import generate_audio
from lib.fish_speech.fish_speech.models.text2semantic.inference import generate_tokens
from pathlib import Path

import utils.audio
import utils.pickler
import config

# Assumes model already exists

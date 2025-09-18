from fish_speech.models.dac.inference import generate_audio, semantic_tokenizer
from fish_speech.models.text2semantic.inference import generate_tokens

import pyrootutils
import utils.audio
import utils.pickler

pyrootutils.setup_root(__file__, indicator=".project-root", pythonpath=True)

# Assumes model already exists

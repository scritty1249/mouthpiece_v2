# mouthpiece v2
Built on top of https://github.com/fishaudio/fish-speech\
Total overhual of https://github.com/scritty1249/mouthpiece utilizing a configurable model and real file hierarchy!

This project was intended to act as a text-to-speech mouthpiece for when I wanted to speak over a call while trying to avoid physically making noise.\
While testing v1 of this project, a friend complained that they were uncomfortable randomly hearing "unfamilar" voices.\
<br/>
The solution was clear:\
*create a model that sounds more like me.*\
Since that would definitely be more relaxing.

# Installation
As always, torch and torchaudio version should be changed to match whichever CUDA version the host machine has installed.\
*Development machine hardware boasts an RTX 4070, and the most recent supported version by torch and host graphics card of CUDA is 12.9*

# Setup
- pip install `torch-requirements.txt` first
- pip install the regular `requirements.txt` after
- fill in relevant fields in `config_train.py` to generate model tokens
- execute `create_model.py` from project root directory

# Generating model tokens
- __example.wav__: Requires a 5-20 second snippet of audio in waveform format. Accepts multiple files of varying sample rates.
- __example.txt__: Transcript corrosponding to the audio. Also accepts multiple files.

# Usage
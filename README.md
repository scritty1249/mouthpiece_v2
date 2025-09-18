# mouthpiece v2
Heavily based off of https://github.com/fishaudio/fish-speech\
Total overhual of https://github.com/scritty1249/mouthpiece utilizing a configurable model and real file hierarchy!

This project was intended to act as a text-to-speech mouthpiece for when I wanted to speak over a call while trying to avoid physically making noise.\
A while testing v1 of this project, a friend complained that they were uncomfortable randomly hearing "unfamilar" voices.\
The solution was clear:\
*create a model that sounds more like my friends.*

# Installation
As always, torch and torchaudio version should be changed to match whichever CUDA version the host machine has installed.\
*Development machine hardware boasts an RTX 4070, and the most recent supported version by torch and host graphics card of CUDA is 12.9*

# Setup
- pip install `torch-requirements.txt` first
- pip install the regular `requirements.txt` after
- fill in relevant fields in `create_model.py` to generate model tokens
- execute `create_model.py`

# Generating model tokens
- __example.wav__: Requires a 5-20 second snippet of audio in waveform format
- __example.txt__: Transcript corrosponding to the audio

# Usage
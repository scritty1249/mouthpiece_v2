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
<details>
<summary>(optional) Using the <code>compile=True</code> model parameter on Windows devices</summary>
Attempting to generate speech with CUDA kernal fusion enabled on Windows devices returns the following error from the pytorch binary:</br>
<code>
OverflowError (Python int too large to convert to C long)
</code></br>
To resolve this, follow instructions listed <a href="https://github.com/pytorch/pytorch/issues/162430#issuecomment-3289054096">here</a> for modifying your specific pytorch binary (or rebuild from source with the patch mentioned at the top of the linked issue)</br>
After applying this fix, it will inference fine but will still raise the warning:</br>
<code>
UserWarning: Enable tracemalloc to get the object allocation traceback
</code></br>
On either of the following lines:</br>
<code>
equal |= a_isnan and b_isnan</br>
mask |= a_isnan and not b_isnan
</code></br>
Inference time still shows significant improvement for enabling the setting, despite the warnings.</br>
</details>

# Generating model tokens
- __example.wav__: Requires a 5-20 second snippet of audio in waveform format. Accepts multiple files of varying sample rates.
- __example.txt__: Transcript corrosponding to the audio. Also accepts multiple files.

# Thoughts on features
### Spellcheck
Light research indicated that allowing natively present spellcheck to interact with the application window is not possible for my development platform.\
Running our own spellchecker would be extremely expensive and come at the cost of model inferencing time- so I will not be pursing this idea further.
### "Hot-swapping" Models during runtime (done)
Definitely will implement.
### Modifying model parameters during runtime (done)
May implement, but would require a complete overhaul / removal of the config files.
### Training new models during runtime
May implement, but only if and after model swapping feature is done.

# Usage
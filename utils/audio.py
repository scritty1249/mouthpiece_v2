from typing import Callable, Optional
from loguru import logger

import threading
import sounddevice as sd
import numpy as np

class StreamCallbackWrapper:
    def __init__(self, data, finished_callback=None):
        self.current_frame = 0
        self.data = data
        self.complete = threading.Event()
        self.finished_cb = finished_callback if finished_callback is not None else lambda: ...

    def callback(self, outdata, frames, time, status):
        if status:
            print(status)
        chunksize = min(len(self.data) - self.current_frame, frames)
        outdata[:chunksize] = self.data[self.current_frame:self.current_frame + chunksize]
        if chunksize < frames:
            outdata[chunksize:] = 0
            raise sd.CallbackStop()
        self.current_frame += chunksize

    def finished_callback(self):
        self.complete.set()
        self.finished_cb()

def play_audio(data, device=None, samplerate=None, callback=None):
    if samplerate is None:
        samplerate = sd.query_devices(device, kind="output")["default_samplerate"]

    cbWrapper = StreamCallbackWrapper(data, callback)
    
    def audio_worker(callback_wrapper: StreamCallbackWrapper):
        stream = sd.OutputStream(
            samplerate=samplerate, device=device, channels=data.shape[1],
            callback=callback_wrapper.callback, finished_callback=callback_wrapper.finished_callback
        )
        with stream:
            callback_wrapper.complete.wait()
        return
    
    t = threading.Thread(target=audio_worker, args=(cbWrapper,))
    t.start()
    return t

def mirror_audio(data, devices: tuple[str|int, ...], callbacks: Optional[tuple[Callable|None, ...]] = None, samplerate: int = None):
    if callbacks is None:
        callbacks = [None] * len(devices)
    elif len(callbacks) != len(devices):
        callbacks.extend([None] * (len(devices) - len(callbacks)))
    for device, callback in zip(devices, callbacks):
        yield play_audio(mono_to_stereo(data), device, samplerate, callback)        

def mono_to_stereo(data):
    return np.stack((data, data), axis=1).astype(np.float32)
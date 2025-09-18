from pathlib import Path

import hydra
import numpy as np
import pyrootutils
import soundfile as sf
import torch
import torchaudio
from hydra import compose, initialize
from hydra.utils import instantiate
from loguru import logger
from omegaconf import OmegaConf

pyrootutils.setup_root(__file__, indicator=".lib-root", pythonpath=True)

from fish_speech.utils.file import AUDIO_EXTENSIONS
# register eval resolver
OmegaConf.register_new_resolver("eval", eval)


def load_model(config_name, checkpoint_path, device="cuda"):
    hydra.core.global_hydra.GlobalHydra.instance().clear()
    with initialize(version_base="1.3", config_path="../../configs"):
        cfg = compose(config_name=config_name)

    model = instantiate(cfg)
    state_dict = torch.load(
        checkpoint_path, map_location=device, mmap=True, weights_only=True
    )
    if "state_dict" in state_dict:
        state_dict = state_dict["state_dict"]

    if any("generator" in k for k in state_dict):
        state_dict = {
            k.replace("generator.", ""): v
            for k, v in state_dict.items()
            if "generator." in k
        }

    result = model.load_state_dict(state_dict, strict=False, assign=True)
    model.eval()
    model.to(device)

    logger.info(f"Loaded model: {result}")
    return model


@torch.no_grad()
def semantic_tokenizer(
    input_path: Path = Path("../test.wav"),
    config_name: str = "modded_dac_vq",
    checkpoint_path: Path = Path("checkpoints/openaudio-s1-mini/codec.pth"),
    device: str = "cuda"
):
    model = load_model(config_name, checkpoint_path, device=device)

    if input_path.suffix in AUDIO_EXTENSIONS:
        logger.info(f"Processing in-place reconstruction of {input_path}")

        # Load audio
        audio, sr = torchaudio.load(str(input_path))
        if audio.shape[0] > 1:
            audio = audio.mean(0, keepdim=True)
        audio = torchaudio.functional.resample(audio, sr, model.sample_rate)

        audios = audio[None].to(device)
        logger.info(
            f"Loaded audio with {audios.shape[2] / model.sample_rate:.2f} seconds"
        )

        # VQ Encoder
        audio_lengths = torch.tensor([audios.shape[2]], device=device, dtype=torch.long)
        indices, indices_lens = model.encode(audios, audio_lengths)

        if indices.ndim == 3:
            indices = indices[0]

        logger.info(f"Generated indices of shape {indices.shape}")

        # Save indices
        return indices.cpu().numpy()
    else:
        raise ValueError(f"Unknown input type: {input_path}")

@torch.no_grad()
def generate_audio(
    compiled_tokens: np.typing.NDArray,
    config_name: str = "modded_dac_vq",
    checkpoint_path: Path = Path("checkpoints/openaudio-s1-mini/codec.pth"),
    device: str = "cuda"
):
    model = load_model(config_name, checkpoint_path, device=device)

    logger.info(f"Processing precomputed indices")
    indices = torch.from_numpy(compiled_tokens).to(device).long()
    assert indices.ndim == 2, f"Expected 2D indices, got {indices.ndim}"
    indices_lens = torch.tensor([indices.shape[1]], device=device, dtype=torch.long)

    # Restore
    fake_audios, audio_lengths = model.decode(indices, indices_lens)
    audio_time = fake_audios.shape[-1] / model.sample_rate

    logger.info(
        f"Generated audio of shape {fake_audios.shape}, equivalent to {audio_time:.2f} seconds from {indices.shape[1]} features, features/second: {indices.shape[1] / audio_time:.2f}"
    )

    # Save audio
    fake_audio = fake_audios[0, 0].float().cpu().numpy() # mono audio
    return (fake_audio, model.sample_rate)
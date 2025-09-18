from numpy import load, save
from numpy.typing import NDArray
from pathlib import Path
from string import ascii_letters, digits
from os import PathLike
from loguru import logger
from numpy import load

def load_model_sources(
    token_paths: tuple[PathLike, ...],
    text_paths: tuple[PathLike, ...]
):
    if len(token_paths) != len(text_paths):
        raise ValueError(
            f"Number of text files ({len(text_paths)}) and token files ({len(token_paths)}) should be the same"
        )
    for token_path, text_path in zip(token_paths, text_paths):
        if token_path.exists() and text_path.exists():
            text = None
            with open(text_path, "r") as infile:
                text = infile.read()
            data = load(token_path)
            yield (data, text)
        else:
            raise FileNotFoundError(f"File {token_path} does not exist.")



def save_model_source(
    semantic_token_data: NDArray,
    output_path: Path,
    source_text: str|PathLike = None
):
    data_path = output_path.with_suffix(".npy")
    text_path = output_path.with_suffix(".txt")
    if source_text is not None:
        if isinstance(source_text, PathLike):
            with open(source_text, "r") as infile, open(text_path, "w") as outfile:
                outfile.write(infile.read())
            logger.info(f"Copied contents of {source_text} to {text_path}.")
        elif isinstance(source_text, str):
            with open(text_path, "w") as outfile:
                outfile.write(source_text)
            logger.info(f"Wrote reference text to {text_path}.")
    save(data_path, semantic_token_data)
    logger.info(f"Saved tokenized semantic data to {data_path}.")

def format_filename(name: str):
    valid_chars = "-_.() %s%s" % (ascii_letters, digits)
    filename = ''.join(c for c in name if c in valid_chars)
    filename = filename.replace(' ','_') # I don't like spaces in filenames.
    return filename
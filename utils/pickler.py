from numpy import load, save
from numpy.typing import NDArray
from pathlib import Path
from string import ascii_letters, digits
from os import PathLike

def load_model_source(
    token_paths: Optional[tuple[Path, ...]],
    text_paths: Optional[tuple[Path, ...]]
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
            data = np.load(token_path)
            yield (data, text)
        else:
            raise FileNotFoundError(f"File {token_path} does not exist.")



def save_model_source(
    semantic_token_data: NDArray,
    output_path: Path,
    source_text: str|Path = None
):
    save_path = output_path.with_suffix(".npy")
    try:
        if source_text is not None:
            if isinstance(source_text, PathLike):
                with open(source_text, "r") as infile, open(output_path.with_suffix(".txt"), "w") as outfile:
                    outfile.write(infile.read())
            elif isinstance(source_text, str):
                with open(output_path.with_suffix(".txt"), "w") as outfile:
                    outfile.write(source_text)
        save(save_path, semantic_token_data)
        return save_path
    except:
        ...

def format_filename(name: str):
    valid_chars = "-_.() %s%s" % (ascii_letters, digits)
    filename = ''.join(c for c in name if c in valid_chars)
    filename = filename.replace(' ','_') # I don't like spaces in filenames.
    return filename
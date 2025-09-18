from numpy import load, save
from numpy.typing import NDArray
from pathlib import Path
from string import ascii_letters, digits

def load_tokens(
    token_paths: Optional[tuple[Path, ...]]
):
    for token_path in token_paths:
        if token_path.exists():
            yield np.load(token_path)
        else:
            raise FileNotFoundError(f"Path {token_path} does not exist.")

def save_token(
    semantic_token_data: NDArray,
    output_path: Path
):
    save_path = output_path.with_suffix(".npy")
    try:
        save(save_path, semantic_token_data)
        return save_path
    except:
        ...

def format_filename(name: str):
    valid_chars = "-_.() %s%s" % (ascii_letters, digits)
    filename = ''.join(c for c in name if c in valid_chars)
    filename = filename.replace(' ','_') # I don't like spaces in filenames.
    return filename
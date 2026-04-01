"""Configuration file parser for A-Maze-ing."""

import sys
from typing import NamedTuple


class MazeConfig(NamedTuple):
    """Holds all validated maze generation parameters.

    Attributes:
        width: Number of columns in the maze.
        height: Number of rows in the maze.
        entry: (x, y) coordinates of the maze entry.
        exit: (x, y) coordinates of the maze exit.
        output_file: Path to the output file.
        perfect: Whether the maze must be perfect.
        seed: Random seed for reproducibility.
    """

    width: int
    height: int
    entry: tuple[int, int]
    exit_: tuple[int, int]
    output_file: str
    perfect: bool
    seed: int


def parse_config(filepath: str) -> MazeConfig:
    """Parse and validate a maze configuration file.

    Args:
        filepath: Path to the configuration file.

    Returns:
        A validated MazeConfig instance.

    Raises:
        SystemExit: If the file is missing, malformed, or invalid.
    """
    raw: dict[str, str] = {}

    try:
        with open(filepath, "r") as f:
            for line_number, line in enumerate(f, 1):
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" not in line:
                    _error(f"line {line_number}: invalid syntax '{line}'")
                key, _, value = line.partition("=")
                raw[key.strip()] = value.strip()
    except FileNotFoundError:
        _error(f"config file not found: '{filepath}'")

    return _validate(raw)


def _validate(raw: dict[str, str]) -> MazeConfig:
    """Validate raw key/value pairs and return a MazeConfig.

    Args:
        raw: Dictionary of raw string key/value pairs.

    Returns:
        A validated MazeConfig instance.
    """
    required = ["WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE", "PERFECT"]
    for key in required:
        if key not in raw:
            _error(f"missing required key: '{key}'")

    width = _parse_int(raw["WIDTH"], "WIDTH", min_val=3)
    height = _parse_int(raw["HEIGHT"], "HEIGHT", min_val=3)
    entry = _parse_coords(raw["ENTRY"], "ENTRY", width, height)
    exit_ = _parse_coords(raw["EXIT"], "EXIT", width, height)
    perfect = _parse_bool(raw["PERFECT"], "PERFECT")
    output_file = raw["OUTPUT_FILE"].strip()
    seed = _parse_int(raw.get("SEED", "0"), "SEED", min_val=0)

    if entry == exit_:
        _error("ENTRY and EXIT must be different cells")
    if not output_file:
        _error("OUTPUT_FILE cannot be empty")

    return MazeConfig(
        width=width,
        height=height,
        entry=entry,
        exit_=exit_,
        output_file=output_file,
        perfect=perfect,
        seed=seed,
    )


def _parse_int(value: str, key: str, min_val: int = 0) -> int:
    """Parse a string as a positive integer.

    Args:
        value: The string to parse.
        key: The config key name (for error messages).
        min_val: Minimum accepted value.

    Returns:
        The parsed integer.
    """
    try:
        result = int(value)
    except ValueError:
        _error(f"{key} must be an integer, got '{value}'")
    if result < min_val:
        _error(f"{key} must be >= {min_val}, got {result}")
    return result


def _parse_coords(
    value: str, key: str, width: int, height: int
) -> tuple[int, int]:
    """Parse a 'x,y' coordinate string and validate bounds.

    Args:
        value: The raw 'x,y' string.
        key: The config key name (for error messages).
        width: Maze width to check bounds.
        height: Maze height to check bounds.

    Returns:
        A validated (x, y) tuple.
    """
    parts = value.split(",")
    if len(parts) != 2:
        _error(f"{key} must be in 'x,y' format, got '{value}'")
    x = _parse_int(parts[0].strip(), f"{key}.x", min_val=0)
    y = _parse_int(parts[1].strip(), f"{key}.y", min_val=0)
    if x >= width or y >= height:
        _error(f"{key} ({x},{y}) is out of bounds for {width}x{height} maze")
    return (x, y)


def _parse_bool(value: str, key: str) -> bool:
    """Parse a string as a boolean (True/False).

    Args:
        value: The string to parse.
        key: The config key name (for error messages).

    Returns:
        The parsed boolean.
    """
    if value.lower() == "true":
        return True
    if value.lower() == "false":
        return False
    _error(f"{key} must be 'True' or 'False', got '{value}'")


def _error(message: str) -> None:
    """Print an error message and exit.

    Args:
        message: The error description.
    """
    print(f"[config error] {message}", file=sys.stderr)
    sys.exit(1)

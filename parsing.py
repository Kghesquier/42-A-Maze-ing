import sys
from typing import Any


class InvalidInput(Exception):
    """Raised when the config file is malformed.

    Covers invalid lines, missing or duplicate keys, and values
    that fail validation.
    """

    pass


def parse_config() -> dict[str, Any]:
    """Read and validate the config file passed as a command-line argument.

    The file must contain KEY=VALUE pairs (one per line). Empty lines
    and lines starting with '#' are ignored.

    Mandatory keys:
        WIDTH, HEIGHT   (int >= 1)
        ENTRY, EXIT     (x,y) within maze bounds and different from each other
        OUTPUT_FILE     output path (non-empty string)
        PERFECT         True or False

    Optional key:
        SEED            int for reproducible generation

    Returns:
        Dict with correctly typed values (int, tuple, bool...).

    Exits:
        Calls sys.exit(1) if the argument is missing, the file is not found,
        a mandatory key is absent, or any value fails validation.
    """
    config: dict[str, Any] = {}
    required_keys = ["WIDTH", "HEIGHT", "ENTRY", "EXIT",
                     "OUTPUT_FILE", "PERFECT"]
    try:
        if len(sys.argv) != 2:
            raise InvalidInput("No argument or too many arguments provided")
    except InvalidInput as e:
        sys.stderr.write(f"ERROR: {e}\n")
        sys.exit(1)
    except Exception as e:
        sys.stderr.write(f"ERROR: {e}\n")
        sys.exit(1)
    try:
        with open(sys.argv[1], "r") as f:
            for line in f:
                if line.startswith("#") or line.strip() == "":
                    continue
                parts = line.split("=", 1)
                if len(parts) != 2:
                    raise InvalidInput(
                        "All lines must be formatted as \"KEY=VALUE\" "
                        "or begin with \"#\" for comments"
                    )
                if parts[0] in config:
                    raise InvalidInput(
                        f"Duplicate key '{parts[0]}' found in {sys.argv[1]}"
                    )
                config[parts[0]] = parts[1].strip()
    except (FileNotFoundError, IsADirectoryError,
            PermissionError, OSError, InvalidInput) as e:
        sys.stderr.write(f"ERROR: {e}\n")
        sys.exit(1)
    except Exception as e:
        sys.stderr.write(f"ERROR: {e}\n")
        sys.exit(1)
    try:
        for key in required_keys:
            if key not in config:
                raise InvalidInput(
                    f"Missing required key '{key}' in {sys.argv[1]}"
                )
    except InvalidInput as e:
        sys.stderr.write(f"ERROR: {e}\n")
        sys.exit(1)
    except Exception as e:
        sys.stderr.write(f"ERROR: {e}\n")
        sys.exit(1)
    for key, value in config.items():
        if key in ("WIDTH", "HEIGHT"):
            try:
                parsed = int(value)
                if parsed < 1:
                    raise ValueError()
                config[key] = parsed
            except (ValueError, OverflowError):
                sys.stderr.write(
                    f"ERROR: '{key}' must be a positive integer >= 1, "
                    f"got '{value}'\n"
                )
                sys.exit(1)
            except Exception as e:
                sys.stderr.write(f"ERROR: {e}\n")
                sys.exit(1)
        elif key in ("ENTRY", "EXIT"):
            try:
                coords = value.split(",")
                if len(coords) != 2:
                    raise ValueError()
                x, y = int(coords[0]), int(coords[1])
                if x < 0 or y < 0:
                    raise ValueError()
                config[key] = (x, y)
            except (ValueError, OverflowError):
                sys.stderr.write(
                    f"ERROR: '{key}' must be formatted as 'x,y' "
                    f"with non-negative integers, got '{value}'\n"
                )
                sys.exit(1)
            except Exception as e:
                sys.stderr.write(f"ERROR: {e}\n")
                sys.exit(1)
        elif key == "PERFECT":
            try:
                if value == "True":
                    config[key] = True
                elif value == "False":
                    config[key] = False
                else:
                    raise ValueError(
                        f"'PERFECT' must be 'True' or 'False', got '{value}'"
                    )
            except ValueError as e:
                sys.stderr.write(f"ERROR: {e}\n")
                sys.exit(1)
            except Exception as e:
                sys.stderr.write(f"ERROR: {e}\n")
                sys.exit(1)
        elif key == "SEED":
            try:
                config[key] = int(value)
            except (ValueError, OverflowError):
                sys.stderr.write(
                    f"ERROR: 'SEED' must be an integer, got '{value}'\n"
                )
                sys.exit(1)
            except Exception as e:
                sys.stderr.write(f"ERROR: {e}\n")
                sys.exit(1)
        elif key == "OUTPUT_FILE":
            try:
                if not value:
                    raise ValueError("'OUTPUT_FILE' must not be empty")
            except ValueError as e:
                sys.stderr.write(f"ERROR: {e}\n")
                sys.exit(1)
            except Exception as e:
                sys.stderr.write(f"ERROR: {e}\n")
                sys.exit(1)
    entry_x, entry_y = config["ENTRY"]
    exit_x, exit_y = config["EXIT"]
    try:
        if config["ENTRY"] == config["EXIT"]:
            raise ValueError("ENTRY and EXIT must be different")
        if entry_x >= config["WIDTH"] or entry_y >= config["HEIGHT"]:
            raise ValueError("ENTRY coordinates are out of maze bounds")
        if exit_x >= config["WIDTH"] or exit_y >= config["HEIGHT"]:
            raise ValueError("EXIT coordinates are out of maze bounds")
    except ValueError as e:
        sys.stderr.write(f"ERROR: {e}\n")
        sys.exit(1)
    except Exception as e:
        sys.stderr.write(f"ERROR: {e}\n")
        sys.exit(1)
    return config

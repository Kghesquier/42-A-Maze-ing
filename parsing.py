import sys
from typing import Any


class InvalidInput(Exception):
    """Exception raised when the configuration file is malformed.

    Raised when a line is not formatted as KEY=VALUE, when a mandatory
    key is missing, when a duplicate key is found, or when any value
    fails validation.
    """

    pass


def parsing() -> dict[str, Any]:
    """Parse and validate the maze configuration file from command-line args.

    Usage:
        python a_maze_ing.py <config_file>

    Config file format:
        Plain text file with one KEY=VALUE pair per line.
        Lines starting with '#' are treated as comments and ignored.
        Empty lines are ignored.

    Mandatory keys:
        WIDTH       (int >= 1)        Width of the maze in cells.
        HEIGHT      (int >= 1)        Height of the maze in cells.
        ENTRY       (int,int)         Entry point as 'x,y' (0-indexed,
                                      within bounds).
        EXIT        (int,int)         Exit point as 'x,y' (0-indexed,
                                      within bounds, must differ from ENTRY).
        OUTPUT_FILE (non-empty str)   Path where the generated maze will
                                      be written.
        PERFECT     (True|False)      Whether to generate a perfect maze
                                      (no loops).

    Optional keys:
        SEED        (int)             RNG seed for reproducible generation.

    Returns:
        dict[str, Any]: Parsed configuration with correctly typed values::

            {
                "WIDTH":       int,
                "HEIGHT":      int,
                "ENTRY":       (int, int),
                "EXIT":        (int, int),
                "OUTPUT_FILE": str,
                "PERFECT":     bool,
                "SEED":        int,   # only present if defined in config file
            }

    Exits:
        Calls sys.exit(1) after writing to stderr in any of these cases:

        - Wrong number of command-line arguments.
        - Config file not found.
        - A line is not formatted as KEY=VALUE or a comment.
        - A mandatory key is missing.
        - WIDTH or HEIGHT is not an integer >= 1.
        - ENTRY or EXIT is not formatted as 'x,y' with non-negative integers.
        - ENTRY or EXIT coordinates are out of maze bounds.
        - ENTRY and EXIT refer to the same cell.
        - PERFECT is not exactly 'True' or 'False'.
        - SEED is not a valid integer.
        - OUTPUT_FILE is an empty string.
    """
    parsed_input: dict[str, Any] = {}
    mandatory_key = ["WIDTH",
                     "HEIGHT",
                     "ENTRY",
                     "EXIT",
                     "OUTPUT_FILE",
                     "PERFECT"]
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
        with open(sys.argv[1], "r") as input_file:
            for line in input_file:
                if line.startswith("#"):
                    continue
                if line.strip() == "":
                    continue
                split_line = line.split("=", 1)
                if len(split_line) != 2:
                    raise InvalidInput("Invalid input, All lines must be "
                                       "formatted as \"KEY=VALUE\" or "
                                       "begin with \"#\" for comments")
                if split_line[0] in parsed_input:
                    raise InvalidInput(f"Duplicate key '{split_line[0]}' "
                                       f"found in {sys.argv[1]}")
                parsed_input[split_line[0]] = split_line[1].strip()
    except (FileNotFoundError, IsADirectoryError,
            PermissionError, OSError, InvalidInput) as e:
        sys.stderr.write(f"ERROR: {e}\n")
        sys.exit(1)
    except Exception as e:
        sys.stderr.write(f"ERROR: {e}\n")
        sys.exit(1)
    try:
        for key in mandatory_key:
            if key not in parsed_input:
                raise InvalidInput(f"Invalid input, Not all required keys "
                                   f"are present in {sys.argv[1]} ('{key}'"
                                   " is missing)")
    except InvalidInput as e:
        sys.stderr.write(f"ERROR: {e}\n")
        sys.exit(1)
    except Exception as e:
        sys.stderr.write(f"ERROR: {e}\n")
        sys.exit(1)
    for key, value in parsed_input.items():
        if key == "WIDTH" or key == "HEIGHT":
            try:
                value = int(value)
                if value < 1:
                    raise ValueError()
                parsed_input[key] = value
            except (ValueError, OverflowError):
                sys.stderr.write("ERROR: Invalid value, the value of "
                                 f"'{key}' must be a positive integer >= 1, "
                                 f"not '{value}'\n")
                sys.exit(1)
            except Exception as e:
                sys.stderr.write(f"ERROR: {e}\n")
                sys.exit(1)
        elif key == "ENTRY" or key == "EXIT":
            try:
                split_value = value.split(",")
                if len(split_value) != 2:
                    raise ValueError()
                x, y = int(split_value[0]), int(split_value[1])
                if x < 0 or y < 0:
                    raise ValueError()
                parsed_input[key] = (x, y)
            except (ValueError, OverflowError):
                sys.stderr.write("ERROR: Invalid value, the value of "
                                 f"'{key}' must be formatted as "
                                 "'positive int,positive int', "
                                 f"not '{value}'\n")
                sys.exit(1)
            except Exception as e:
                sys.stderr.write(f"ERROR: {e}\n")
                sys.exit(1)
        elif key == "PERFECT":
            try:
                if value == "True":
                    parsed_input[key] = True
                elif value == "False":
                    parsed_input[key] = False
                else:
                    raise ValueError("Invalid value, the value of "
                                     f"'{key}' must be 'True' or 'False', "
                                     f"not '{value}'")
            except ValueError as e:
                sys.stderr.write(f"ERROR: {e}\n")
                sys.exit(1)
            except Exception as e:
                sys.stderr.write(f"ERROR: {e}\n")
                sys.exit(1)
        elif key == "SEED":
            try:
                value = int(value)
                parsed_input[key] = value
            except (ValueError, OverflowError):
                sys.stderr.write(f"ERROR: Invalid value, "
                                 f"{key} has to be an int\n")
                sys.exit(1)
            except Exception as e:
                sys.stderr.write(f"ERROR: {e}\n")
                sys.exit(1)
        elif key == "OUTPUT_FILE":
            try:
                if not value:
                    raise ValueError("Invalid value, "
                                     "'OUTPUT_FILE' must not be empty")
            except ValueError as e:
                sys.stderr.write(f"ERROR: {e}\n")
                sys.exit(1)
            except Exception as e:
                sys.stderr.write(f"ERROR: {e}\n")
                sys.exit(1)
    x_s, y_s = parsed_input["ENTRY"]
    x_e, y_e = parsed_input["EXIT"]
    try:
        if parsed_input["ENTRY"] == parsed_input["EXIT"]:
            raise ValueError("ENTRY and EXIT must be different")
        if x_s >= parsed_input["WIDTH"] or y_s >= parsed_input["HEIGHT"]:
            raise ValueError("ENTRY coordinates are out of maze bounds")
        if x_e >= parsed_input["WIDTH"] or y_e >= parsed_input["HEIGHT"]:
            raise ValueError("EXIT coordinates are out of maze bounds")
    except ValueError as e:
        sys.stderr.write(f"ERROR: {e}\n")
        sys.exit(1)
    except Exception as e:
        sys.stderr.write(f"ERROR: {e}\n")
        sys.exit(1)
    return parsed_input

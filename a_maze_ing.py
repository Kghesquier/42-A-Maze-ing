import sys
import curses
from parsing import parse_config
from mazegen import MazeGenerator
from display import render_maze


def run() -> None:
    """Main entry point of the program.

    Parses the config, builds the maze generator, and launches the curses
    display. Handles keyboard interrupts and terminal errors gracefully.
    """
    config = parse_config()
    maze = MazeGenerator(
        config["WIDTH"],
        config["HEIGHT"],
        config["ENTRY"],
        config["EXIT"],
        config["PERFECT"],
        config.get("SEED"),
    )
    try:
        curses.wrapper(lambda stdscr:
                       render_maze(stdscr, maze, config["OUTPUT_FILE"]))
    except KeyboardInterrupt:
        pass
    except curses.error as e:
        sys.stderr.write(f"ERROR: Terminal error: {e}\n")
        sys.exit(1)
    except OSError as e:
        sys.stderr.write(f"ERROR: Could not write output file: {e}\n")
        sys.exit(1)
    except Exception as e:
        sys.stderr.write(f"ERROR: Unexpected error: {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    run()

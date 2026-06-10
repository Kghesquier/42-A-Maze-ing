import sys
import curses
from parsing import parsing
from mazegen import MazeGenerator
from display import display_maze


def amazeing() -> None:
    """Run the maze generation and display the result.

    Parses the configuration file, initializes the maze generator,
    and launches the curses-based visual display.
    Exits gracefully on keyboard interrupt or terminal error.
    """
    data = parsing()
    width = data["WIDTH"]
    height = data["HEIGHT"]
    start = data["ENTRY"]
    end = data["EXIT"]
    perfect = data["PERFECT"]
    seed = data.get("SEED")
    maze = MazeGenerator(width, height, start, end, perfect, seed)
    try:
        curses.wrapper(lambda stdscr:
                       display_maze(stdscr, maze, data["OUTPUT_FILE"]))
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
    amazeing()

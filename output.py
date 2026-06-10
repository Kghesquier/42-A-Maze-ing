from mazegen import MazeGenerator


def save_maze(filepath: str, maze: MazeGenerator,
              path: list[tuple[int, int]]) -> None:
    """Write the maze data to a text file.

    File format: the grid as hex digits (one row per line), a blank line,
    the entry and exit coordinates, then the solution path as N/E/S/W letters.

    Args:
        filepath: Path of the file to write.
        maze:     MazeGenerator instance holding the grid and coordinates.
        path:     Solution path as a list of (x, y) tuples.

    Raises:
        OSError: If the file cannot be created or written to.
    """
    try:
        with open(filepath, "w") as f:
            for row in maze.grid:
                f.write("".join(f"{cell:X}" for cell in row) + "\n")
            f.write("\n")
            f.write(f"{maze.start[0]},{maze.start[1]}\n")
            f.write(f"{maze.end[0]},{maze.end[1]}\n")
            for i in range(len(path) - 1):
                x, y = path[i]
                nx, ny = path[i + 1]
                if x < nx:
                    f.write("E")
                elif x > nx:
                    f.write("W")
                elif y < ny:
                    f.write("S")
                elif y > ny:
                    f.write("N")
            f.write("\n")
    except OSError:
        raise
    except Exception as e:
        raise OSError(f"Unexpected write error: {e}")

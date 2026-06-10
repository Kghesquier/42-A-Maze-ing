from mazegen import MazeGenerator


def write_output(output_name: str, maze: MazeGenerator,
                 path: list[tuple[int, int]]) -> None:
    """Write the maze data to the output file in hexadecimal format.

    Writes the maze grid row by row as hexadecimal wall bitmasks (uppercase),
    followed by a blank line, the entry and exit coordinates, and the shortest
    path as a sequence of cardinal directions (N, E, S, W).

    Output format::

        <WIDTH hex chars per row, HEIGHT rows>
        <blank line>
        <entry_x>,<entry_y>
        <exit_x>,<exit_y>
        <path as NESW string>

    Args:
        output_name: Path to the output file to write.
        maze:        The MazeGenerator instance containing the grid,
                     start, and end positions.
        path:        The shortest path from start to end as a list of
                     (x, y) tuples.

    Raises:
        OSError: If the file cannot be created or written to
                 (e.g., permission denied, invalid path).
    """
    try:
        with open(output_name, "w") as output_file:
            for y in range(maze.height):
                for x in range(maze.width):
                    output_file.write(f"{maze.grid[y][x]:X}")
                output_file.write("\n")
            output_file.write("\n")
            output_file.write(f"{maze.start[0]},{maze.start[1]}\n")
            output_file.write(f"{maze.end[0]},{maze.end[1]}\n")
            for i in range(len(path) - 1):
                x, y = path[i]
                x_n, y_n = path[i + 1]
                if x < x_n:
                    output_file.write("E")
                elif x > x_n:
                    output_file.write("W")
                elif y < y_n:
                    output_file.write("S")
                elif y > y_n:
                    output_file.write("N")
            output_file.write("\n")
    except OSError:
        raise
    except Exception as e:
        raise OSError(f"Unexpected write error: {e}")

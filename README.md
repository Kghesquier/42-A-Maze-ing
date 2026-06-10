*This project has been created as part of the 42 curriculum by kghesqui.*

# A-Maze-ing

## Description

A-Maze-ing is a maze generator written in Python 3. Given a configuration file, it generates a maze (perfect or imperfect), writes it to an output file in hexadecimal wall format, and displays it interactively in the terminal using curses. The maze always contains a visible **"42" pattern** made of fully closed cells, and exposes its generation logic as a reusable, installable Python package.

## Instructions

### Requirements

- Python 3.10 or later
- `pip` or `uv`

### Install dependencies

```bash
make install
```

### Run

```bash
python3 a_maze_ing.py config.txt
```

Or via the Makefile:

```bash
make run
```

### Debug mode

```bash
make debug
```

### Lint

```bash
make lint
```

### Clean

```bash
make clean
```
or
```bash
make fclean
```
(more complete)
### Terminal interactions

Once the maze is displayed:

| Key | Action |
|-----|--------|
| `1` | Re-generate a new maze |
| `2` | Show / Hide the solution path |
| `3` | Rotate wall colours |
| `4` or `q` | Quit |

---

## Configuration file format

The configuration file must contain one `KEY=VALUE` pair per line. Lines starting with `#` are comments and are ignored. Empty lines are ignored.

| Key | Type | Description | Example |
|-----|------|-------------|---------|
| `WIDTH` | `int >= 1` | Maze width in cells | `WIDTH=20` |
| `HEIGHT` | `int >= 1` | Maze height in cells | `HEIGHT=15` |
| `ENTRY` | `x,y` | Entry coordinates (0-indexed) | `ENTRY=0,0` |
| `EXIT` | `x,y` | Exit coordinates (0-indexed, ≠ ENTRY) | `EXIT=19,14` |
| `OUTPUT_FILE` | `str` | Path of the output file | `OUTPUT_FILE=maze.txt` |
| `PERFECT` | `True\|False` | Generate a perfect maze (single path) | `PERFECT=False` |
| `SEED` | `int` | Optional RNG seed for reproducibility | `SEED=42` |


## Output file format

Each cell is encoded as one uppercase hexadecimal digit (0–F) where each bit represents a wall:

| Bit | Direction |
|-----|-----------|
| 0 (LSB) | North |
| 1 | East |
| 2 | South |
| 3 | West |

`1` = wall closed, `0` = wall open.

Cells are written row by row, one row per line. After a blank line, three lines follow:
1. Entry coordinates as `x,y`
2. Exit coordinates as `x,y`
3. Shortest path from entry to exit using `N`, `E`, `S`, `W`

---

## Maze generation algorithm

The generator uses the **recursive backtracker** algorithm (iterative DFS with a stack):

1. Start from the entry cell, push it onto the stack.
2. Before generation, stamp the **"42" pattern** cells as visited so the DFS never carves through them.
3. At each step, pick a random unvisited neighbour, remove the shared wall, and push the neighbour.
4. When no unvisited neighbours remain, pop the stack (backtrack).
5. Repeat until the stack is empty — every non-42 cell has been visited exactly once.

For **imperfect** mazes (`PERFECT=False`), a second pass randomly removes extra east/south walls with 25% probability, skipping any removal that would create a fully open 2×2 area or touch a "42" cell.

### Why this algorithm?

The recursive backtracker is simple to implement, produces mazes with long winding corridors (visually interesting), and naturally guarantees full connectivity. Its iterative form avoids Python's recursion limit on large grids.

---

## Reusable module — `mazegen`

The maze generation logic is packaged as a standalone, installable module.

### Install from the wheel

```bash
pip install mazegen-1.0.0-py3-none-any.whl
```

### Rebuild the package from source

```bash
pip install build
python -m build
```

This produces `dist/mazegen-1.0.0-py3-none-any.whl` and `dist/mazegen-1.0.0.tar.gz`.

### Basic usage

```python
from mazegen import MazeGenerator

# Create a 20×15 perfect maze with a fixed seed
maze = MazeGenerator(
    width=20,
    height=15,
    start=(0, 0),
    end=(19, 14),
    perfect=True,
    seed=42,
)

# Generate the maze (returns the 2D grid)
grid = maze.generate()

# Access the grid: grid[y][x] is an int 0–15 encoding walls
# Bit 0 = North, Bit 1 = East, Bit 2 = South, Bit 3 = West
print(grid[0][0])  # wall bitmask of top-left cell

# Solve: returns list of (x, y) tuples from start to end
path = maze.solve()
print(path)

# Access pattern cells
print(maze.cell_42)       # set of (x, y) belonging to the "42" logo
print(maze.can_draw_42)   # False if the maze was too small for the pattern
```

### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `width` | `int` | Number of cells horizontally (≥ 1) |
| `height` | `int` | Number of cells vertically (≥ 1) |
| `start` | `tuple[int, int]` | Entry cell as `(x, y)` |
| `end` | `tuple[int, int]` | Exit cell as `(x, y)`, must differ from `start` |
| `perfect` | `bool` | `True` for a perfect maze (unique path) |
| `seed` | `int \| None` | Optional RNG seed for reproducibility |

### Accessing the solution

After `generate()`, call `solve()` to get the shortest path as a list of `(x, y)` tuples from `start` to `end`. Returns an empty list if the end is unreachable.

---

## Team and project management

### Team

Solo project — **kghesqui**  (supposed to be a group project but I had problems with my m8...)

### Planning

The project was split into four stages:

1. **Core generator** — `MazeGenerator` class, DFS algorithm, "42" pattern placement, open-area constraint.
2. **Output & parsing** — config file parser, hexadecimal output writer.
3. **Display** — curses-based terminal rendering, animations, colour rotation, user interactions.
4. **Package & polish** — `pyproject.toml`, wheel build, Makefile, tests, README.

### What worked well

- Separating the generator into its own module made testing and packaging straightforward.
- The iterative DFS avoided recursion-limit issues on large grids.
- Curses animations (row-by-row and path drawing) gave immediate visual feedback.

### What could be improved

- The imperfect mode could allow up to 2-wide corridors (2×3 areas) as the spec permits, instead of always preventing 2×2 open areas.
- The visual representation of the maze would have been better with MLX but the lack of time and doc made me choose the terminal output.

### Tools used

- **Claude Code** — for debugging, code structure, and test generation (see Resources).
- **uv** — for dependency management and virtual environments.
- **pytest** — for unit and integration testing.
- **mypy** / **flake8** — for static type checking and linting.

---

## Resources

### References

- [Maze generation algorithms — Wikipedia](https://en.wikipedia.org/wiki/Maze_generation_algorithm)
- [Recursive backtracker explained — Jamis Buck's blog](https://weblog.jamisbuck.org/2010/12/27/maze-generation-recursive-backtracking)
- [Python curses documentation](https://docs.python.org/3/library/curses.html)
- [PEP 257 — Docstring Conventions](https://peps.python.org/pep-0257/)
- [Python packaging user guide](https://packaging.python.org/en/latest/)

### AI usage

**Claude Code** was used in two ways on this project:

- **Debugging and code structure**: helping trace wall-consistency bugs, reviewing the open-area detection logic, and structuring the module layout (separate `mazegen` package, `output.py`, `parsing.py`).
- **Test generation**: generating the pytest test suite covering constructor validation, wall consistency, path correctness, output format, and end-to-end integration scenarios.

All generated code and tests were reviewed, understood, and validated manually before being included in the project.

"""Test suite for the A-Maze-ing project (V2).

Tests cover MazeGenerator, parsing, output writing, and end-to-end
integration scenarios.
"""
import os
import sys
import tempfile
from collections import deque

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from mazegen import MazeGenerator  # noqa: E402
from output import write_output  # noqa: E402


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _bfs_reachable(
    maze: MazeGenerator,
    origin: tuple[int, int]
) -> set[tuple[int, int]]:
    """Return all cells reachable from origin via open walls (BFS)."""
    visited: set[tuple[int, int]] = set()
    queue: deque[tuple[int, int]] = deque([origin])
    visited.add(origin)
    while queue:
        x, y = queue.popleft()
        val = maze.grid[y][x]
        neighbors = []
        if x + 1 < maze.width and val & 2 == 0:
            neighbors.append((x + 1, y))
        if x - 1 >= 0 and val & 8 == 0:
            neighbors.append((x - 1, y))
        if y + 1 < maze.height and val & 4 == 0:
            neighbors.append((x, y + 1))
        if y - 1 >= 0 and val & 1 == 0:
            neighbors.append((x, y - 1))
        for nb in neighbors:
            if nb not in visited:
                visited.add(nb)
                queue.append(nb)
    return visited


def _bfs_distance(
    maze: MazeGenerator,
    origin: tuple[int, int],
    target: tuple[int, int]
) -> int:
    """Return shortest path length from origin to target.

    Returns -1 if target is unreachable.
    """
    dist: dict[tuple[int, int], int] = {origin: 0}
    queue: deque[tuple[int, int]] = deque([origin])
    while queue:
        x, y = queue.popleft()
        if (x, y) == target:
            return dist[target]
        val = maze.grid[y][x]
        for nx, ny, bit in [
            (x + 1, y, 2), (x - 1, y, 8),
            (x, y + 1, 4), (x, y - 1, 1)
        ]:
            if (0 <= nx < maze.width and 0 <= ny < maze.height
                    and val & bit == 0 and (nx, ny) not in dist):
                dist[(nx, ny)] = dist[(x, y)] + 1
                queue.append((nx, ny))
    return -1


# ---------------------------------------------------------------------------
# GROUPE 1 — MazeGenerator.__init__()
# ---------------------------------------------------------------------------

class TestMazeGeneratorInit:
    """Tests for MazeGenerator constructor validation."""

    def test_width_zero_raises(self) -> None:
        """width=0 must raise ValueError."""
        with pytest.raises(ValueError):
            MazeGenerator(0, 5, (0, 0), (0, 4), True)

    def test_height_zero_raises(self) -> None:
        """height=0 must raise ValueError."""
        with pytest.raises(ValueError):
            MazeGenerator(5, 0, (0, 0), (4, 0), True)

    def test_start_out_of_bounds_raises(self) -> None:
        """start out of maze bounds must raise ValueError."""
        with pytest.raises(ValueError):
            MazeGenerator(5, 5, (5, 0), (4, 4), True)

    def test_end_out_of_bounds_raises(self) -> None:
        """end out of maze bounds must raise ValueError."""
        with pytest.raises(ValueError):
            MazeGenerator(5, 5, (0, 0), (5, 4), True)

    def test_start_equals_end_raises(self) -> None:
        """start == end must raise ValueError."""
        with pytest.raises(ValueError):
            MazeGenerator(5, 5, (0, 0), (0, 0), True)

    def test_valid_parameters_no_exception(self) -> None:
        """Valid parameters must not raise any exception."""
        maze = MazeGenerator(10, 10, (0, 0), (9, 9), True)
        assert maze.width == 10
        assert maze.height == 10
        assert maze.start == (0, 0)
        assert maze.end == (9, 9)


# ---------------------------------------------------------------------------
# GROUPE 2 — generate()
# ---------------------------------------------------------------------------

class TestGenerate:
    """Tests for maze generation correctness."""

    def test_grid_dimensions(self) -> None:
        """generate() must return a grid of dimensions height x width."""
        maze = MazeGenerator(10, 8, (0, 0), (9, 7), True, seed=1)
        grid = maze.generate()
        assert len(grid) == 8
        assert all(len(row) == 10 for row in grid)

    def test_cell_values_range(self) -> None:
        """All cell values must be between 0 and 15 inclusive."""
        maze = MazeGenerator(10, 8, (0, 0), (9, 7), True, seed=2)
        maze.generate()
        for row in maze.grid:
            for val in row:
                assert 0 <= val <= 15

    def test_wall_consistency_east_west(self) -> None:
        """If A has east open (bit1=0), B to the east has west open (bit3=0)."""  # noqa: E501
        maze = MazeGenerator(10, 8, (0, 0), (9, 7), True, seed=3)
        maze.generate()
        for y in range(maze.height):
            for x in range(maze.width - 1):
                east_open = maze.grid[y][x] & 2 == 0
                west_open = maze.grid[y][x + 1] & 8 == 0
                assert east_open == west_open, (
                    f"Wall inconsistency at ({x},{y}): "
                    f"east={east_open}, west_of_neighbor={west_open}"
                )

    def test_wall_consistency_south_north(self) -> None:
        """If A has south open (bit2=0), cell below has north open (bit0=0)."""
        maze = MazeGenerator(10, 8, (0, 0), (9, 7), True, seed=4)
        maze.generate()
        for y in range(maze.height - 1):
            for x in range(maze.width):
                south_open = maze.grid[y][x] & 4 == 0
                north_open = maze.grid[y + 1][x] & 1 == 0
                assert south_open == north_open, (
                    f"Wall inconsistency at ({x},{y}): "
                    f"south={south_open}, north_of_below={north_open}"
                )

    def test_seed_reproducibility(self) -> None:
        """Two generate() calls with the same seed produce identical grids."""
        maze1 = MazeGenerator(15, 10, (0, 0), (14, 9), True, seed=42)
        grid1 = maze1.generate()
        maze2 = MazeGenerator(15, 10, (0, 0), (14, 9), True, seed=42)
        grid2 = maze2.generate()
        assert grid1 == grid2

    def test_perfect_maze_full_connectivity(self) -> None:
        """Perfect maze: BFS from start must reach all non-42 cells."""
        maze = MazeGenerator(12, 10, (0, 0), (11, 9), True, seed=5)
        maze.generate()
        reachable = _bfs_reachable(maze, maze.start)
        total = maze.width * maze.height
        pattern_cells = len(maze.cell_42)
        assert len(reachable) == total - pattern_cells

    def test_pattern_42_present_large_maze(self) -> None:
        """Pattern 42 must be present if maze dimensions are >= 9x7."""
        maze = MazeGenerator(12, 10, (0, 0), (11, 9), True, seed=6)
        maze.generate()
        assert maze.can_draw_42 is True
        assert len(maze.cell_42) > 0

    def test_pattern_42_absent_small_maze(self) -> None:
        """Pattern 42 must be absent and can_draw_42=False if maze < 9x7."""
        maze = MazeGenerator(5, 5, (0, 0), (4, 4), True, seed=7)
        maze.generate()
        assert maze.can_draw_42 is False
        assert len(maze.cell_42) == 0

    def test_pattern_42_cells_value_15(self) -> None:
        """All cells of the 42 pattern must have value 15 (all walls closed)."""  # noqa: E501
        maze = MazeGenerator(15, 12, (0, 0), (14, 11), True, seed=8)
        maze.generate()
        assert maze.can_draw_42 is True
        for x, y in maze.cell_42:
            assert maze.grid[y][x] == 15, (
                f"Cell ({x},{y}) of pattern 42 has value "
                f"{maze.grid[y][x]}, expected 15"
            )

    def test_no_fully_open_2x2_area(self) -> None:
        """No 2x2 block of cells should have all four internal walls open."""
        maze = MazeGenerator(20, 15, (0, 0), (19, 14), False, seed=99)
        maze.generate()
        for y in range(maze.height - 1):
            for x in range(maze.width - 1):
                a_east = maze.grid[y][x] & 2 == 0
                a_south = maze.grid[y][x] & 4 == 0
                b_south = maze.grid[y][x + 1] & 4 == 0
                c_east = maze.grid[y + 1][x] & 2 == 0
                assert not (a_east and a_south and b_south and c_east), (
                    f"Fully open 2x2 area found at ({x},{y})"
                )

    def test_external_walls_closed(self) -> None:
        """All border cells must have their outer walls closed."""
        maze = MazeGenerator(10, 8, (0, 0), (9, 7), True, seed=10)
        maze.generate()
        for x in range(maze.width):
            assert maze.grid[0][x] & 1 == 1, (
                f"North wall open at ({x},0)"
            )
        for x in range(maze.width):
            assert maze.grid[maze.height - 1][x] & 4 == 4, (
                f"South wall open at ({x},{maze.height - 1})"
            )
        for y in range(maze.height):
            assert maze.grid[y][0] & 8 == 8, (
                f"West wall open at (0,{y})"
            )
        for y in range(maze.height):
            assert maze.grid[y][maze.width - 1] & 2 == 2, (
                f"East wall open at ({maze.width - 1},{y})"
            )


# ---------------------------------------------------------------------------
# GROUPE 3 — solve()
# ---------------------------------------------------------------------------

class TestSolve:
    """Tests for maze solving correctness."""

    def test_solve_returns_nonempty_path(self) -> None:
        """solve() must return a non-empty list for a valid connected maze."""
        maze = MazeGenerator(10, 8, (0, 0), (9, 7), True, seed=11)
        maze.generate()
        path = maze.solve()
        assert len(path) > 0

    def test_path_starts_at_start(self) -> None:
        """First element of path must be start."""
        maze = MazeGenerator(10, 8, (0, 0), (9, 7), True, seed=12)
        maze.generate()
        path = maze.solve()
        assert path[0] == maze.start

    def test_path_ends_at_end(self) -> None:
        """Last element of path must be end."""
        maze = MazeGenerator(10, 8, (0, 0), (9, 7), True, seed=13)
        maze.generate()
        path = maze.solve()
        assert path[-1] == maze.end

    def test_path_walls_open_between_steps(self) -> None:
        """Each consecutive step in path must pass through an open wall."""
        maze = MazeGenerator(10, 8, (0, 0), (9, 7), True, seed=14)
        maze.generate()
        path = maze.solve()
        for i in range(len(path) - 1):
            x, y = path[i]
            nx, ny = path[i + 1]
            val = maze.grid[y][x]
            if nx == x + 1:
                assert val & 2 == 0, f"East wall closed at ({x},{y})"
            elif nx == x - 1:
                assert val & 8 == 0, f"West wall closed at ({x},{y})"
            elif ny == y + 1:
                assert val & 4 == 0, f"South wall closed at ({x},{y})"
            elif ny == y - 1:
                assert val & 1 == 0, f"North wall closed at ({x},{y})"

    def test_solve_returns_empty_if_end_inaccessible(self) -> None:
        """solve() must return [] if end is completely isolated."""
        maze = MazeGenerator(5, 5, (0, 0), (4, 4), True, seed=15)
        maze.generate()
        ex, ey = maze.end
        maze.grid[ey][ex] = 15
        if ex + 1 < maze.width:
            maze.grid[ey][ex + 1] |= 8
        if ex - 1 >= 0:
            maze.grid[ey][ex - 1] |= 2
        if ey + 1 < maze.height:
            maze.grid[ey + 1][ex] |= 1
        if ey - 1 >= 0:
            maze.grid[ey - 1][ex] |= 4
        path = maze.solve()
        assert path == []

    def test_path_is_shortest(self) -> None:
        """Path length must equal the BFS shortest distance + 1."""
        maze = MazeGenerator(10, 8, (0, 0), (9, 7), True, seed=16)
        maze.generate()
        path = maze.solve()
        bfs_dist = _bfs_distance(maze, maze.start, maze.end)
        assert len(path) == bfs_dist + 1


# ---------------------------------------------------------------------------
# GROUPE 4 — parsing.py
# ---------------------------------------------------------------------------

class TestParsing:
    """Tests for the configuration file parser."""

    def _make_config(self, content: str) -> str:
        """Write content to a temporary file and return its path."""
        fd, path = tempfile.mkstemp(suffix=".txt")
        with os.fdopen(fd, "w") as f:
            f.write(content)
        return path

    def test_valid_config_parsed_correctly(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """A fully valid config file must be parsed with correct types."""
        config = (
            "WIDTH=20\n"
            "HEIGHT=15\n"
            "ENTRY=0,0\n"
            "EXIT=19,14\n"
            "OUTPUT_FILE=maze.txt\n"
            "PERFECT=True\n"
            "SEED=42\n"
        )
        path = self._make_config(config)
        monkeypatch.setattr("sys.argv", ["prog", path])
        from parsing import parsing
        result = parsing()
        assert result["WIDTH"] == 20
        assert result["HEIGHT"] == 15
        assert result["ENTRY"] == (0, 0)
        assert result["EXIT"] == (19, 14)
        assert result["OUTPUT_FILE"] == "maze.txt"
        assert result["PERFECT"] is True
        assert result["SEED"] == 42
        os.unlink(path)

    def test_missing_argument_exits(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Missing command-line argument must call sys.exit(1)."""
        monkeypatch.setattr("sys.argv", ["prog"])
        from parsing import parsing
        with pytest.raises(SystemExit) as exc:
            parsing()
        assert exc.value.code == 1

    def test_file_not_found_exits(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Non-existent config file must call sys.exit(1)."""
        monkeypatch.setattr(
            "sys.argv", ["prog", "/nonexistent/path/config.txt"]
        )
        from parsing import parsing
        with pytest.raises(SystemExit) as exc:
            parsing()
        assert exc.value.code == 1

    def test_missing_key_width_exits(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Config missing WIDTH key must call sys.exit(1)."""
        config = (
            "HEIGHT=15\n"
            "ENTRY=0,0\n"
            "EXIT=14,14\n"
            "OUTPUT_FILE=maze.txt\n"
            "PERFECT=True\n"
        )
        path = self._make_config(config)
        monkeypatch.setattr("sys.argv", ["prog", path])
        from parsing import parsing
        with pytest.raises(SystemExit) as exc:
            parsing()
        assert exc.value.code == 1
        os.unlink(path)

    def test_width_zero_exits(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """WIDTH=0 must call sys.exit(1)."""
        config = (
            "WIDTH=0\n"
            "HEIGHT=15\n"
            "ENTRY=0,0\n"
            "EXIT=0,14\n"
            "OUTPUT_FILE=maze.txt\n"
            "PERFECT=True\n"
        )
        path = self._make_config(config)
        monkeypatch.setattr("sys.argv", ["prog", path])
        from parsing import parsing
        with pytest.raises(SystemExit) as exc:
            parsing()
        assert exc.value.code == 1
        os.unlink(path)

    def test_width_non_integer_exits(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """WIDTH=abc must call sys.exit(1)."""
        config = (
            "WIDTH=abc\n"
            "HEIGHT=15\n"
            "ENTRY=0,0\n"
            "EXIT=0,14\n"
            "OUTPUT_FILE=maze.txt\n"
            "PERFECT=True\n"
        )
        path = self._make_config(config)
        monkeypatch.setattr("sys.argv", ["prog", path])
        from parsing import parsing
        with pytest.raises(SystemExit) as exc:
            parsing()
        assert exc.value.code == 1
        os.unlink(path)

    def test_entry_out_of_bounds_exits(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """ENTRY coordinates outside maze bounds must call sys.exit(1)."""
        config = (
            "WIDTH=10\n"
            "HEIGHT=10\n"
            "ENTRY=10,0\n"
            "EXIT=9,9\n"
            "OUTPUT_FILE=maze.txt\n"
            "PERFECT=True\n"
        )
        path = self._make_config(config)
        monkeypatch.setattr("sys.argv", ["prog", path])
        from parsing import parsing
        with pytest.raises(SystemExit) as exc:
            parsing()
        assert exc.value.code == 1
        os.unlink(path)

    def test_entry_equals_exit_exits(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """ENTRY == EXIT must call sys.exit(1)."""
        config = (
            "WIDTH=10\n"
            "HEIGHT=10\n"
            "ENTRY=0,0\n"
            "EXIT=0,0\n"
            "OUTPUT_FILE=maze.txt\n"
            "PERFECT=True\n"
        )
        path = self._make_config(config)
        monkeypatch.setattr("sys.argv", ["prog", path])
        from parsing import parsing
        with pytest.raises(SystemExit) as exc:
            parsing()
        assert exc.value.code == 1
        os.unlink(path)

    def test_perfect_invalid_value_exits(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """PERFECT=maybe must call sys.exit(1)."""
        config = (
            "WIDTH=10\n"
            "HEIGHT=10\n"
            "ENTRY=0,0\n"
            "EXIT=9,9\n"
            "OUTPUT_FILE=maze.txt\n"
            "PERFECT=maybe\n"
        )
        path = self._make_config(config)
        monkeypatch.setattr("sys.argv", ["prog", path])
        from parsing import parsing
        with pytest.raises(SystemExit) as exc:
            parsing()
        assert exc.value.code == 1
        os.unlink(path)

    def test_seed_non_integer_exits(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """SEED=abc must call sys.exit(1)."""
        config = (
            "WIDTH=10\n"
            "HEIGHT=10\n"
            "ENTRY=0,0\n"
            "EXIT=9,9\n"
            "OUTPUT_FILE=maze.txt\n"
            "PERFECT=True\n"
            "SEED=abc\n"
        )
        path = self._make_config(config)
        monkeypatch.setattr("sys.argv", ["prog", path])
        from parsing import parsing
        with pytest.raises(SystemExit) as exc:
            parsing()
        assert exc.value.code == 1
        os.unlink(path)

    def test_comment_lines_ignored(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Lines starting with # must be ignored."""
        config = (
            "# This is a comment\n"
            "WIDTH=10\n"
            "HEIGHT=10\n"
            "ENTRY=0,0\n"
            "EXIT=9,9\n"
            "OUTPUT_FILE=maze.txt\n"
            "PERFECT=True\n"
            "# Another comment\n"
        )
        path = self._make_config(config)
        monkeypatch.setattr("sys.argv", ["prog", path])
        from parsing import parsing
        result = parsing()
        assert result["WIDTH"] == 10
        os.unlink(path)

    def test_empty_lines_ignored(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Empty lines in config must be ignored without error."""
        config = (
            "\n"
            "WIDTH=10\n"
            "\n"
            "HEIGHT=10\n"
            "ENTRY=0,0\n"
            "EXIT=9,9\n"
            "OUTPUT_FILE=maze.txt\n"
            "PERFECT=True\n"
        )
        path = self._make_config(config)
        monkeypatch.setattr("sys.argv", ["prog", path])
        from parsing import parsing
        result = parsing()
        assert result["WIDTH"] == 10
        os.unlink(path)

    def test_seed_optional_absent_no_key(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """When SEED is absent, it must not appear in the returned dict."""
        config = (
            "WIDTH=10\n"
            "HEIGHT=10\n"
            "ENTRY=0,0\n"
            "EXIT=9,9\n"
            "OUTPUT_FILE=maze.txt\n"
            "PERFECT=True\n"
        )
        path = self._make_config(config)
        monkeypatch.setattr("sys.argv", ["prog", path])
        from parsing import parsing
        result = parsing()
        assert "SEED" not in result
        os.unlink(path)


# ---------------------------------------------------------------------------
# GROUPE 5 — output.py (write_output)
# ---------------------------------------------------------------------------

class TestWriteOutput:
    """Tests for the output file writer."""

    def _run(
        self, width: int = 10, height: int = 8, seed: int = 42
    ) -> tuple[MazeGenerator, list[tuple[int, int]], str]:
        """Generate maze, solve it, write output, return maze, path, fname."""
        maze = MazeGenerator(
            width, height, (0, 0),
            (width - 1, height - 1), True, seed=seed
        )
        maze.generate()
        path = maze.solve()
        fd, fname = tempfile.mkstemp(suffix=".txt")
        os.close(fd)
        write_output(fname, maze, path)
        return maze, path, fname

    def test_output_file_line_count(self) -> None:
        """Output file must have HEIGHT + 4 lines (grid + blank + 3 meta)."""
        maze, path, fname = self._run()
        with open(fname) as f:
            lines = f.readlines()
        os.unlink(fname)
        assert len(lines) == maze.height + 4

    def test_grid_line_width(self) -> None:
        """Each grid line must have exactly WIDTH hex characters."""
        maze, path, fname = self._run()
        with open(fname) as f:
            lines = f.readlines()
        os.unlink(fname)
        for i in range(maze.height):
            assert len(lines[i].rstrip("\n")) == maze.width, (
                f"Row {i} has wrong width"
            )

    def test_blank_line_after_grid(self) -> None:
        """A blank line must be present immediately after the grid rows."""
        maze, path, fname = self._run()
        with open(fname) as f:
            lines = f.readlines()
        os.unlink(fname)
        assert lines[maze.height].strip() == ""

    def test_entry_exit_coordinates_format(self) -> None:
        """Entry and exit lines must be formatted as 'x,y'."""
        maze, path, fname = self._run()
        with open(fname) as f:
            lines = f.readlines()
        os.unlink(fname)
        entry_line = lines[maze.height + 1].strip()
        exit_line = lines[maze.height + 2].strip()
        sx, sy = maze.start
        ex, ey = maze.end
        assert entry_line == f"{sx},{sy}"
        assert exit_line == f"{ex},{ey}"

    def test_path_directions_coherent(self) -> None:
        """Path string must contain only N, E, S, W characters."""
        maze, path, fname = self._run()
        with open(fname) as f:
            lines = f.readlines()
        os.unlink(fname)
        path_line = lines[maze.height + 3].strip()
        assert all(c in "NESW" for c in path_line), (
            f"Invalid characters in path: {path_line}"
        )

    def test_path_moves_match_open_walls(self) -> None:
        """Each letter in path must correspond to a valid open wall move."""
        maze, path, fname = self._run()
        with open(fname) as f:
            lines = f.readlines()
        os.unlink(fname)
        path_line = lines[maze.height + 3].strip()
        direction_map = {"E": 2, "W": 8, "S": 4, "N": 1}
        x, y = maze.start
        for direction in path_line:
            bit = direction_map[direction]
            assert maze.grid[y][x] & bit == 0, (
                f"Wall closed for direction {direction} at ({x},{y})"
            )
            if direction == "E":
                x += 1
            elif direction == "W":
                x -= 1
            elif direction == "S":
                y += 1
            elif direction == "N":
                y -= 1

    def test_all_lines_end_with_newline(self) -> None:
        """All lines in the output file must end with a newline character."""
        maze, path, fname = self._run()
        with open(fname) as f:
            lines = f.readlines()
        os.unlink(fname)
        for i, line in enumerate(lines):
            assert line.endswith("\n"), (
                f"Line {i} does not end with \\n: {repr(line)}"
            )


# ---------------------------------------------------------------------------
# GROUPE 6 — Integration end-to-end
# ---------------------------------------------------------------------------

class TestIntegration:
    """End-to-end integration tests."""

    def test_generate_solve_write_readable(self) -> None:
        """Full pipeline: generate, solve, write produces a valid file."""
        maze = MazeGenerator(15, 10, (0, 0), (14, 9), True, seed=77)
        maze.generate()
        path = maze.solve()
        fd, fname = tempfile.mkstemp(suffix=".txt")
        os.close(fd)
        write_output(fname, maze, path)
        with open(fname) as f:
            lines = f.readlines()
        os.unlink(fname)
        assert len(lines) >= maze.height

    def test_seed_42_deterministic_result(self) -> None:
        """With seed=42, WIDTH=20, HEIGHT=15: two runs produce same output."""
        def run() -> str:
            m = MazeGenerator(20, 15, (0, 0), (19, 14), True, seed=42)
            m.generate()
            p = m.solve()
            fd, fname = tempfile.mkstemp(suffix=".txt")
            os.close(fd)
            write_output(fname, m, p)
            with open(fname) as f:
                result = f.read()
            os.unlink(fname)
            return result

        assert run() == run()

    def test_imperfect_maze_solvable(self) -> None:
        """Imperfect maze (PERFECT=False) must still be solvable."""
        maze = MazeGenerator(20, 15, (0, 0), (19, 14), False, seed=123)
        maze.generate()
        reachable = _bfs_reachable(maze, maze.start)
        total = maze.width * maze.height - len(maze.cell_42)
        assert len(reachable) >= total
        path = maze.solve()
        assert len(path) > 0
        assert path[0] == maze.start
        assert path[-1] == maze.end

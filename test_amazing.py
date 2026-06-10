"""Complementary test suite for the A-Maze-ing project.

Covers angles not addressed in tests.py: negative/boundary inputs,
path uniqueness, determinism of repeated calls, extra parsing edge cases,
and integration with non-default start/end positions.
"""
import os
import sys
import tempfile

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from mazegen import MazeGenerator  # noqa: E402
from output import save_maze    # noqa: E402


# ---------------------------------------------------------------------------
# GROUPE 1 — MazeGenerator.__init__() — cas limites supplémentaires
# ---------------------------------------------------------------------------

class TestMazeGeneratorInitExtra:

    def test_negative_width_raises(self) -> None:
        with pytest.raises(ValueError):
            MazeGenerator(-1, 5, (0, 0), (0, 4), True)

    def test_negative_height_raises(self) -> None:
        with pytest.raises(ValueError):
            MazeGenerator(5, -1, (0, 0), (4, 0), True)

    def test_start_negative_x_raises(self) -> None:
        with pytest.raises(ValueError):
            MazeGenerator(5, 5, (-1, 0), (4, 4), True)

    def test_end_negative_y_raises(self) -> None:
        with pytest.raises(ValueError):
            MazeGenerator(5, 5, (0, 0), (4, -1), True)

    def test_start_at_bottom_right_end_at_top_left(self) -> None:
        maze = MazeGenerator(8, 6, (7, 5), (0, 0), True)
        assert maze.start == (7, 5)
        assert maze.end == (0, 0)

    def test_minimal_2x2_valid(self) -> None:
        maze = MazeGenerator(2, 2, (0, 0), (1, 1), True)
        assert maze.width == 2
        assert maze.height == 2

    def test_width_one_height_two_valid(self) -> None:
        maze = MazeGenerator(1, 2, (0, 0), (0, 1), True)
        assert maze.width == 1
        assert maze.height == 2

    def test_end_at_top_right_corner(self) -> None:
        maze = MazeGenerator(10, 10, (0, 9), (9, 0), True)
        assert maze.start == (0, 9)
        assert maze.end == (9, 0)


# ---------------------------------------------------------------------------
# GROUPE 2 — generate() — propriétés supplémentaires
# ---------------------------------------------------------------------------

class TestGenerateExtra:

    def test_different_seeds_produce_different_grids(self) -> None:
        maze1 = MazeGenerator(10, 8, (0, 0), (9, 7), True, seed=100)
        maze2 = MazeGenerator(10, 8, (0, 0), (9, 7), True, seed=200)
        grid1 = maze1.generate()
        grid2 = maze2.generate()
        assert grid1 != grid2

    def test_generate_twice_same_object_same_result(self) -> None:
        maze = MazeGenerator(10, 8, (0, 0), (9, 7), True, seed=55)
        grid1 = maze.generate()
        grid2 = maze.generate()
        assert grid1 == grid2

    def test_grid_not_all_zeros(self) -> None:
        maze = MazeGenerator(10, 8, (0, 0), (9, 7), True, seed=66)
        maze.generate()
        flat = [val for row in maze.grid for val in row]
        assert any(v != 0 for v in flat)

    def test_pattern_42_threshold_exactly_9x7(self) -> None:
        maze = MazeGenerator(9, 7, (0, 0), (8, 6), True, seed=77)
        maze.generate()
        assert maze.can_draw_42 is True

    def test_pattern_42_below_threshold_8x7(self) -> None:
        maze = MazeGenerator(8, 7, (0, 0), (7, 6), True, seed=88)
        maze.generate()
        assert maze.can_draw_42 is False

    def test_imperfect_maze_cell_values_range(self) -> None:
        maze = MazeGenerator(12, 10, (0, 0), (11, 9), False, seed=111)
        maze.generate()
        for row in maze.grid:
            for val in row:
                assert 0 <= val <= 15

    def test_minimal_1x2_generates_without_error(self) -> None:
        maze = MazeGenerator(1, 2, (0, 0), (0, 1), True, seed=1)
        grid = maze.generate()
        assert len(grid) == 2
        assert all(len(row) == 1 for row in grid)

    def test_wall_consistency_east_west_non_perfect(self) -> None:
        maze = MazeGenerator(10, 8, (0, 0), (9, 7), False, seed=222)
        maze.generate()
        for y in range(maze.height):
            for x in range(maze.width - 1):
                east_open = maze.grid[y][x] & 2 == 0
                west_open = maze.grid[y][x + 1] & 8 == 0
                assert east_open == west_open


# ---------------------------------------------------------------------------
# GROUPE 3 — solve() — propriétés supplémentaires
# ---------------------------------------------------------------------------

class TestSolveExtra:

    def test_path_has_no_duplicate_cells(self) -> None:
        maze = MazeGenerator(10, 8, (0, 0), (9, 7), True, seed=33)
        maze.generate()
        path = maze.solve()
        assert len(path) == len(set(path))

    def test_solve_twice_returns_same_path(self) -> None:
        maze = MazeGenerator(10, 8, (0, 0), (9, 7), True, seed=44)
        maze.generate()
        assert maze.solve() == maze.solve()

    def test_path_consecutive_steps_adjacent(self) -> None:
        maze = MazeGenerator(10, 8, (0, 0), (9, 7), True, seed=55)
        maze.generate()
        path = maze.solve()
        for i in range(len(path) - 1):
            x0, y0 = path[i]
            x1, y1 = path[i + 1]
            assert abs(x1 - x0) + abs(y1 - y0) == 1, (
                f"Non-adjacent steps at index {i}: {path[i]} -> {path[i+1]}"
            )

    def test_solve_minimal_1x2(self) -> None:
        maze = MazeGenerator(1, 2, (0, 0), (0, 1), True, seed=1)
        maze.generate()
        path = maze.solve()
        assert path[0] == (0, 0)
        assert path[-1] == (0, 1)

    def test_solve_non_default_start_end(self) -> None:
        maze = MazeGenerator(10, 10, (2, 3), (7, 8), True, seed=77)
        maze.generate()
        path = maze.solve()
        assert len(path) > 0
        assert path[0] == (2, 3)
        assert path[-1] == (7, 8)

    def test_solve_imperfect_path_valid(self) -> None:
        maze = MazeGenerator(12, 10, (0, 0), (11, 9), False, seed=99)
        maze.generate()
        path = maze.solve()
        assert len(path) > 0
        assert path[0] == maze.start
        assert path[-1] == maze.end


# ---------------------------------------------------------------------------
# GROUPE 4 — parsing.py — clés manquantes supplémentaires
# ---------------------------------------------------------------------------

class TestParsingExtra:

    def _make_config(self, content: str) -> str:
        fd, path = tempfile.mkstemp(suffix=".txt")
        with os.fdopen(fd, "w") as f:
            f.write(content)
        return path

    def _base(self, **overrides: str) -> str:
        keys: dict[str, str] = {
            "WIDTH": "10",
            "HEIGHT": "10",
            "ENTRY": "0,0",
            "EXIT": "9,9",
            "OUTPUT_FILE": "maze.txt",
            "PERFECT": "True",
        }
        keys.update(overrides)
        return "".join(f"{k}={v}\n" for k, v in keys.items())

    def test_missing_height_exits(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        config = (
            "WIDTH=10\n"
            "ENTRY=0,0\n"
            "EXIT=9,9\n"
            "OUTPUT_FILE=maze.txt\n"
            "PERFECT=True\n"
        )
        path = self._make_config(config)
        monkeypatch.setattr("sys.argv", ["prog", path])
        from parsing import parse_config
        with pytest.raises(SystemExit) as exc:
            parse_config()
        assert exc.value.code == 1
        os.unlink(path)

    def test_missing_entry_exits(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        config = (
            "WIDTH=10\n"
            "HEIGHT=10\n"
            "EXIT=9,9\n"
            "OUTPUT_FILE=maze.txt\n"
            "PERFECT=True\n"
        )
        path = self._make_config(config)
        monkeypatch.setattr("sys.argv", ["prog", path])
        from parsing import parse_config
        with pytest.raises(SystemExit) as exc:
            parse_config()
        assert exc.value.code == 1
        os.unlink(path)

    def test_missing_exit_exits(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        config = (
            "WIDTH=10\n"
            "HEIGHT=10\n"
            "ENTRY=0,0\n"
            "OUTPUT_FILE=maze.txt\n"
            "PERFECT=True\n"
        )
        path = self._make_config(config)
        monkeypatch.setattr("sys.argv", ["prog", path])
        from parsing import parse_config
        with pytest.raises(SystemExit) as exc:
            parse_config()
        assert exc.value.code == 1
        os.unlink(path)

    def test_missing_perfect_exits(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        config = (
            "WIDTH=10\n"
            "HEIGHT=10\n"
            "ENTRY=0,0\n"
            "EXIT=9,9\n"
            "OUTPUT_FILE=maze.txt\n"
        )
        path = self._make_config(config)
        monkeypatch.setattr("sys.argv", ["prog", path])
        from parsing import parse_config
        with pytest.raises(SystemExit) as exc:
            parse_config()
        assert exc.value.code == 1
        os.unlink(path)

    def test_exit_out_of_bounds_exits(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        path = self._make_config(self._base(EXIT="10,9"))
        monkeypatch.setattr("sys.argv", ["prog", path])
        from parsing import parse_config
        with pytest.raises(SystemExit) as exc:
            parse_config()
        assert exc.value.code == 1
        os.unlink(path)

    def test_negative_width_exits(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        path = self._make_config(self._base(WIDTH="-5"))
        monkeypatch.setattr("sys.argv", ["prog", path])
        from parsing import parse_config
        with pytest.raises(SystemExit) as exc:
            parse_config()
        assert exc.value.code == 1
        os.unlink(path)

    def test_height_non_integer_exits(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        path = self._make_config(self._base(HEIGHT="xyz"))
        monkeypatch.setattr("sys.argv", ["prog", path])
        from parsing import parse_config
        with pytest.raises(SystemExit) as exc:
            parse_config()
        assert exc.value.code == 1
        os.unlink(path)

    def test_seed_zero_valid(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        path = self._make_config(self._base(SEED="0"))
        monkeypatch.setattr("sys.argv", ["prog", path])
        from parsing import parse_config
        result = parse_config()
        assert result["SEED"] == 0
        os.unlink(path)

    def test_perfect_false_valid(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        path = self._make_config(self._base(PERFECT="False"))
        monkeypatch.setattr("sys.argv", ["prog", path])
        from parsing import parse_config
        result = parse_config()
        assert result["PERFECT"] is False
        os.unlink(path)


# ---------------------------------------------------------------------------
# GROUPE 5 — output.py — propriétés supplémentaires
# ---------------------------------------------------------------------------

class TestWriteOutputExtra:

    def _run(
        self,
        width: int = 10,
        height: int = 8,
        start: tuple[int, int] = (0, 0),
        end: tuple[int, int] | None = None,
        perfect: bool = True,
        seed: int = 42,
    ) -> tuple[MazeGenerator, list[tuple[int, int]], str]:
        if end is None:
            end = (width - 1, height - 1)
        maze = MazeGenerator(width, height, start, end, perfect, seed=seed)
        maze.generate()
        path = maze.solve()
        fd, fname = tempfile.mkstemp(suffix=".txt")
        os.close(fd)
        save_maze(fname, maze, path)
        return maze, path, fname

    def test_path_direction_count_matches_path_length(self) -> None:
        maze, path, fname = self._run()
        with open(fname) as f:
            lines = f.readlines()
        os.unlink(fname)
        direction_line = lines[maze.height + 3].strip()
        assert len(direction_line) == len(path) - 1

    def test_path_traversal_ends_at_end(self) -> None:
        maze, path, fname = self._run()
        with open(fname) as f:
            lines = f.readlines()
        os.unlink(fname)
        direction_line = lines[maze.height + 3].strip()
        x, y = maze.start
        for d in direction_line:
            if d == "E":
                x += 1
            elif d == "W":
                x -= 1
            elif d == "S":
                y += 1
            elif d == "N":
                y -= 1
        assert (x, y) == maze.end

    def test_file_not_empty(self) -> None:
        maze, path, fname = self._run()
        assert os.path.getsize(fname) > 0
        os.unlink(fname)

    def test_output_non_perfect_maze(self) -> None:
        maze, path, fname = self._run(perfect=False, seed=55)
        with open(fname) as f:
            lines = f.readlines()
        os.unlink(fname)
        assert len(lines) == maze.height + 4

    def test_output_non_default_start_end(self) -> None:
        maze, path, fname = self._run(
            width=12, height=10,
            start=(2, 3), end=(10, 8), seed=88
        )
        with open(fname) as f:
            lines = f.readlines()
        os.unlink(fname)
        entry_line = lines[maze.height + 1].strip()
        exit_line = lines[maze.height + 2].strip()
        assert entry_line == "2,3"
        assert exit_line == "10,8"


# ---------------------------------------------------------------------------
# GROUPE 6 — Intégration — scénarios supplémentaires
# ---------------------------------------------------------------------------

class TestIntegrationExtra:

    def test_large_maze_still_solvable(self) -> None:
        maze = MazeGenerator(50, 30, (0, 0), (49, 29), True, seed=9999)
        maze.generate()
        path = maze.solve()
        assert len(path) > 0
        assert path[0] == (0, 0)
        assert path[-1] == (49, 29)

    def test_start_end_adjacent_horizontal(self) -> None:
        maze = MazeGenerator(2, 1, (0, 0), (1, 0), True, seed=1)
        maze.generate()
        path = maze.solve()
        assert path[0] == (0, 0)
        assert path[-1] == (1, 0)

    def test_different_seeds_different_paths(self) -> None:
        maze1 = MazeGenerator(15, 10, (0, 0), (14, 9), True, seed=1)
        maze1.generate()
        path1 = maze1.solve()
        maze2 = MazeGenerator(15, 10, (0, 0), (14, 9), True, seed=2)
        maze2.generate()
        path2 = maze2.solve()
        assert path1 != path2

    def test_full_pipeline_non_default_positions(self) -> None:
        maze = MazeGenerator(20, 15, (3, 5), (18, 12), True, seed=314)
        maze.generate()
        path = maze.solve()
        fd, fname = tempfile.mkstemp(suffix=".txt")
        os.close(fd)
        save_maze(fname, maze, path)
        with open(fname) as f:
            lines = f.readlines()
        os.unlink(fname)
        assert lines[maze.height + 1].strip() == "3,5"
        assert lines[maze.height + 2].strip() == "18,12"

    def test_repeated_full_pipeline_deterministic(self) -> None:
        def run() -> str:
            m = MazeGenerator(15, 10, (1, 2), (13, 8), True, seed=7)
            m.generate()
            p = m.solve()
            fd, fname = tempfile.mkstemp(suffix=".txt")
            os.close(fd)
            save_maze(fname, m, p)
            with open(fname) as f:
                content = f.read()
            os.unlink(fname)
            return content

        assert run() == run()

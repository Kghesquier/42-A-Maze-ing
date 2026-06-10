import random
from collections import deque


class MazeGenerator:
    """Maze generator using iterative DFS with backtracking.

    Each cell is encoded as a 4-bit bitmask (N=1, E=2, S=4, W=8).
    Supports both perfect mazes (single unique path) and imperfect ones
    (with loops), and optionally places a '42' pattern of fully closed cells.

    Attributes:
        width:       Number of cells horizontally.
        height:      Number of cells vertically.
        start:       Entry point as (x, y).
        end:         Exit point as (x, y).
        perfect:     True for a perfect maze (no loops).
        seed:        Optional RNG seed for reproducibility.
        grid:        2D list of bitmasks representing cell walls.
        visited:     Cells already visited during generation.
        cell_42:     Cells belonging to the '42' pattern.
        can_draw_42: True if the '42' pattern was successfully placed.
    """

    def __init__(self, width: int, height: int,
                 start: tuple[int, int], end: tuple[int, int],
                 perfect: bool, seed: int | None = None) -> None:
        """Validate parameters and initialize the generator.

        Args:
            width:   Number of cells horizontally (>= 1).
            height:  Number of cells vertically (>= 1).
            start:   Entry point (x, y), within maze bounds.
            end:     Exit point (x, y), within maze bounds,
                     must differ from start.
            perfect: True to generate a maze with no loops.
            seed:    Optional RNG seed for reproducibility.

        Raises:
            ValueError: If width/height < 1, start/end out of bounds,
                        or start == end.
        """
        if width < 1:
            raise ValueError(f"width must be >= 1, got {width}")
        if height < 1:
            raise ValueError(f"height must be >= 1, got {height}")
        if not (0 <= start[0] < width and 0 <= start[1] < height):
            raise ValueError(
                f"start {start} is out of bounds ({width}x{height})"
            )
        if not (0 <= end[0] < width and 0 <= end[1] < height):
            raise ValueError(
                f"end {end} is out of bounds ({width}x{height})"
            )
        if start == end:
            raise ValueError("start and end must be different")
        self.width = width
        self.height = height
        self.start = start
        self.end = end
        self.perfect = perfect
        self.seed = seed
        self.grid = self._init_grid()
        self.visited: set[tuple[int, int]] = set()
        self.cell_42: set[tuple[int, int]] = set()
        self.can_draw_42 = True

    def _init_grid(self) -> list[list[int]]:
        """Build the initial grid with all walls closed (value 15 = 0b1111).

        Returns:
            2D list of integers, one per cell, with all 4 walls set.
        """
        return [[15] * self.width for _ in range(self.height)]

    def _reset(self) -> None:
        """Reset the maze state before regeneration.

        Clears the grid, visited cells, the 42 pattern cells,
        and the can_draw_42 flag.
        """
        self.grid = self._init_grid()
        self.visited = set()
        self.cell_42 = set()
        self.can_draw_42 = True

    def _unvisited_neighbors(self, x: int, y: int) -> list[tuple[int, int]]:
        """Return the unvisited neighbors of cell (x, y).

        Args:
            x: Column index of the cell.
            y: Row index of the cell.

        Returns:
            List of (x, y) tuples for adjacent cells not yet visited.
        """
        neighbors = []
        if y + 1 < self.height and (x, y + 1) not in self.visited:
            neighbors.append((x, y + 1))
        if x + 1 < self.width and (x + 1, y) not in self.visited:
            neighbors.append((x + 1, y))
        if y - 1 >= 0 and (x, y - 1) not in self.visited:
            neighbors.append((x, y - 1))
        if x - 1 >= 0 and (x - 1, y) not in self.visited:
            neighbors.append((x - 1, y))
        return neighbors

    def _place_logo(self) -> None:
        """Try to place the '42' pattern on the grid.

        Attempts the center position first, then the four corners.
        Pattern cells are marked as visited so the DFS skips them.
        Sets can_draw_42 to False if the maze is too small or no valid
        position avoids start and end.
        """
        if self.width < 9 or self.height < 7:
            self.can_draw_42 = False
            return
        candidate_positions = [
            ((self.width - 7) // 2, (self.height - 5) // 2),
            (1, 1),
            (self.width - 8, 1),
            (1, self.height - 6),
            (self.width - 8, self.height - 6),
        ]
        logo_shape = [
            (0, 0), (0, 1), (0, 2), (1, 2), (2, 2), (2, 3),
            (2, 4), (4, 0), (5, 0), (6, 0), (6, 1), (4, 2),
            (5, 2), (6, 2), (4, 3), (4, 4), (5, 4), (6, 4),
        ]
        for ox, oy in candidate_positions:
            logo_cells = [(x + ox, y + oy) for x, y in logo_shape]
            if self.start not in logo_cells and self.end not in logo_cells:
                for cell in logo_cells:
                    self.visited.add(cell)
                    self.cell_42.add(cell)
                return
        self.can_draw_42 = False

    def _east_wall_safe(self, x: int, y: int) -> bool:
        """Check if removing the east wall creates a 2x2 open area.

        Args:
            x: Column index of the cell.
            y: Row index of the cell.

        Returns:
            True if the wall can be safely removed, False otherwise.
        """
        if y + 1 < self.height and x + 1 < self.width:
            if (self.grid[y][x] & 4 == 0
                    and self.grid[y][x + 1] & 4 == 0
                    and self.grid[y + 1][x] & 2 == 0):
                return False
        if y - 1 >= 0 and x + 1 < self.width:
            if (self.grid[y - 1][x] & 2 == 0
                    and self.grid[y - 1][x] & 4 == 0
                    and self.grid[y - 1][x + 1] & 4 == 0):
                return False
        if x - 1 >= 0 and y + 1 < self.height:
            if (self.grid[y][x - 1] & 2 == 0
                    and self.grid[y][x - 1] & 4 == 0
                    and self.grid[y][x] & 4 == 0
                    and self.grid[y + 1][x - 1] & 2 == 0):
                return False
        if x - 1 >= 0 and y - 1 >= 0:
            if (self.grid[y - 1][x - 1] & 2 == 0
                    and self.grid[y - 1][x - 1] & 4 == 0
                    and self.grid[y - 1][x] & 4 == 0
                    and self.grid[y][x - 1] & 2 == 0):
                return False
        return True

    def _south_wall_safe(self, x: int, y: int) -> bool:
        """Check if removing the south wall creates a 2x2 open area.

        Args:
            x: Column index of the cell.
            y: Row index of the cell.

        Returns:
            True if the wall can be safely removed, False otherwise.
        """
        if x + 1 < self.width and y + 1 < self.height:
            if (self.grid[y][x] & 2 == 0
                    and self.grid[y][x + 1] & 4 == 0
                    and self.grid[y + 1][x] & 2 == 0):
                return False
        if x - 1 >= 0 and y + 1 < self.height:
            if (self.grid[y][x - 1] & 2 == 0
                    and self.grid[y][x - 1] & 4 == 0
                    and self.grid[y + 1][x - 1] & 2 == 0):
                return False
        if x + 1 < self.width and y - 1 >= 0:
            if (self.grid[y - 1][x] & 2 == 0
                    and self.grid[y - 1][x] & 4 == 0
                    and self.grid[y - 1][x + 1] & 4 == 0
                    and self.grid[y][x] & 2 == 0):
                return False
        if x - 1 >= 0 and y - 1 >= 0:
            if (self.grid[y - 1][x - 1] & 2 == 0
                    and self.grid[y - 1][x - 1] & 4 == 0
                    and self.grid[y - 1][x] & 4 == 0
                    and self.grid[y][x - 1] & 2 == 0):
                return False
        return True

    def _add_loops(self) -> None:
        """Randomly remove walls to introduce loops in the maze.

        Iterates over the grid and removes east/south walls with a 25%
        probability, only if it would not create a 2x2 open area and neither
        affected cell belongs to the 42 pattern.
        """
        for y in range(self.height):
            for x in range(self.width):
                if (x + 1 < self.width
                        and (x, y) not in self.cell_42
                        and (x + 1, y) not in self.cell_42
                        and self._east_wall_safe(x, y)):
                    if random.random() < 0.25:
                        self.grid[y][x] &= ~2
                        self.grid[y][x + 1] &= ~8
                if (y + 1 < self.height
                        and (x, y) not in self.cell_42
                        and (x, y + 1) not in self.cell_42
                        and self._south_wall_safe(x, y)):
                    if random.random() < 0.25:
                        self.grid[y][x] &= ~4
                        self.grid[y + 1][x] &= ~1

    def generate(self) -> list[list[int]]:
        """Generate the maze using iterative DFS with backtracking.

        Resets the grid, places the 42 pattern, then carves passages from
        start using a stack. Calls _add_loops() at the end if perfect is False.

        Returns:
            The generated grid as a 2D list of wall bitmasks.
        """
        if self.seed is not None:
            random.seed(self.seed)
        self._reset()
        self._place_logo()
        stack = [self.start]
        self.visited.add(self.start)
        while stack:
            x, y = stack[-1]
            candidates = self._unvisited_neighbors(x, y)
            if candidates:
                neighbor = random.choice(candidates)
                nx, ny = neighbor
                if x < nx:
                    self.grid[y][x] &= ~2
                    self.grid[ny][nx] &= ~8
                elif x > nx:
                    self.grid[y][x] &= ~8
                    self.grid[ny][nx] &= ~2
                elif y < ny:
                    self.grid[y][x] &= ~4
                    self.grid[ny][nx] &= ~1
                elif y > ny:
                    self.grid[y][x] &= ~1
                    self.grid[ny][nx] &= ~4
                stack.append(neighbor)
                self.visited.add(neighbor)
            else:
                stack.pop()
        if not self.perfect:
            self._add_loops()
        return self.grid

    def _open_wall_neighbors(
            self,
            pos: tuple[int, int],
            visited: dict[tuple[int, int], tuple[int, int] | None]
    ) -> list[tuple[int, int]]:
        """Return neighbors reachable from pos through open walls.

        Args:
            pos:     The (x, y) position to check from.
            visited: Cells already visited by the BFS solver.

        Returns:
            List of (x, y) tuples reachable through open walls,
            not yet visited.
        """
        reachable = []
        x, y = pos
        if x + 1 < self.width and self.grid[y][x] & 2 == 0 \
                and (x + 1, y) not in visited:
            reachable.append((x + 1, y))
        if x - 1 >= 0 and self.grid[y][x] & 8 == 0 \
                and (x - 1, y) not in visited:
            reachable.append((x - 1, y))
        if y + 1 < self.height and self.grid[y][x] & 4 == 0 \
                and (x, y + 1) not in visited:
            reachable.append((x, y + 1))
        if y - 1 >= 0 and self.grid[y][x] & 1 == 0 \
                and (x, y - 1) not in visited:
            reachable.append((x, y - 1))
        return reachable

    def solve(self) -> list[tuple[int, int]]:
        """Solve the maze with BFS and return the shortest path.

        Must be called after generate(). Only travels through open walls.

        Returns:
            List of (x, y) tuples from start to end inclusive.
            Empty list if end is unreachable from start.
        """
        queue: deque[tuple[int, int]] = deque([self.start])
        came_from: dict[tuple[int, int], tuple[int, int] | None] = {
            self.start: None
        }
        while queue:
            pos = queue.popleft()
            if pos == self.end:
                break
            for nb in self._open_wall_neighbors(pos, came_from):
                came_from[nb] = pos
                queue.append(nb)
        if self.end not in came_from:
            return []
        path: list[tuple[int, int]] = []
        current: tuple[int, int] | None = self.end
        while current is not None:
            path.append(current)
            current = came_from[current]
        path.reverse()
        return path

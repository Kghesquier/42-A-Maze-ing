import random
from collections import deque


class MazeGenerator:
    """Maze generator using recursive backtracker (DFS) algorithm.

    Generates a maze by carving passages through a grid, optionally placing
    a '42' pattern of fully closed cells, and supports both perfect mazes
    (single unique path) and imperfect ones (with loops).

    Attributes:
        width:       Number of cells horizontally.
        height:      Number of cells vertically.
        start:       Entry point as (x, y).
        end:         Exit point as (x, y).
        perfect:     If True, generates a perfect maze (one unique path).
        seed:        Optional RNG seed for reproducibility.
        grid:        2D list of integers representing wall bitmasks per cell.
        visit:       Set of (x, y) cells already visited during generation.
        cell_42:     Set of (x, y) cells belonging to the '42' pattern.
        can_draw_42: True if the '42' pattern was successfully placed.
    """

    def __init__(self, width: int, height: int,
                 start: tuple[int, int], end: tuple[int, int],
                 perfect: bool, seed: int | None = None) -> None:
        """Initialize the MazeGenerator with the given parameters.

        Args:
            width:   Number of cells horizontally (must be >= 1).
            height:  Number of cells vertically (must be >= 1).
            start:   Entry point as (x, y), within maze bounds.
            end:     Exit point as (x, y), within maze bounds,
                     must differ from start.
            perfect: If True, generates a perfect maze (one unique path).
            seed:    Optional RNG seed for reproducibility.

        Raises:
            ValueError: If width or height < 1, if start or end are out of
                        bounds, or if start == end.
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
        self.grid = self.grid_setup()
        self.visit: set[tuple[int, int]] = set()
        self.cell_42: set[tuple[int, int]] = set()
        self.can_draw_42 = True

    def grid_setup(self) -> list[list[int]]:
        """Initialize the grid with all walls closed (value 15 = 0b1111).

        Returns:
            A 2D list of integers, one per cell, with all 4 walls set.
        """
        grid = [[15] * self.width for _ in range(self.height)]
        return grid

    def reset(self) -> None:
        """Reset the maze to its initial state.

        Reinitializes the grid, visited cells, 42 pattern cells,
        and the can_draw_42 flag. Used before regenerating a maze.
        """
        self.grid = self.grid_setup()
        self.visit = set()
        self.cell_42 = set()
        self.can_draw_42 = True

    def get_neighbors(self, x: int, y: int) -> list[tuple[int, int]]:
        """Return unvisited neighbors of the cell at (x, y).

        Args:
            x: Column index of the current cell.
            y: Row index of the current cell.

        Returns:
            List of (x, y) tuples for adjacent unvisited cells.
        """
        neighbors = []
        if 0 <= y + 1 < self.height and (x, y + 1) not in self.visit:
            neighbors.append((x, y + 1))
        if 0 <= x + 1 < self.width and (x + 1, y) not in self.visit:
            neighbors.append((x + 1, y))
        if 0 <= y - 1 < self.height and (x, y - 1) not in self.visit:
            neighbors.append((x, y - 1))
        if 0 <= x - 1 < self.width and (x - 1, y) not in self.visit:
            neighbors.append((x - 1, y))
        return neighbors

    def draw_42(self) -> None:
        """Attempt to place the '42' pattern on the maze grid.

        Tries several positions (centered first, then corners).
        Marks the pattern cells as visited and stores them in cell_42
        so the generator avoids carving through them.
        Sets can_draw_42 to False if the maze is too small or no valid
        position is found.
        """
        if self.width < 9 or self.height < 7:
            self.can_draw_42 = False
            return
        try_pos = [((self.width - 7) // 2, (self.height - 5) // 2),
                   (1, 1), (self.width - 8, 1), (1, self.height - 6),
                   (self.width - 8, self.height - 6)]
        logo = [(0, 0), (0, 1), (0, 2), (1, 2), (2, 2), (2, 3),
                (2, 4), (4, 0), (5, 0), (6, 0), (6, 1), (4, 2),
                (5, 2), (6, 2), (4, 3), (4, 4), (5, 4), (6, 4)]
        for offset_x, offset_y in try_pos:
            offset_logo = [(x + offset_x, y + offset_y) for x, y in logo]
            if self.start not in offset_logo and self.end not in offset_logo:
                for pos in offset_logo:
                    self.visit.add(pos)
                    self.cell_42.add(pos)
                return
        self.can_draw_42 = False

    def create_open_area_est(self, x: int, y: int) -> bool:
        """Check if removing the east wall of (x, y) would create an open area.

        Checks all four possible 2x2 squares that include the east wall
        between (x, y) and (x+1, y) to ensure no open area is created.

        Args:
            x: Column index of the current cell.
            y: Row index of the current cell.

        Returns:
            True if the wall can be removed safely, False otherwise.
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

    def create_open_area_south(self, x: int, y: int) -> bool:
        """Check if removing south wall of (x, y) would create an open area.

        Checks all four possible 2x2 squares that include the south wall
        between (x, y) and (x, y+1) to ensure no open area is created.

        Args:
            x: Column index of the current cell.
            y: Row index of the current cell.

        Returns:
            True if the wall can be removed safely, False otherwise.
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

    def imperfect(self) -> None:
        """Randomly remove walls to create loops and open areas.

        Iterates over the grid and removes east/south walls with a 25%
        probability, only if doing so would not create a 2x2 open area
        and neither cell belongs to the 42 pattern.
        """
        for y in range(self.height):
            for x in range(self.width):
                if (self.create_open_area_est(x, y)
                        and (x, y) not in self.cell_42
                        and (x + 1, y) not in self.cell_42
                        and x + 1 < self.width):
                    if random.random() < 0.25:
                        self.grid[y][x] &= ~2
                        self.grid[y][x + 1] &= ~8
                if (self.create_open_area_south(x, y)
                        and (x, y) not in self.cell_42
                        and (x, y + 1) not in self.cell_42
                        and y + 1 < self.height):
                    if random.random() < 0.25:
                        self.grid[y][x] &= ~4
                        self.grid[y + 1][x] &= ~1

    def generate(self) -> list[list[int]]:
        """Generate the maze using a recursive backtracker algorithm.

        Seeds the RNG only if a seed was provided, resets the grid, places
        the 42 pattern, then carves passages using an iterative depth-first
        search with a stack. If PERFECT is False, calls imperfect() to add
        extra openings.

        Returns:
            The generated grid as a 2D list of integers (wall bitmasks).
        """
        if self.seed is not None:
            random.seed(self.seed)
        self.reset()
        stack = [self.start]
        self.draw_42()
        self.visit.add(self.start)
        while stack:
            x, y = stack[-1]
            neighbors = self.get_neighbors(x, y)
            if len(neighbors) != 0:
                next_cell = random.choice(neighbors)
                x_n, y_n = next_cell
                if x < x_n:
                    self.grid[y][x] &= ~2
                    self.grid[y_n][x_n] &= ~8
                elif x > x_n:
                    self.grid[y][x] &= ~8
                    self.grid[y_n][x_n] &= ~2
                elif y < y_n:
                    self.grid[y][x] &= ~4
                    self.grid[y_n][x_n] &= ~1
                elif y > y_n:
                    self.grid[y][x] &= ~1
                    self.grid[y_n][x_n] &= ~4
                stack.append(next_cell)
                self.visit.add(next_cell)
            else:
                stack.pop()
        if not self.perfect:
            self.imperfect()
        return self.grid

    def reachable_neighbors(
            self,
            current_cell: tuple[int, int],
            came_from: dict[tuple[int, int], tuple[int, int] | None]
    ) -> list[tuple[int, int]]:
        """Return neighbors reachable from current_cell through open walls.

        Args:
            current_cell: The (x, y) position to check from.
            came_from:    Dict of already-visited cells used by the BFS solver.

        Returns:
            List of (x, y) tuples reachable through open walls
            and not yet visited.
        """
        reachable = []
        x, y = current_cell
        if x + 1 < self.width and self.grid[y][x] & 2 == 0 \
                and (x + 1, y) not in came_from:
            reachable.append((x + 1, y))
        if x - 1 >= 0 and self.grid[y][x] & 8 == 0 \
                and (x - 1, y) not in came_from:
            reachable.append((x - 1, y))
        if y + 1 < self.height and self.grid[y][x] & 4 == 0 \
                and (x, y + 1) not in came_from:
            reachable.append((x, y + 1))
        if y - 1 >= 0 and self.grid[y][x] & 1 == 0 \
                and (x, y - 1) not in came_from:
            reachable.append((x, y - 1))
        return reachable

    def solve(self) -> list[tuple[int, int]]:
        """Solve the maze using BFS and return the shortest path.

        Finds the shortest path from start to end by exploring
        cells through open walls. Must be called after generate().

        Returns:
            List of (x, y) tuples representing the shortest path
            from start to end, inclusive. Returns an empty list if
            end is not reachable from start.
        """
        queue: deque[tuple[int, int]] = deque()
        queue.append(self.start)
        came_from: dict[tuple[int, int], tuple[int, int] | None] = {
            self.start: None
        }
        while queue:
            current_cell = queue.popleft()
            if current_cell == self.end:
                break
            for neighbor in self.reachable_neighbors(current_cell, came_from):
                came_from[neighbor] = current_cell
                queue.append(neighbor)
        if self.end not in came_from:
            return []
        path = []
        current: tuple[int, int] | None = self.end
        while current is not None:
            path.append(current)
            current = came_from[current]
        path.reverse()
        return path

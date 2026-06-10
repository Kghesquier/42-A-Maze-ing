import sys
import curses
import time
from mazegen import MazeGenerator
from output import write_output


def display_maze(stdscr: curses.window,
                 maze: MazeGenerator, output_name: str) -> None:
    """Display the maze and handle user interactions using curses.

    Generates and renders the maze with an animated display, shows the
    solution path, and writes the output file. Handles user inputs to
    re-generate the maze, show/hide the solution path, and rotate colors.

    Args:
        stdscr:      The curses window object provided by curses.wrapper.
        maze:        The MazeGenerator instance used to generate and solve
                     the maze.
        output_name: Path to the output file where the maze will be written.

    User interactions:
        1: Re-generate a new maze and display it.
        2: Show/Hide the solution path.
        3: Rotate maze wall colors.
        4 or q: Quit the program.
    """
    curses.start_color()
    curses.curs_set(0)
    stdscr.keypad(True)
    curses.init_pair(1, curses.COLOR_BLUE, curses.COLOR_BLUE)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_GREEN)
    curses.init_pair(3, curses.COLOR_RED, curses.COLOR_RED)
    curses.init_pair(4, curses.COLOR_MAGENTA, curses.COLOR_MAGENTA)
    curses.init_pair(5, curses.COLOR_WHITE, curses.COLOR_WHITE)
    curses.init_pair(6, curses.COLOR_BLACK, curses.COLOR_BLACK)
    curses.init_pair(7, curses.COLOR_RED, curses.COLOR_BLACK)
    key_pres = ord(' ')
    show_path = True
    color_bool = True
    blue = 1
    green = 2
    red = 3
    magenta = 4
    white = 5
    black = 6
    color_path = white
    color_start = green
    color_end = red
    color_wall = blue
    color_42 = magenta

    width = maze.width
    height = maze.height
    start = maze.start
    end = maze.end

    total_width = 3 * width + 1
    total_height = 2 * height + 1
    block = "\u2588"
    x_0 = 1
    y_0 = 1
    x_s = start[0] * 3 + x_0
    y_s = start[1] * 2 + y_0
    x_e = end[0] * 3 + x_0
    y_e = end[1] * 2 + y_0

    animate = True
    path_animate = True
    try:
        grid = maze.generate()
        path = maze.solve()
        write_output(output_name, maze, path)
    except Exception as e:
        curses.endwin()
        sys.stderr.write(f"ERROR: Maze init failed: {e}\n")
        sys.exit(1)

    while True:
        try:
            term_height, term_width = stdscr.getmaxyx()
            if total_width > term_width or total_height > term_height:
                stdscr.clear()
                stdscr.addstr(0, 0, "Terminal too small! Please resize. "
                              "or press 'q' to quit.")
                stdscr.refresh()
                key_pres = stdscr.getch()
                if key_pres == ord('q') or key_pres == ord('4'):
                    break
                continue

            stdscr.addstr(total_height + 1, 0, "=== A-Maze-ing ===")
            stdscr.addstr(total_height + 2, 0, "1. Re-generate a new maze")
            stdscr.addstr(total_height + 3, 0, "2. Show/Hide "
                          "path from entry to exit")
            stdscr.addstr(total_height + 4, 0, "3. Rotate maze colors")
            stdscr.addstr(total_height + 5, 0, "4. Quit")
            stdscr.addstr(total_height + 6, 0, "Choice? (1-4): ")
            stdscr.addstr(total_height + 6, 15, str(chr(key_pres)))
            if not maze.can_draw_42:
                stdscr.addstr(total_height + 7, 0,
                              "[ALERT]: The 42 logo cannot be displayed.",
                              curses.color_pair(7))

            for i in range(total_height):
                stdscr.addstr(0 + i, 0, block * total_width,
                              curses.color_pair(color_wall))

            for y in range(total_height - 2):
                for x in range(total_width - 2):
                    if x % 3 == 0 and y % 2 == 0:
                        stdscr.addstr(0 + y + 1, 0 + x + 1, " " * 2)

            for cy in range(height):
                for cx in range(width):
                    val = grid[cy][cx]
                    px = x_0 + cx * 3
                    py = y_0 + cy * 2
                    if not (val & 1):
                        stdscr.addstr(py - 1, px, block * 2,
                                      curses.color_pair(black))
                    if not (val & 2):
                        stdscr.addstr(py, px + 2, block,
                                      curses.color_pair(black))
                    if not (val & 4):
                        stdscr.addstr(py + 2, px, block * 2,
                                      curses.color_pair(black))
                    if not (val & 8):
                        stdscr.addstr(py, px - 1, block,
                                      curses.color_pair(black))
                    if val == 15:
                        stdscr.addstr(py, px, block * 2,
                                      curses.color_pair(color_42))
                if animate:
                    stdscr.refresh()
                    time.sleep(0.05)
            animate = False

            if show_path:
                for i in range(len(path) - 1):
                    curr_x, curr_y = path[i]
                    next_x, next_y = path[i + 1]
                    x_path = x_0 + curr_x * 3
                    y_path = y_0 + curr_y * 2
                    stdscr.addstr(y_path, x_path, block * 2,
                                  curses.color_pair(color_path))
                    stdscr.addstr(y_s, x_s, block * 2,
                                  curses.color_pair(color_start))
                    stdscr.addstr(y_e, x_e, block * 2,
                                  curses.color_pair(color_end))
                    if curr_x == next_x and curr_y > next_y:
                        stdscr.addstr(y_path - 1, x_path, block * 2,
                                      curses.color_pair(color_path))
                    if curr_x < next_x and curr_y == next_y:
                        stdscr.addstr(y_path, x_path + 2, block,
                                      curses.color_pair(color_path))
                    if curr_x == next_x and curr_y < next_y:
                        stdscr.addstr(y_path + 1, x_path, block * 2,
                                      curses.color_pair(color_path))
                    if curr_x > next_x and curr_y == next_y:
                        stdscr.addstr(y_path, x_path - 1, block,
                                      curses.color_pair(color_path))
                    if path_animate:
                        stdscr.refresh()
                        time.sleep(0.01)
            else:
                stdscr.addstr(y_s, x_s, block * 2,
                              curses.color_pair(color_start))
                stdscr.addstr(y_e, x_e, block * 2,
                              curses.color_pair(color_end))
            path_animate = False

            stdscr.nodelay(True)
            while stdscr.getch() != -1:
                pass
            stdscr.nodelay(False)
            key_pres = stdscr.getch()
            if key_pres == ord('q') or key_pres == ord('4'):
                break
            if key_pres == ord('1'):
                grid = maze.generate()
                path = maze.solve()
                write_output(output_name, maze, path)
                animate = True
                path_animate = show_path
            if key_pres == ord('2') and show_path:
                show_path = False
            elif key_pres == ord('2'):
                show_path = True
                path_animate = True
            if key_pres == ord('3') and color_bool:
                color_wall = magenta
                color_42 = blue
                color_bool = False
            elif key_pres == ord('3'):
                color_wall = blue
                color_42 = magenta
                color_bool = True
        except curses.error:
            stdscr.clear()
            stdscr.addstr(0, 0, "Terminal too small! "
                          "Please resize. or press 'q' to quit.")
            stdscr.refresh()
            key_pres = stdscr.getch()
            if key_pres == ord('q') or key_pres == ord('4'):
                break
        except Exception as e:
            stdscr.clear()
            stdscr.addstr(0, 0, f"ERROR: Unexpected error: {e}")
            stdscr.refresh()
            stdscr.getch()
            break

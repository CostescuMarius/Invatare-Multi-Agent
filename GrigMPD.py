class GridMDP:
    def __init__(self, grid_values, terminals, init=(0, 0)):
        grid = grid_values.copy()
        grid.reverse()  # Reverse rows so that (0, 0) is at the bottom-left
        self.grid = grid
        self.terminals = terminals
        self.init = init

        self.rows = len(grid)
        self.cols = len(grid[0])

        self.states = set()
        self.rewards = {}

        for y in range(self.rows):
            for x in range(self.cols):
                if grid[y][x] is not None:  # Non-obstacle states
                    self.states.add((x, y))
                    self.rewards[(x, y)] = grid[y][x]

    def display_grid(self):
        for row in reversed(self.grid):
            print(" ".join([f"{cell}" if cell is not None else "   X" for cell in row]))


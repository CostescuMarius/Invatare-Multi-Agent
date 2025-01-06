import tkinter as tk
from tkinter import simpledialog
from GrigMPD import GridMDP
from SimpleAgent import SimpleAgent
from ADP import AdaptiveDynamicProgramming
import random

north = (0, 1)
south = (0,-1)
west = (-1, 0)
east = (1, 0)

TERMINAL_REWARD_VALUE = 1.0


class GridApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Grid Interactiv")

        self.GRID_ROWS = 2
        self.GRID_COLS = 2
        
        self.grid_values = None
        self.buttons = None
        self.current_state = None
        self.start_pos = None
        self.terminals = []

        self.create_controls()

        self.create_grid()

    def create_controls(self):
        tk.Label(self.root, text="Rows:").grid(row=0, column=0)
        self.row_input = tk.Entry(self.root, width=5)
        self.row_input.grid(row=0, column=1)
        self.row_input.insert(0, str(self.GRID_ROWS))

        tk.Label(self.root, text="Cols:").grid(row=0, column=2)
        self.col_input = tk.Entry(self.root, width=5)
        self.col_input.grid(row=0, column=3)
        self.col_input.insert(0, str(self.GRID_COLS))

        set_button = tk.Button(self.root, text="Set Grid", command=self.set_grid_size)
        set_button.grid(row=0, column=4)

        run_button = tk.Button(self.root, text="Run ADP", command=self.run_ADP)
        run_button.grid(row=0, column=5)


    def set_grid_size(self):
        try:
            rows = int(self.row_input.get())
            cols = int(self.col_input.get())
            if rows > 0 and rows <= 25 and cols > 0 and cols <= 20:
                self.GRID_ROWS = rows
                self.GRID_COLS = cols
                self.create_grid()  # Re-creează grila corect
            else:
                print("Dimensiunile trebuie să fie mai mari decât 0!")
        except ValueError:
            print("Dimensiuni invalide!")

    def create_grid(self):
        for widget in self.root.grid_slaves():
            if int(widget.grid_info()["row"]) > 0:
                widget.destroy()

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        table_width = screen_width // 3
        table_height = screen_height // 3

        cell_width = (table_width // self.GRID_COLS) // 10
        cell_height = (table_height // self.GRID_ROWS) // 10

        if cell_width < 6:
            cell_width = 6

        # Reinițializează grila și butoanele
        self.grid_values = [[0.00 for _ in range(self.GRID_COLS)] for _ in range(self.GRID_ROWS)]
        self.buttons = [[None for _ in range(self.GRID_COLS)] for _ in range(self.GRID_ROWS)]

        for row in range(self.GRID_ROWS):
            for col in range(self.GRID_COLS):
                button = tk.Button(self.root, width=cell_width, height=cell_height, bg="white")
                button.grid(row=row + 1, column=col)
                button.bind("<Button-3>", lambda event, r=row, c=col: self.show_context_menu(event, r, c))
                self.buttons[row][col] = button

        # Meniu contextual pentru celule
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Start", command=lambda: self.set_start(self.selected_row, self.selected_col))
        self.context_menu.add_command(label="Terminal", command=lambda: self.set_terminal(self.selected_row, self.selected_col))
        self.context_menu.add_command(label="Obstacle", command=lambda: self.set_obstacle(self.selected_row, self.selected_col))
        self.context_menu.add_command(label="Reward", command=lambda: self.set_reward(self.selected_row, self.selected_col))

    def show_context_menu(self, event, row, col):
        self.selected_row = row
        self.selected_col = col
        self.context_menu.post(event.x_root, event.y_root)

    def set_environment(self, row, col, color, value):
        self.clear_grid_cell(row, col)
        self.grid_values[row][col] = value
        self.buttons[row][col].config(bg=color)

    def set_start(self, row, col):
        self.set_environment(row, col, 'green', 0.0)
        self.start_pos = (row, col)

    def set_terminal(self, row, col):
        self.set_environment(row, col, 'blue', TERMINAL_REWARD_VALUE)
        self.terminals.append((row, col))

    def set_obstacle(self, row, col):
        self.set_environment(row, col, 'black', None)

    def set_reward(self, row, col):
        try:
            value = simpledialog.askfloat("Set Reward", "Enter reward value:", minvalue=-1000, maxvalue=1000)

            if value is not None:
                self.set_environment(row, col, 'yellow', value)
        except Exception as e:
            print("Invalid input:", e)

    def clear_grid_cell(self, row, col):
        if (row, col) in self.terminals:
            self.terminals.remove((row, col))
        self.grid_values[row][col] = 0.00
        self.buttons[row][col].config(bg='white')

    def get_grid_input(self):
        adjusted_terminals = [(col, self.GRID_ROWS - row - 1) for (row, col) in self.terminals]
        print (adjusted_terminals)

        return self.grid_values, self.start_pos, adjusted_terminals
    
    def generate_random_policy(self, mdp):
        actions = [north, south, west, east]
        random_policy = {}

        for state in mdp.states:
            if state in mdp.terminals:
                random_policy[state] = None
            else:
                random_policy[state] = random.choice(actions)

        return random_policy


    def run_ADP(self):
        grid_values, start_pos, terminals = self.get_grid_input()
        print (grid_values)

        def mark_agent(row, col):
            if self.buttons[row][col].cget('bg') == 'white':
                self.buttons[row][col].config(bg='red')


        def clear_agent():
            for r in range(self.GRID_ROWS):
                for c in range(self.GRID_COLS):
                    if self.buttons[r][c].cget('bg') == 'red':
                        self.buttons[r][c].config(bg='white')

        def gui_update(state):
            row, col = self.GRID_ROWS - 1 - state[1], state[0]
            
            clear_agent()
            mark_agent(row, col)
            
            self.root.update()
            self.root.after(1000)


        mdp = GridMDP(grid_values, terminals)
        policy = self.generate_random_policy(mdp)
        agent = SimpleAgent(policy)
        adp = AdaptiveDynamicProgramming(mdp, agent, gui_callback=gui_update)

        print("##########################################################\n\nGrid:")

        mdp.display_grid()

        print (f"Terminals: {terminals}")

        print ('\nInitial Policy:')
        adp.print_policy()

        print("\nUtilities Evolusion:")
        adp.iterate_utilities(epsilon=0.01, max_iterations=100)

        print ('\nUtilities:')
        adp.print_utilities()

        print ('\nPolicy:')
        adp.print_policy()
        print("\n##########################################################")


if __name__ == "__main__":
    root = tk.Tk()
    app = GridApp(root)
    
    # Crează un buton pentru a obține input-ul când este apăsat
    # btn_get_input = tk.Button(root, text="Run ADP", command=app.run_ADP)
    # btn_get_input.grid(row=100, column=0, columnspan=100) 
    root.geometry(f"{root.winfo_screenwidth()}x{root.winfo_screenheight()}")
    root.resizable(True, True)
    root.bind("<Escape>", lambda event: root.destroy())
    root.mainloop()

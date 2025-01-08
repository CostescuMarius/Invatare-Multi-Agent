import tkinter as tk
from tkinter import simpledialog
from GrigMPD import GridMDP
from SimpleAgent import SimpleAgent
from ADP import AdaptiveDynamicProgramming
import random
from tkinter import messagebox
import matplotlib.pyplot as plt

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
        self.start_pos = None
        self.terminals = []

        self.mdp = None
        self.agent = None
        self.adp = None

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

        self.grid_values = None
        self.buttons = None
        self.start_pos = None
        self.terminals = []
        self.mdp = None
        self.agent = None
        self.adp = None

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        table_width = screen_width // 3
        table_height = screen_height // 3

        cell_width = (table_width // self.GRID_COLS) // 10
        cell_height = (table_height // self.GRID_ROWS) // 10

        if cell_width < 6:
            cell_width = 6

        # reinitializare butoane
        self.grid_values = [[0.00 for _ in range(self.GRID_COLS)] for _ in range(self.GRID_ROWS)]
        self.buttons = [[None for _ in range(self.GRID_COLS)] for _ in range(self.GRID_ROWS)]

        for row in range(self.GRID_ROWS):
            for col in range(self.GRID_COLS):
                button = tk.Button(self.root, width=cell_width, height=cell_height, bg="white", text=f"{self.grid_values[row][col]:.2f}")
                button.grid(row=row + 1, column=col)
                button.bind("<Button-3>", lambda event, r=row, c=col: self.show_context_menu(event, r, c))
                self.buttons[row][col] = button

        # Meniu pentru celule
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Start", command=lambda: self.set_start(self.selected_row, self.selected_col))
        self.context_menu.add_command(label="Terminal", command=lambda: self.set_terminal(self.selected_row, self.selected_col))
        self.context_menu.add_command(label="Obstacle", command=lambda: self.set_obstacle(self.selected_row, self.selected_col))
        self.context_menu.add_command(label="Reward", command=lambda: self.set_reward(self.selected_row, self.selected_col))
        self.context_menu.add_command(label="Clear", command=lambda: self.clear_grid_cell(self.selected_row, self.selected_col))

    def show_context_menu(self, event, row, col):
        self.selected_row = row
        self.selected_col = col
        self.context_menu.post(event.x_root, event.y_root)

    def set_environment(self, row, col, color, value):
        self.clear_grid_cell(row, col)
        self.grid_values[row][col] = value
        self.buttons[row][col].config(bg=color)
        self.buttons[row][col].config(text=f'{value}')

    def set_start(self, row, col):
        self.start_pos = (row, col)

        if self.agent.policy is None:
            messagebox.showerror("Error", "First run ADP!")
        else:
            self.draw_policy_path()

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
        self.buttons[row][col].config(text=f'{0.00}')
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
                valid_actions = []
                
                for action in actions:
                    next_state = (state[0] + action[0], state[1] + action[1])
                    
                    if 0 <= next_state[0] < self.GRID_ROWS and 0 <= next_state[1] < self.GRID_COLS:
                        valid_actions.append(action)
                

                if valid_actions:
                    random_policy[state] = random.choice(valid_actions)
                else:
                    random_policy[state] = None

        return random_policy
    

    def clear_path(self):
        for r in range(self.GRID_ROWS):
            for c in range(self.GRID_COLS):
                if self.buttons[r][c].cget('bg') == 'green' or self.buttons[r][c].cget('bg') == 'red':
                    self.buttons[r][c].config(bg='white')

    def draw_policy_path(self):
        self.clear_path()

        start_col, start_row = self.GRID_ROWS - 1 - self.start_pos[0], self.start_pos[1]
        current_pos = (start_row, start_col)

        self.buttons[self.start_pos[0]][self.start_pos[1]].config(bg='green')
        visited_states = set()

        adjusted_terminals = [(col, self.GRID_ROWS - row - 1) for (row, col) in self.terminals]
        while current_pos not in adjusted_terminals:
            if current_pos in visited_states:
                break
            visited_states.add(current_pos)

            action = self.agent.policy.get(current_pos, None)
            if action is None:
                break

            next_pos = (current_pos[0] + action[0], current_pos[1] + action[1])
            if next_pos in adjusted_terminals:
                break

            gui_col = next_pos[0]
            gui_row = self.GRID_ROWS - 1 - next_pos[1]

            if (0 <= next_pos[1] < self.GRID_ROWS and 0 <= next_pos[0] < self.GRID_COLS and self.grid_values[next_pos[1]][next_pos[0]] is not None):
                self.buttons[gui_row][gui_col].config(bg='green')

                current_pos = next_pos
                
            else:
                break

    def plot_delta(self, delta_per_iteration):
        iterations = list(range(1, len(delta_per_iteration) + 1))
        
        deltas = delta_per_iteration

        plt.figure(figsize=(10, 6))
        plt.plot(iterations, deltas, marker='o', color='b', label='Delta')

        plt.xlabel('Iteratii')
        plt.ylabel('Delta')
        plt.title('Evolutia Delta per fiecare iteratie')
        plt.yscale('log')
        plt.grid(True)
        plt.legend()
        plt.show()

    def plot_policies(self, policy_per_iteration):
        changes_per_iteration = []
    
        for i in range(1, len(policy_per_iteration)):
            current_policy = policy_per_iteration[i]
            previous_policy = policy_per_iteration[i - 1]
            
            changes = 0
            for state in current_policy:
                if current_policy[state] != previous_policy.get(state, None):
                    changes += 1
            
            changes_per_iteration.append(changes)
        
        changes_per_iteration = [0] + changes_per_iteration


        iterations = list(range(1, len(changes_per_iteration) + 1))

        changes = changes_per_iteration

        plt.figure(figsize=(10, 6))
        plt.plot(iterations, changes, marker='o', color='r', label='Schimbari in policy')

        plt.xlabel('Iteratii')
        plt.ylabel('Numar de schimbari în politica')
        plt.title('Schimbari în politica pe iteratii')
        plt.grid(True)
        plt.legend()

        plt.show()


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

        def gui_update(current_state, next_state, utility_value):
            current_row, current_col = self.GRID_ROWS - 1 - current_state[1], current_state[0]
            self.buttons[current_row][current_col].config(text=f"{utility_value:.2f}")

            move_row, move_col = self.GRID_ROWS - 1 - next_state[1], next_state[0]
            clear_agent()
            mark_agent(move_row, move_col)

            self.root.update()
            self.root.after(1)
            

        self.mdp = GridMDP(grid_values, terminals)
        initial_policy = self.generate_random_policy(self.mdp)
        self.agent = SimpleAgent(initial_policy)
        self.adp = AdaptiveDynamicProgramming(self.mdp, self.agent, gui_callback=gui_update)

        print("##########################################################\n\nGrid:")

        self.mdp.display_grid()

        print (f"Terminals: {terminals}")

        print ('\nInitial Policy:')
        self.adp.print_policy()

        print("\nUtilities Evolusion:")
        delta_per_iteration, policy_per_iteration = self.adp.iterate_utilities(epsilon=0.01, max_iterations=100)
        self.plot_delta(delta_per_iteration)
        self.plot_policies(policy_per_iteration)


        print ('\nUtilities:')
        self.adp.print_utilities()

        print ('\nPolicy:')
        self.adp.print_policy()
        print("\n##########################################################")


if __name__ == "__main__":
    root = tk.Tk()
    app = GridApp(root)
    
    root.geometry(f"{root.winfo_screenwidth()}x{root.winfo_screenheight()}")
    root.resizable(True, True)
    root.bind("<Escape>", lambda event: root.destroy())
    root.mainloop()

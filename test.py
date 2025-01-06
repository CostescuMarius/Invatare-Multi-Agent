import numpy as np
import random
import matplotlib.pyplot as plt

class GridMDP:
    def __init__(self, grid, terminals, init=(0, 0), gamma=0.9):
        grid.reverse()  # Reversing rows to make (0, 0) at bottom-left
        self.grid = grid
        self.terminals = terminals
        self.init = init
        self.gamma = gamma  # Discount factor

        self.rows = len(grid)
        self.cols = len(grid[0])

        self.states = set()
        self.rewards = {}
        self.transitions = {}

        for y in range(self.rows):
            for x in range(self.cols):
                if grid[y][x] is not None:  # Non-obstacle states
                    self.states.add((x, y))
                    self.rewards[(x, y)] = grid[y][x]

        # Initializing transition model (empty table for now)
        for state in self.states:
            self.transitions[state] = {action: [] for action in ['UP', 'DOWN', 'LEFT', 'RIGHT']}
    
    def display_grid(self):
        """Affichează gridul cu obstacole și stările terminale"""
        for row in reversed(self.grid):
            print(" ".join([f"{cell}" if cell is not None else "   X" for cell in row]))
    
    def get_neighbors(self, state):
        """Obține vecinii unui punct, excluzând obstacolele"""
        x, y = state
        neighbors = []
        if x > 0 and self.grid[y][x - 1] is not None:  # Left
            neighbors.append((x - 1, y))
        if x < self.cols - 1 and self.grid[y][x + 1] is not None:  # Right
            neighbors.append((x + 1, y))
        if y > 0 and self.grid[y - 1][x] is not None:  # Up
            neighbors.append((x, y - 1))
        if y < self.rows - 1 and self.grid[y + 1][x] is not None:  # Down
            neighbors.append((x, y + 1))
        return neighbors
    
    def update_transitions(self, state, action, next_state):
        """Actualizează modelul de tranziție pentru starea și acțiunea dată"""
        self.transitions[state][action].append(next_state)
    
    def get_transition_prob(self, state, action, next_state):
        """Calculăm probabilitatea de tranziție P(s' | s, a)"""
        count = self.transitions[state][action].count(next_state)
        total = len(self.transitions[state][action])
        return count / total if total > 0 else 0
    
    def value_iteration(self, epsilon=0.01):
        """Funcția de iterație a valorii pentru calcularea utilității stărilor"""
        utilities = {state: 0 for state in self.states}
        iteration = 0
        
        while True:
            max_diff = 0
            for state in self.states:
                if state in self.terminals:
                    continue  # Nu actualizăm utilitatea pentru stările terminale
                action_utilities = []
                for action in ['UP', 'DOWN', 'LEFT', 'RIGHT']:
                    action_value = 0
                    for next_state in self.get_neighbors(state):
                        reward = self.rewards.get(next_state, 0)
                        prob = self.get_transition_prob(state, action, next_state)
                        action_value += prob * (reward + self.gamma * utilities[next_state])
                    action_utilities.append(action_value)
                best_action_value = max(action_utilities)
                max_diff = max(max_diff, abs(utilities[state] - best_action_value))
                utilities[state] = best_action_value
            iteration += 1
            if max_diff < epsilon:
                break
            print(f"Iteration {iteration} - max_diff: {max_diff}")
        return utilities

# Testarea agentului

grid = [
    [0, 0, 0, 1, 0],
    [0, 1, 0, 1, 0],
    [0, 0, 0, 0, 0],
    [1, 1, 1, 0, 0]
]

terminals = {(4, 0), (0, 4)}  # Stările terminale

mdp = GridMDP(grid, terminals)

# Exemple de actualizare a tranzițiilor (pe măsură ce agentul se deplasează)
mdp.update_transitions((1, 1), 'UP', (1, 2))
mdp.update_transitions((1, 2), 'RIGHT', (2, 2))
mdp.update_transitions((2, 2), 'DOWN', (2, 1))

# Apelăm valoarea iterativă pentru a calcula utilitățile
utilities = mdp.value_iteration()

# Vizualizarea utilităților în grid
utility_matrix = np.array([[utilities.get((x, y), 0) for x in range(mdp.cols)] for y in range(mdp.rows)])
plt.imshow(utility_matrix, cmap='hot', interpolation='nearest')
plt.colorbar()
plt.title('Utilitățile Stărilor')
plt.show()

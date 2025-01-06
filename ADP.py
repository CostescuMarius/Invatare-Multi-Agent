import numpy as np

class AdaptiveDynamicProgramming:
    def __init__(self, mdp, agent, gamma=0.9, gui_callback=None):
        self.mdp = mdp
        self.agent = agent
        self.gamma = gamma
        self.gui_callback = gui_callback
        
        self.U = {s: 0 for s in mdp.states}
        for terminal in mdp.terminals:
            self.U[terminal] = mdp.rewards.get(terminal, 0)

        self.transitions = {
            (0, 1): [(0.8, (0, 1)), (0.1, (-1, 0)), (0.1, (1, 0))],  # North
            (0, -1): [(0.8, (0, -1)), (0.1, (-1, 0)), (0.1, (1, 0))], # South
            (-1, 0): [(0.8, (-1, 0)), (0.1, (0, 1)), (0.1, (0, -1))], # West
            (1, 0): [(0.8, (1, 0)), (0.1, (0, 1)), (0.1, (0, -1))]   # East
        }

        

    def update_utilities(self):
        U_new = self.U.copy()
        for state in self.mdp.states:
            if state in self.mdp.terminals:
                continue

            action = self.agent.act(state)
            if action is not None:
                expected_utility = 0
                for prob, move in self.transitions[action]:
                    next_state = (state[0] + move[0], state[1] + move[1])

                    if next_state in self.mdp.states:
                        self.agent.update_state(next_state)
                        
                        expected_utility += prob * self.U[next_state]
                    else:
                        expected_utility += prob * self.U[state]

                    if self.gui_callback:
                        self.gui_callback(self.agent.current_state)

                # Formula Bellman
                U_new[state] = self.mdp.rewards[state] + self.gamma * expected_utility

        self.U = U_new

    def print_utilities(self):
        grid = [[self.U.get((x, y), None) for x in range(self.mdp.cols)] for y in range(self.mdp.rows)]
        for row in reversed(grid):
            print([f'{val}' if val is not None else ' X ' for val in row])


    def update_policy(self):
        new_policy = {}
        
        for state in self.mdp.states:
            if state in self.mdp.terminals:
                continue

            best_action = None
            max_utility = float('-inf')

            for action in [(0, 1), (0, -1), (-1, 0), (1, 0)]:
                next_state = (state[0] + action[0], state[1] + action[1])

                if next_state in self.mdp.states:
                    #utility = self.mdp.rewards[state] + self.gamma * self.U.get(next_state, 0)
                    utility = self.U[next_state]

                    if utility > max_utility:
                        max_utility = utility
                        best_action = action
            
            new_policy[state] = best_action

        self.agent.policy = new_policy

    def print_policy(self):
        grid = [[self.agent.policy.get((x, y), None) for x in range(self.mdp.cols)] for y in range(self.mdp.rows)]
        for row in reversed(grid):
            print([f'{val}' if val is not None else ' X ' for val in row])


    def iterate_utilities(self, epsilon=0.01, max_iterations=100):
        for i in range(max_iterations):
            prev_U = self.U.copy()
            self.update_utilities()

            delta = max(abs(self.U[s] - prev_U[s]) for s in self.mdp.states)
            print(f"Iteration {i + 1}, Delta: {delta:.4f}")

            if delta < epsilon:
                print("Done!")
                break

            self.update_policy()
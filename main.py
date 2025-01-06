from GrigMPD import GridMDP
from SimpleAgent import SimpleAgent
from ADP import AdaptiveDynamicProgramming
import random

north = (0, 1)
south = (0,-1)
west = (-1, 0)
east = (1, 0)

def generate_random_policy(mdp):
    actions = [north, south, west, east]
    random_policy = {}

    for state in mdp.states:
        if state in mdp.terminals:
            random_policy[state] = None
        else:
            random_policy[state] = random.choice(actions)

    return random_policy


grid = [
    [0, +10],
    [None, 0.5],
    [0.5, 0.5]
]
terminals = [(1, 2)]



mdp = GridMDP(grid, terminals)
policy = generate_random_policy(mdp)
agent = SimpleAgent(policy)
adp = AdaptiveDynamicProgramming(mdp, agent)

print("##########################################################\n\nGrid:")

mdp.display_grid()

print ('\nInitial Policy:')
adp.print_policy()

print("\nUtilities Evolusion:")
adp.iterate_utilities(epsilon=0.01, max_iterations=100)

print ('\nUtilities:')
adp.print_utilities()

print ('\nPolicy:')
adp.print_policy()
print("\n##########################################################")
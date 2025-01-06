class SimpleAgent:
    def __init__(self, policy):
        self.policy = policy
        self.current_state = (0, 0)

    def act(self, state):
        return self.policy.get(state, None)
    
    def update_state(self, new_state):
        self.current_state = new_state
class SimpleAgent:
    def __init__(self, policy):
        self.policy = policy
        self.current_state = (0, 0)
        self.move_state = (0, 0)

    def act(self, state):
        return self.policy.get(state, None)
    
    def update_current_state(self, new_state):
        self.current_state = new_state

    def update_move_state(self, new_state):
        self.move_state = new_state

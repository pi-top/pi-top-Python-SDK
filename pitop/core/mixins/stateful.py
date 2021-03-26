from json import dumps


class Stateful:
    """Represents an object with a particular set of important properties that
    represent its state."""

    def __init__(self, children=[]):
        self.children = children

    @property
    def own_state(self):
        """Representation of an object state that will be used to determine the
        current state of an object."""
        return {}

    def __child_state(self, child_name):
        child = getattr(self, child_name)
        if hasattr(child, "state"):
            return child.state
        return None

    @property
    def state(self):
        """Returns a dictionary with the state of the current object and all of
        its children."""
        state = self.own_state
        for k, v in state.items():
            if callable(v):
                state[k] = v()
        for child in self.children:
            child_state = self.__child_state(child)
            if child_state is None:
                continue
            state[child] = child_state
        return state

    def print_state(self):
        print(dumps(self.state, indent=4))

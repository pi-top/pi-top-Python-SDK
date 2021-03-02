class Stateful:
    def __init__(self, children=[]):
        self.children = children

    @property
    def own_state(self):
        return {}

    def __child_state(self, child):
        return getattr(self, child).component_state

    @property
    def component_state(self):
        state = self.own_state
        for k, v in state.items():
            if callable(v):
                state[k] = v()
        for child in self.children:
            state[child] = self.__child_state(child)
        return state

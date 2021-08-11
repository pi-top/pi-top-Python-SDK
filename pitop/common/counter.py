class Counter:
    """A simple counter class."""

    def __init__(self, max_val, current=0):
        self.current = current
        self.max = max_val

    def increment(self):
        if self.current < self.max:
            self.current += 1
            return True
        else:
            return False

    def reset(self):
        self.current = 0

    def maxed(self):
        return self.current == self.max

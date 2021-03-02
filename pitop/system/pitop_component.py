
class PiTopComponent:
    def __init__(self, ports, args):
        args.pop("self", None)
        self.ports = ports
        self.args = args

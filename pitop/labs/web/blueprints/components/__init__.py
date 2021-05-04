from flask import Blueprint


class ComponentsBlueprint(Blueprint):
    def __init__(self, **kwargs):
        Blueprint.__init__(
            self,
            "components",
            __name__,
            static_folder="components",
            **kwargs
        )

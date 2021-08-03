from flask import Blueprint


class BaseBlueprint(Blueprint):
    def __init__(self, name="base", **kwargs):
        Blueprint.__init__(
            self,
            name,
            __name__,
            template_folder="templates",
            static_folder="base",
            **kwargs
        )

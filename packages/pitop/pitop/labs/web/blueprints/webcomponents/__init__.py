from flask import Blueprint


class WebComponentsBlueprint(Blueprint):
    def __init__(self, **kwargs):
        Blueprint.__init__(
            self,
            "webcomponents",
            __name__,
            static_folder="webcomponents",
            template_folder="templates",
            **kwargs
        )

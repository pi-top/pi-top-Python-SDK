from flask import Blueprint, g
import gevent


class BatteryBlueprint(Blueprint):
    def __init__(self, name="battery", battery=None, messaging_blueprint=None, **kwargs):
        Blueprint.__init__(
            self,
            name=name,
            import_name=__name__,
            static_folder="battery",
            template_folder="templates",
            **kwargs
        )

        @self.before_app_request
        def set_show_battery():
            g.show_battery = (battery is not None)

        self.battery = battery
        self.messaging_blueprint = messaging_blueprint
        if self.battery is not None:
            gevent.spawn(self.battery_update)

    def battery_update(self):
        while True:
            battery_state = self.battery.get_full_state()
            message = {
                'type': 'battery_state',
                'data': battery_state
            }
            self.broadcast(message)
            gevent.sleep(1)

    def broadcast(self, message):
        self.messaging_blueprint.broadcast(message)

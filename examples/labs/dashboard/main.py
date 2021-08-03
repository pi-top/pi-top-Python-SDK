from time import sleep

import gevent
from pitop import LED, Button, Pitop, UltrasonicSensor
from pitop.labs import WebController

robot = Pitop()
robot.add_component(Button("D1"))
robot.add_component(LED("D2"))
robot.add_component(UltrasonicSensor("D3"))

dashboard_server = WebController()


def broadcast_state():
    while True:
        sleep(0.1)
        dashboard_server.broadcast(robot.state)


hub = gevent.get_hub()
hub.threadpool.spawn(broadcast_state)

dashboard_server.serve_forever()

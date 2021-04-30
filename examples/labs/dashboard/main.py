from pitop import Pitop, LED, Button, UltrasonicSensor
from pitop.labs import WebController
from time import sleep
import gevent

robot = Pitop()
robot.add_component(LED('D1'))
robot.add_component(UltrasonicSensor('D2'))
robot.add_component(Button('D3'))

dashboard_server = WebController()


def broadcast_state():
    while True:
        sleep(0.1)
        dashboard_server.broadcast(robot.state)


hub = gevent.get_hub()
hub.threadpool.spawn(broadcast_state)

dashboard_server.serve_forever()

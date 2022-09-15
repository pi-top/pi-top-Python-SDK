from pitop import Pitop
from pitop.pma import LED, Button
from time import sleep

pitop = Pitop()
pitop.add_component(LED("D0", name="led1"))
pitop.add_component(Button("D1", name="button1"))
pitop.add_component(LED("D2", name="led2", color="green"))
pitop.add_component(Button("D3", name="button2"))
pitop.add_component(LED("D4", name="led3"))
pitop.add_component(Button("D5", name="button3"))
pitop.add_component(LED("D6", name="led4", color="yellow"))
pitop.add_component(Button("D7", name="button4"))

pitop.button1.when_pressed = pitop.led1.on
pitop.button1.when_released = pitop.led1.off

pitop.button2.when_pressed = pitop.led2.on
pitop.button2.when_released = pitop.led2.off

pitop.button3.when_pressed = pitop.led3.on
pitop.button3.when_released = pitop.led3.off

pitop.button4.when_pressed = pitop.led4.on
pitop.button4.when_released = pitop.led4.off

pitop.simulate()
pitop.led4.simulate()
##pitop.button4.simulate()
sleep(10)
pitop.stop_simulation()
sleep(1)
## TODO stopping multiple sims at the same tim kills the xserver
pitop.led4.stop_simulation()
##pitop.button4.stop_simulation()

from pitop.simulation import simulate, use_virtual_hardware

use_virtual_hardware()

from time import sleep  # noqa: E402

from pitop import (  # noqa: E402
    Buzzer,
    LightSensor,
    Pitop,
    Potentiometer,
    SoundSensor,
    UltrasonicSensor,
)

pitop = Pitop()
pitop.add_component(Buzzer("D2"))
pitop.add_component(Potentiometer("A0"))
pitop.add_component(SoundSensor("A1"))
pitop.add_component(LightSensor("A2"))
pitop.add_component(UltrasonicSensor("D3"))

simulate(pitop)

while True:
    pitop.buzzer.toggle()
    sleep(1)

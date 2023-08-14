from unittest.mock import patch


def test_led_state_keys():
    from pitop.pma import LED

    led = LED("D7")
    assert set(led.own_state.keys()) == {"is_lit", "value"}
    led.close()


def test_button_state_keys():
    from pitop.pma import Button

    button = Button("D7")
    assert set(button.own_state.keys()) == {"is_held", "is_pressed", "value"}
    button.close()


def test_buzzer_state_keys():
    from pitop.pma import Buzzer

    buzzer = Buzzer("D7")
    assert set(buzzer.own_state.keys()) == {"is_active", "value"}
    buzzer.close()


def test_ultrasonic_sensor_state_keys():
    from pitop.pma import UltrasonicSensor

    buzzer = UltrasonicSensor("D7")
    assert set(buzzer.own_state.keys()) == {"distance"}
    buzzer.close()


def test_light_sensor_state_keys():
    from pitop.pma import LightSensor

    light_sensor = LightSensor("A0")
    assert set(light_sensor.own_state.keys()) == {"value", "reading"}


def test_potentiometer_state_keys():
    from pitop.pma import Potentiometer

    potentiometer = Potentiometer("A0")
    assert set(potentiometer.own_state.keys()) == {"position"}


def test_sound_sensor_state_keys():
    from pitop.pma import SoundSensor

    sound_sensor = SoundSensor("A0")
    assert set(sound_sensor.own_state.keys()) == {"value", "reading"}


def test_encoder_motor_state_keys():
    from pitop.pma import EncoderMotor

    encoder_motor = EncoderMotor("M0", forward_direction=1)
    assert set(encoder_motor.own_state.keys()) == {
        "forward_direction",
        "current_rpm",
        "braking_type",
        "wheel_diameter",
        "distance",
        "current_speed",
    }


@patch("pitop.pma.servo_motor.ServoController")
def test_servo_motor_state_keys(_):
    from pitop.pma import ServoMotor

    servo_motor = ServoMotor("S0")
    servo_motor._controller.get_current_angle_and_speed = lambda: (0, 0)
    servo_motor.target_angle = 0
    assert set(servo_motor.own_state.keys()) == {"angle", "speed"}


@patch("pitop.camera.camera.UsbCamera", autospec=True)
def test_camera_state_keys(_):
    from pitop import Camera

    camera = Camera()
    assert set(camera.own_state.keys()) == {"running", "capture_actions"}


def test_drive_controller_state_keys():
    from pitop import DriveController

    drive_controller = DriveController()
    assert set(drive_controller.own_state.keys()) == set()


@patch("pitop.pma.servo_motor.ServoController")
def test_pan_tilt_controller_state_keys(_):
    from pitop import PanTiltController

    pan_tilt_controller = PanTiltController()
    assert set(pan_tilt_controller.own_state.keys()) == set()


@patch("pitop.pma.servo_motor.ServoController")
def test_pincer_controller_state_keys(_):
    from pitop import PincerController

    pincer_controller = PincerController()
    assert set(pincer_controller.own_state.keys()) == set()


@patch("pitop.pma.servo_motor.ServoController")
def test_tilt_roll_controller_state_keys(_):
    from pitop import TiltRollHeadController

    tilt_roll_controller = TiltRollHeadController()
    assert set(tilt_roll_controller.own_state.keys()) == set()

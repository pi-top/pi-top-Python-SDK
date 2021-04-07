var cmd_vel_twist = {
  'linear': {
    'x': 0.0
  },
  'angular': {
    'z': 0.0
  }
};

var pan_tilt_position = {
  'angle': {
    'y': 0.0,
    'z': 0.0
  }
};

const MAX_LINEAR_SPEED = 0.44;
const MAX_ANGULAR_SPEED = 5.12;
const MAX_SERVO_ANGLE = 90;
var publishCmdVelImmediately = true;
var publishPanTiltImmediately = true;

function cmdVelTwistPublisher(linear, angular) {
    if (linear !== undefined && angular !== undefined) {
        cmd_vel_twist.linear.x = linear;
        cmd_vel_twist.angular.z = angular;
    } else {
        cmd_vel_twist.linear.x = 0;
        cmd_vel_twist.angular.z = 0;
    }
    window.command['cmd_vel'](cmd_vel_twist);
}

function panTiltPositionPublisher(angle_y, angle_z) {
    if (angle_y !== undefined && angle_z !== undefined) {
        pan_tilt_position.angle.y = angle_y;
        pan_tilt_position.angle.z = angle_z;
    } else {
        pan_tilt_position.angle.y = 0;
        pan_tilt_position.angle.z = 0;
    }
    window.command['pan_tilt'](pan_tilt_position);
}

['left', 'right'].forEach((position) => {
    const joystickZone = document.getElementById(position + 'JoystickContainer');

    const joystick = nipplejs.create({
        zone: joystickZone,
        mode: 'static',
        size: 200,
        position: {top: 50, [position]: 50}
    }).get();

    joystick.on('move', (evt, joystick) => {

        let direction = joystick.angle.degree - 90;
        if (direction > 180) {
            direction = -(450 - joystick.angle.degree);
        }

        if (position === "left") {
            // joystick distance max is 100, so set that to be maximum speeds
            let linear = Math.cos(direction / 57.29) * joystick.distance * MAX_LINEAR_SPEED / 100.0;
            let angular = Math.sin(direction / 57.29) * joystick.distance * MAX_ANGULAR_SPEED / 100.0;
            if (publishCmdVelImmediately) {
              publishCmdVelImmediately = false;
              cmdVelTwistPublisher(linear, angular);
              setTimeout(function () {
                publishCmdVelImmediately = true;
              }, 50);
            }
        } else {
            let angle_y = -Math.cos(direction / 57.29) * joystick.distance * MAX_SERVO_ANGLE / 100.0;
            let angle_z = Math.sin(direction / 57.29) * joystick.distance * MAX_SERVO_ANGLE / 100.0;
            if (publishPanTiltImmediately) {
              publishPanTiltImmediately = false;
              panTiltPositionPublisher(angle_y, angle_z);
              setTimeout(function () {
                publishPanTiltImmediately = true;
              }, 50);
            }

        }
    });

    joystick.on('end', (evt) => {
        joystick.frontPosition.x = 0;
        joystick.frontPosition.y = 0;
        if (position === "left") {
          for (let i = 0; i < 3; i++) {
              setTimeout(function () {
                cmdVelTwistPublisher(0, 0);
              }, i * 10);
          }
        } else {
            for (let i = 0; i < 3; i++) {
              setTimeout(function () {
                panTiltPositionPublisher(0, 0);
              }, i * 10);
          }
        }
    });
});

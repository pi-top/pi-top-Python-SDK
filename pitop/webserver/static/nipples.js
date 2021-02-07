var cmd_vel_twist = {
  'linear': {
    'x': 0.0
  },
  'angular': {
    'z': 0.0
  }
};

var pan_tilt_twist = {
  'angular': {
    'y': 0.0,
    'z': 0.0
  }
};

const MAX_LINEAR_SPEED = 0.44;
const MAX_ANGULAR_SPEED = 5.12;
const MAX_SERVO_SPEED = 100;
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
    // console.log(linear)
    window.command['cmd_vel'](cmd_vel_twist);
}

function panTiltTwistPublisher(angular_y, angular_z) {
    if (angular_y !== undefined && angular_z !== undefined) {
        pan_tilt_twist.angular.y = angular_y;
        pan_tilt_twist.angular.z = angular_z;
    } else {
        pan_tilt_twist.linear.x = 0;
        pan_tilt_twist.angular.z = 0;
    }
    // console.log(linear)
    window.command['pan_tilt'](pan_tilt_twist);
}

['left', 'right'].forEach((position) => {
    const nippleZone = document.getElementById(position + 'NippleContainer');

    const nipple = nipplejs.create({
        zone: nippleZone,
        mode: 'static',
        size: 200,
        position: {top: 50, [position]: 50}
    }).get();

    nipple.on('move', (evt, nipple) => {

        let direction = nipple.angle.degree - 90;
        if (direction > 180) {
            direction = -(450 - nipple.angle.degree);
        }

        if (position === "left") {
            // nipple distance max is 100, so set that to be maximum speeds
            let linear = Math.cos(direction / 57.29) * nipple.distance * MAX_LINEAR_SPEED / 100.0;
            let angular = Math.sin(direction / 57.29) * nipple.distance * MAX_ANGULAR_SPEED / 100.0;
            if (publishCmdVelImmediately) {
              publishCmdVelImmediately = false;
              cmdVelTwistPublisher(linear, angular);
              setTimeout(function () {
                publishCmdVelImmediately = true;
              }, 50);
            }
        } else {
            let angular_y = -Math.cos(direction / 57.29) * nipple.distance * MAX_SERVO_SPEED / 100.0;
            let angular_z = Math.sin(direction / 57.29) * nipple.distance * MAX_SERVO_SPEED / 100.0;
            if (publishPanTiltImmediately) {
              publishPanTiltImmediately = false;
              panTiltTwistPublisher(angular_y, angular_z);
              setTimeout(function () {
                publishPanTiltImmediately = true;
              }, 50);
            }

        }
    });

    nipple.on('end', (evt) => {
        nipple.frontPosition.x = 0;
        nipple.frontPosition.y = 0;
        if (position === "left") {
          for (let i = 0; i < 3; i++) {
              setTimeout(function () {
                cmdVelTwistPublisher(0, 0);
              }, i * 10);
          }
        } else {
            for (let i = 0; i < 3; i++) {
              setTimeout(function () {
                panTiltTwistPublisher(0, 0);
              }, i * 10);
          }
        }
    });
});

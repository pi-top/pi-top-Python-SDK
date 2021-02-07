
var twist_data = {
  'linear': {
    'x': 0.0
  },
  'angular': {
    'z': 0.0
  }
};

['left', 'right'].forEach((position) => {
    const nippleZone = document.getElementById(position + 'NippleContainer');

    const nipple = nipplejs.create({
        zone: nippleZone,
        mode: 'static',
        size: 200,
        position: {top: 50, [position]: 50}
    }).get();

    nipple.on('move', (evt, nipple) => {

        var direction = nipple.angle.degree - 90;
        if (direction > 180) {
            direction = -(450 - nipple.angle.degree);
        }

        if (position === "left") {
            var linear = Math.cos(direction / 57.29) * nipple.distance * 0.008;
            var angular = Math.sin(direction / 57.29) * nipple.distance * 0.03;
            twist_data.linear.x = linear;
            twist_data.angular.z = angular;
            window.command['cmd_vel'](twist_data);
        } else {
            window.command['servo_move'](nipple);
        }
    });

    nipple.on('end', (evt) => {
        nipple.frontPosition.x = 0;
        nipple.frontPosition.y = 0;
        if (position === "left") {
            twist_data.linear.x = 0.0;
            twist_data.angular.z = 0.0;
            window.command['cmd_vel'](twist_data);
        } else {
            window.command['servo_stop']();
        }
    });
});
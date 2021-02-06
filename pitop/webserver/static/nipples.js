
['left', 'right'].forEach((position) => {
  const nippleZone = document.getElementById(position + 'NippleContainer');

  const nipple = nipplejs.create({
    zone: nippleZone,
    mode: 'static',
    size: 200,
    position: { top: 50, [position]: 50 }
  }).get();

  nipple.on('move', (evt, data) => {
    if (position === "left") {
      window.command['motor_move'](data);
    } else {
      window.command['servo_move'](data);
    }
  });

  nipple.on('end', (evt) => {
    nipple.frontPosition.x = 0;
    nipple.frontPosition.y = 0;
    if (position === "left") {
      window.command['motor_stop']();
    } else {
      window.command['servo_stop']();
    }
  });
});

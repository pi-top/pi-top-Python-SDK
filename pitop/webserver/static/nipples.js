const nippleZone = document.getElementById('leftNippleContainer');

const nipple = nipplejs.create({
  zone: nippleZone,
  mode: 'static',
  size: 200,
  position: { top: 50, left: 50 },
}).get();

nipple.on('move', (evt, data) => {
  window.command['motor_move'](data);
});

nipple.on('end', (evt) => {
  nipple.frontPosition.x = 0;
  nipple.frontPosition.y = 0;
  window.command['motor_stop']();
});

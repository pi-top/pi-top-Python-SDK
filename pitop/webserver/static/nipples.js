['left', 'right'].forEach((direction) => {
  const nippleZone = document.getElementById(direction + 'NippleContainer');

  const nipple = nipplejs.create({
    zone: nippleZone,
    mode: 'static',
    size: 200,
    position: { top: 50, [direction]: 50 },
  }).get();

  nipple.on('start move end dir plain', (evt) => {
    nipple.ui.front.style.left = 0;
    nipple.frontPosition.x = 0;
    window.command[direction + 'Motor'](nipple.frontPosition.y * -1);
  });

  nipple.on('end', (evt) => {
    nipple.ui.front.style.left = 0;
    nipple.frontPosition.x = 0;
    nipple.frontPosition.y = 0;
    window.command[direction + 'Motor'](0);
  });
});

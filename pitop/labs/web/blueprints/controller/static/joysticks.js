function sanitiseJoystickData(data) {
  const {
    force = 0,
    pressure = 0,
    distance = 0,
    angle = { radian: 0, degree: 0 },
    direction = { x: "", y: "", angle: "" },
    position = { x: 0, y: 0 },
  } = data || {};

  return {
    force,
    pressure,
    distance,
    angle,
    direction,
    position,
  };
}

["left", "right"].forEach((position) => {
  const joystickZone = document.getElementById(position + "JoystickContainer");
  if (!joystickZone) return;

  const type = `${position}_joystick`;
  const joystick = nipplejs
    .create({
      zone: joystickZone,
      mode: "static",
      size: 200,
      position: { top: 50, [position]: 50 },
    })
    .get();

  joystick.on("move", (_, data) => {
    publish({ type, data: sanitiseJoystickData(data) });
  });

  joystick.on("end", (_, data) => {
    joystick.frontPosition.x = 0;
    joystick.frontPosition.y = 0;
    publish({ type, data: sanitiseJoystickData(data) });
  });
});

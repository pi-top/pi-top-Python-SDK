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

function setupJoystick({ containerId, type } = {}) {
  const joystickZone = document.getElementById(containerId);
  if (!joystickZone) {
    return console.warn(
      `Unable to setup joystick "${type}", no element with id "${containerId}" found`
    );
  }

  const joystick = nipplejs
    .create({
      zone: joystickZone,
      mode: "static",
      size: 200,
      position: { top: 100, left: 100 },
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

  return joystick;
}

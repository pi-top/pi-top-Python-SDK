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

class Joystick extends HTMLElement {
  constructor() {
    super();
  }

  getJoystickPosition() {
    const positionTop = parseInt(this.getAttribute("positionTop"), 10);
    const positionLeft = parseInt(this.getAttribute("positionLeft"), 10);
    const positionRight = parseInt(this.getAttribute("positionRight"), 10);
    const positionBottom = parseInt(this.getAttribute("positionBottom"), 10);
    return {
      top: !Number.isNaN(positionTop) ? positionTop : 100,
      left: !Number.isNaN(positionLeft) ? positionLeft : 100,
      right: !Number.isNaN(positionRight) ? positionRight : undefined,
      bottom: !Number.isNaN(positionBottom) ? positionBottom : undefined,
    };
  }

  connectedCallback() {
    if (!this.connected) {
      this.connected = true;

      const type = this.getAttribute("type") || "joystick";
      const mode = this.getAttribute("mode") || "static";
      const position = this.getAttribute("position") || "relative";
      const size = parseInt(this.getAttribute("size"), 10) || 200;

      const style = this.getAttribute("style");
      this.setAttribute(
        "style",
        `${style}; position: ${position}; width: ${size}px; height: ${size}px`
      );

      this.joystick = nipplejs
        .create({
          zone: this,
          mode,
          size,
          position: this.getJoystickPosition(),
        })
        .get();

      this.joystick.on("move", (_, data) => {
        publish({ type, data: sanitiseJoystickData(data) });
      });

      this.joystick.on("end", (_, data) => {
        this.joystick.frontPosition.x = 0;
        this.joystick.frontPosition.y = 0;
        publish({ type, data: sanitiseJoystickData(data) });
      });
    }
  }

  disconnectedCallback() {
    this.joystick.destroy();
    this.connected = false;
  }
}

window.customElements.define("joystick-component", Joystick);

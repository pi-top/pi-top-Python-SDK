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

  connectedCallback() {
    if (!this.rendered) {
      this.rendered = true;

      const type =  this.getAttribute("type") || "joystick";
      const mode =  this.getAttribute("mode") || "static";
      const position =  this.getAttribute("position") || "relative";
      const size =  +this.getAttribute("size") || 200;
      const positionTop =  +this.getAttribute("positionTop") || 100;
      const positionLeft =  +this.getAttribute("positionLeft") || 100;
      const positionRight =  +this.getAttribute("positionRight") || undefined;
      const positionBottom =  +this.getAttribute("positionBottom") || undefined;

      const style = this.getAttribute("style");
      this.setAttribute(
        "style",
        `${style}; position: ${position}; width: ${size}px; height: ${size}px`
      );

      const joystick = nipplejs
        .create({
          zone: this,
          mode,
          size,
          position: {
            top: positionTop,
            left: positionLeft,
            right: positionRight,
            bottom: positionBottom,
          },
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
    }
  }
}

window.customElements.define("joystick-component", Joystick);

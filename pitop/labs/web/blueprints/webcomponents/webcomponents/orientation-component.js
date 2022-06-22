class DeviceOrientation extends HTMLElement {
  constructor() {
    super();
  }

  connectedCallback() {
    if (!this.connected) {
      this.connected = true;
      this.setup();
    }
  }

  disconnectedCallback() {
    this.disable();
    this.connected = false;
  }

  setup = async () => {
    this.attachShadow({mode: 'open'});
    this.wrapper = document.createElement('div');
    this.shadowRoot.append(this.wrapper);

    this.header = document.createElement('h3');
    this.header.textContent = 'Device Orientation Control';
    this.wrapper.appendChild(this.header);

    if (typeof DeviceOrientationEvent === 'undefined') {
      this.header.textContent = 'Device Orientation Not Supported On This Device!';
      return;
    }

    if (typeof DeviceOrientationEvent.requestPermission === 'function') {
      this.permissionButton = document.createElement('button');
      this.permissionButton.setAttribute('type','button');
      this.permissionButton.textContent = 'Allow sensor access';
      this.permissionButton.addEventListener('click', this.requestPermission);
      this.wrapper.appendChild(this.permissionButton);
      return;
    }

    this.showEnable();
  }

  requestPermission = async () => {
    const permissionState = await DeviceOrientationEvent.requestPermission()
    return permissionState === 'granted' ? this.permissionGranted() : this.permissionDenied();
  }

  permissionGranted = () => {
    this.showEnable();
    this.permissionButton.remove();
  }

  permissionDenied = () => {
    this.header.textContent = 'Device Orientation Permission Denied!';
  }

  showEnable = () => {
    this.enabled = document.createElement('input');
    this.enabled.setAttribute('type','checkbox');
    this.enabled.setAttribute('id','enabled');
    this.wrapper.appendChild(this.enabled);

    this.enabledLabel = document.createElement('label');
    this.enabledLabel.setAttribute('for','enabled');
    this.enabledLabel.innerText = 'Disabled';
    this.wrapper.appendChild(this.enabledLabel);

    this.enabled.addEventListener('change', (event) => {
      if (event.currentTarget.checked) {
        this.enable();
      } else {
        this.disable();
      }
    })
  }

  enable = () => {
    window.addEventListener('deviceorientation', this.handleOrientationEvent);
    // deviceorientation events don't fire when window blurs, so reset controls
    window.addEventListener('blur', this.orientationReset);

    this.showOrientationDisplay();
    this.enabledLabel.innerText = 'Enabled';
  }

  disable = () => {
    this.orientationReset();

    window.removeEventListener('deviceorientation', this.handleOrientationEvent);
    window.removeEventListener('blur', this.orientationReset);

    this.hideOrientationDisplay();
    this.enabledLabel.innerText = 'Disabled';
  }

  orientationReset = () => {
    this.handleOrientationEvent({ alpha: 0, beta: 0, gamma: 0 });
  };

  handleOrientationEvent = (event) => {
    const x = event.beta; // landscape left right
    const y = event.gamma; // landscape forward back
    const z = event.alpha; // landscape rotation

    this.updateOrientationDisplay(x, y, z);

    eval(`
     const data = ${JSON.stringify({ x, y, z })};
     ${this.getAttribute('onchange')}
    `);
  }

  showOrientationDisplay = () => {
    this.x = document.createElement('p');
    this.y = document.createElement('p');
    this.z = document.createElement('p');
    this.wrapper.appendChild(this.x);
    this.wrapper.appendChild(this.y);
    this.wrapper.appendChild(this.z);

    this.updateOrientationDisplay(0, 0, 0)
  }

  hideOrientationDisplay = () => {
    this.x.remove();
    this.y.remove();
    this.z.remove();
  }

  updateOrientationDisplay = (x, y, z) => {
    this.x.textContent = 'x: ' + x;
    this.y.textContent = 'y: ' + y;
    this.z.textContent = 'z: ' + z;
  }
}

window.customElements.define('orientation-component', DeviceOrientation);

var speed = 20;

console.log(speed)
function showSpeed() {
  const speedIndicator = document.getElementById("speed-indicator");
  console.log(speed)
  speedIndicator.style = `height:${100 - speed}%`;
}

function incrementSpeed() {
  speed = speed === 100 ? speed : speed + 20;
  showSpeed();
}

function decrementSpeed() {
  speed = speed === 0 ? speed : speed - 20;
  showSpeed();
}

document.addEventListener("keydown", function (event) {
  publish({
    type: "key_down",
    data: { key: event.key, code: event.code, keyCode: event.keyCode },
  });

  switch (event.key) {
    case "ArrowUp":
      incrementSpeed();
      break;

    case "ArrowDown":
      decrementSpeed();
      break;
  }
});

document.addEventListener("keyup", function (event) {
  publish({
    type: "key_up",
    data: { key: event.key, code: event.code, keyCode: event.keyCode },
  });
});

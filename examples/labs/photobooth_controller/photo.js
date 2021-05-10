function cameraFlash() {
  const flash = document.getElementById("flash");
  flash.classList.add("visible");
  flash.classList.add("fadeout");

  setTimeout(() => {
    flash.classList.remove("visible");
    flash.classList.remove("fadeout");
  }, 750);
}

function savePhoto() {
  const input = document.getElementById("name-input");
  publish({ type: "save_photo", data: { name: input.value } });
  cameraFlash();
}

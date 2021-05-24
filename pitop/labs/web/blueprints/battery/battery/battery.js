subscribe((message) => {
    if (message.type === 'battery_state') {
        let batteryCapacity = message.data[1];
        let batteryChargeStatus = message.data[0];
        let color = 'greenyellow';
        console.log(batteryCapacity);
        document.getElementById("batteryPercentage").innerHTML = batteryCapacity + "%";
        document.getElementById("batteryLevel").style.width = batteryCapacity + "%";
        if (parseInt(batteryCapacity) < 50) {
            color = 'orange';
        }
        if (parseInt(batteryCapacity) < 20) {
            color = 'orangered';
        }
        if (parseInt(batteryChargeStatus) === 0){
            document.getElementById("chargeIcon").style.display = 'none';
        } else {
            document.getElementById("chargeIcon").style.display = 'block';
        }
        document.getElementById("batteryLevel").style.backgroundColor = color;
    }
})

subscribe((message) => {
    if (message.type === 'battery_capacity') {
        let batteryCapacity = message.data;
        let color = 'greenyellow';
        console.log(batteryCapacity);
        document.getElementById("batteryPercentage").innerHTML = batteryCapacity + "%";
        document.getElementById("batteryLevel").style.width = batteryCapacity + "%";
        if (batteryCapacity < 20) {
            color = 'orangered';
        }
        if (batteryCapacity < 50) {
            color = 'orange';
        }
        document.getElementById("batteryLevel").style.backgroundColor = color;
    }
})

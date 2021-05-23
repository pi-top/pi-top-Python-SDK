subscribe((message) => {
    if (message.type === 'battery_capacity') {
        console.log(message.data)
    }
})

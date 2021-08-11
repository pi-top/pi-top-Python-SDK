from pitop.processing.speech import services

config = {
    "language": "us",
}

tts = services.get(service_id="FESTIVAL", **config)

tts.say("This is the festival speech service")

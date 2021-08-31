from pitop.processing import tts

config = {
    "language": "us",
}

speech = tts.services.get(service_id="FESTIVAL", **config)

speech.say("This is the festival tts service")
